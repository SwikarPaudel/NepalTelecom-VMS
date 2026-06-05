from rest_framework import serializers
from .models import Profile
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.exceptions import ValidationError

class AdminUserProfileManagementSerializer(serializers.ModelSerializer):
    # CRITICAL FIX: Removed source='user.xxx' so DRF doesn't wrap them into a read-only 'user' dictionary
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(allow_blank=True, required=False)
    last_name = serializers.CharField(allow_blank=True, required=False)
    approved_by_name = serializers.ReadOnlyField(source='approved_by.user.username')

    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'username', 'email', 'first_name', 'last_name', 
            'role', 'role_approved', 'phone_number', 'branch', 
            'approved_by', 'approved_by_name'
        ]
        # Keep 'user' read-only so the profile link itself cannot be changed
        read_only_fields = ['id', 'user', 'approved_by']

    def to_representation(self, instance):
        """
        Forces the serializer to pull and inject user account details 
        into the read-only GET data output.
        """
        # Get the standard serialized representation dictionary
        representation = super().to_representation(instance)
        
        # Pull details from the related user object securely if it exists
        if instance.user:
            representation['username'] = instance.user.username
            representation['email'] = instance.user.email
            representation['first_name'] = instance.user.first_name
            representation['last_name'] = instance.user.last_name
            
        return representation

    def validate(self, data):
        """Prevents duplicate usernames or emails using flat data dictionary."""
        current_user = self.instance.user if self.instance else None

        # Check flat username values directly
        if 'username' in data:
            username = data['username']
            if User.objects.filter(username=username).exclude(id=current_user.id if current_user else None).exists():
                raise ValidationError({'username': 'This username is already taken.'})

        if 'email' in data:
            email = data['email']
            if User.objects.filter(email=email).exclude(id=current_user.id if current_user else None).exists():
                raise ValidationError({'email': 'This email is already taken.'})
        return data

    def create(self, validated_data):
        """Handles admin-side creation extracting flat fields."""
        # Pop out user account variables cleanly
        username = validated_data.pop('username', None)
        email = validated_data.pop('email', None)
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')

        if not username or not email:
            raise serializers.ValidationError({"detail": "Username and email fields are required."})

        request = self.context.get('request')

        with transaction.atomic():
            random_password = User.objects.make_random_password()
            user_instance = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=random_password
            )

            if validated_data.get('role_approved') is True and request and request.user:
                validated_data['approved_by'] = getattr(request.user, 'profile', None)

            profile_instance = Profile.objects.create(user=user_instance, **validated_data)
            
        return profile_instance

    def update(self, instance, validated_data):
        """Handles partial updates safely without losing relation targets."""
        # Pop user account variables safely from flat dictionary
        username = validated_data.pop('username', None)
        email = validated_data.pop('email', None)
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)
        
        user_instance = instance.user

        with transaction.atomic():
            # Update only fields that were actually passed in the request
            if username is not None: user_instance.username = username
            if email is not None: user_instance.email = email
            if first_name is not None: user_instance.first_name = first_name
            if last_name is not None: user_instance.last_name = last_name
            user_instance.save()
            
            # Dynamic approvals tracking
            request = self.context.get('request')
            if validated_data.get('role_approved') is True and not instance.role_approved:
                if request and request.user:
                    validated_data['approved_by'] = getattr(request.user, 'profile', None)

            # Let parent update standard profile model fields
            instance = super().update(instance, validated_data)
            
        return instance
    