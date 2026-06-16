from rest_framework import serializers
from .models import Dispatches, DriverProfile
from fleet.models import Vehicle

class DriverProfileFirstTimeSetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        # Only expose fields the driver needs to fill out the first time
        fields = ['license_number', 'license_image', 'address']

    def validate(self, attrs):
        # 'self.instance' refers to the DriverProfile fetched by get_object()
        if self.instance and self.instance.license_number:
            raise serializers.ValidationError(
                {"detail": "Your profile information has already been submitted and locked."}
            )
        return attrs
    
    def to_representation(self, instance):
        """
        Dynamically handles the GET output response.
        If data is empty, it returns null values. If filled, it shows them.
        """
        representation = super().to_representation(instance)
        
        # Include extra status tracking fields so the frontend knows it's locked
        representation['is_locked'] = bool(instance.license_number)
        representation['driver_status'] = instance.driver_status
        
        # Include branch details if assigned
        representation['branch_id'] = instance.branch_id if instance.branch else None
        representation['branch_name'] = instance.branch.name if instance.branch else None
        return representation
    

class AdminDriverProfileManagementSerializer(serializers.ModelSerializer):
    # CRITICAL CHANGE: Explicitly set read_only=True on user account data
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    phone_number = serializers.CharField(read_only=True)

    class Meta:
        model = DriverProfile
        # Fields exposed to the admin panel dashboard grid layout
        fields = [
            'id', 'user', 'username', 'email', 'phone_number',
            'license_number', 'license_image', 'address', 
            'driver_status', 'branch'
        ]
        # Protect internal primary keys and profile links from being altered
        read_only_fields = ['id', 'user']

    def to_representation(self, instance):
        """
        Gathers profile metrics to securely display user data on the dashboard 
        without opening them up to modifications during save operations.
        """
        representation = super().to_representation(instance)
        
        # Pull read-only informational blocks from: DriverProfile -> Profile -> User
        if instance.user:
            base_profile = instance.user
            representation['phone_number'] = base_profile.phone_number
            
            if base_profile.user:
                representation['username'] = base_profile.user.username
                representation['email'] = base_profile.user.email
                
        return representation

    def update(self, instance, validated_data):
        """
        Guaranteed to only write parameters bound to the DriverProfile model table.
        """
        # Purge account relations out of the payload if passed by accident
        validated_data.pop('user', None)
        
        # This super call now exclusively updates address, license info, status, or branch
        return super().update(instance, validated_data)


class DriverVehicleInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model=Vehicle
        fields=['manufacturer','model','year','license_plate','approval_status','current_driver']
        read_only_fields=['manufacturer','model','year','license_plate','approval_status','current_driver']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

       
        representation['current_driver'] = instance.current_driver.user.user.username if instance.current_driver else None

        return representation


class DispatchSerializers(serializers.ModelSerializer):
    driver_name = serializers.ReadOnlyField(source='driver.user.user.username')
    driver_status = serializers.ReadOnlyField(source='driver.driver_status')
    vehicle_manufacturer = serializers.ReadOnlyField(source='vehicle.manufacturer')
    vehicle_model = serializers.ReadOnlyField(source='vehicle.model')
    vehicle_license_plate = serializers.ReadOnlyField(source='vehicle.license_plate')
    booking_start_time = serializers.ReadOnlyField(source='booking.start_time')
    booking_end_time = serializers.ReadOnlyField(source='booking.end_time')
    booking_purpose = serializers.ReadOnlyField(source='booking.purpose')
    booking_user = serializers.ReadOnlyField(source='booking.user.username')
    booking_status = serializers.ReadOnlyField(source='booking.status')

    class Meta:
        model = Dispatches
        # Combined all fields so it handles both manual writes and descriptive reads
        fields = [
            'id', 'booking', 'booking_user', 'booking_purpose',
            'booking_status', 'driver', 'driver_name', 'driver_status',
            'vehicle', 'vehicle_manufacturer', 'vehicle_model', 'vehicle_license_plate',
            'booking_start_time', 'booking_end_time'
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        # 1. During a PATCH/partial update request, fields might be missing from attrs.
        # Fall back to the existing instance values if they aren't part of the incoming request body.
        driver = attrs.get('driver', getattr(self.instance, 'driver', None))
        booking = attrs.get('booking', getattr(self.instance, 'booking', None))
        
        # 2. Extract active row ID if executing an update tracking transaction
        dispatch_id = self.instance.id if self.instance else None

        if driver and booking:
            driver_branch = getattr(driver, 'branch', None) or getattr(getattr(driver, 'user', None), 'branch', None)
            booking_branch = getattr(getattr(booking, 'vehicle', None), 'branch', None) or getattr(getattr(getattr(booking, 'user', None), 'profile', None), 'branch', None)

            if driver_branch is not None and booking_branch is not None and driver_branch != booking_branch:
                raise serializers.ValidationError({
                    "driver": "This driver must belong to the same branch as the booking vehicle."
                })

            # 3. Trigger the interval math logic check on the model layer
            if not driver.is_available_during(booking.start_time, booking.end_time, exclude_dispatch_id=dispatch_id):
                raise serializers.ValidationError({
                    "driver": "This driver is already assigned to another approved trip during this schedule timeframe."
                })
                
        return attrs