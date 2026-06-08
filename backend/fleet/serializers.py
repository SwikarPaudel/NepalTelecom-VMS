import re
from rest_framework import serializers
from .models import Vehicle
from driver.models import DriverProfile


class VehicleSerializer(serializers.ModelSerializer):
    vehicle_type = serializers.ReadOnlyField(source='vehicle_choice')
    branch=serializers.PrimaryKeyRelatedField(read_only=True)
  

    class Meta:
        model = Vehicle
        fields = ('id', 'manufacturer', 'model', 'year', 'license_plate', 'approval_status', 'vehicle_type', 'branch','current_driver')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Extract the request from context to see who is logged in
        request = self.context.get('request')
        if request and hasattr(request.user, 'profile') and request.user.profile.branch:
            admin_branch = request.user.profile.branch
            
            # Dynamically filter the dropdown to show ONLY available drivers inside the admin's branch
            self.fields['current_driver'].queryset = DriverProfile.objects.filter(
                driver_status=DriverProfile.DriverStatusChoices.AVAILABLE,
                branch=admin_branch
            )

    def validate_license_plate(self, value):
        # 1. Strip whitespace from edges and convert to uppercase
        cleaned_value = value.strip().upper()
        
        # 2. Collapse multiple spaces inside the string down to a single space
        cleaned_value = re.sub(r'\s+', ' ', cleaned_value)
        
        # 3. Return the normalized text
        return cleaned_value
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Pull details from the related user object securely if it exists
        if instance.current_driver:
            representation['current_driver'] = instance.current_driver.user.user.username if instance.current_driver else None
            
        return representation
        
    
class VehicleListUpdateSerializer(serializers.ModelSerializer):

    current_driver = serializers.PrimaryKeyRelatedField(source='current_driver.name', read_only=True)
    class Meta:
        model = Vehicle
        fields = ('id', 'manufacturer', 'model', 'year', 'license_plate', 'approval_status', 'branch', 'current_driver')

class AssignDriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ('id', 'current_driver')

    #assign drivers by admin is left
    