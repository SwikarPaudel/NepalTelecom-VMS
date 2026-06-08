from rest_framework import serializers
from .models import DriverProfile

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