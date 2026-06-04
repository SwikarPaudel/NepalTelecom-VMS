from rest_framework import serializers
from .models import Profile
from django.contrib.auth.models import User
from django.db import transaction

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)

    #Capture custom profile details
    requested_role = serializers.ChoiceField(choices=Profile.ROLE.choices,default=Profile.ROLE.NOT_ASSIGNED, required=True)
    phone_number = serializers.CharField(max_length=10, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'requested_role', 'phone_number']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value
    
    def create(self, validated_data):
         # Extract profile fields so they aren't passed to the core User model
        requested_role = validated_data.pop('requested_role', Profile.ROLE.NOT_ASSIGNED)
        phone_number = validated_data.pop('phone_number')

        # Use an atomic transaction block so if either step fails, everything rolls back safely
        with transaction.atomic():
            # 1. Create and hash password for the core Django User.
            # This line will IMMEDIATELY fire your post_save signal and create a blank profile.
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', '')
            )
            
            # 2. MODIFY: Instead of .create(), update the profile already built by the signal.
            # This protects your database from unique constraint conflicts.
            Profile.objects.filter(user=user).update(
                phone_number=phone_number,
                role=requested_role,
                role_approved=False
            )
            
        return user
class userProfileSerializer(serializers.ModelSerializer):
    username=serializers.ReadOnlyField(source='user.username')
    approved_by=serializers.ReadOnlyField(source='approved_by.user.username')
    class Meta:
        model = Profile
        fields = ['user','username', 'role', 'role_approved', 'phone_number', 'branch', 'approved_by']


class UserProfileDetailSerializer(serializers.ModelSerializer):
    # Dotted source fields mapped from the related User model
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.EmailField(source='user.email',allow_blank=True, required=False)
    first_name = serializers.CharField(source='user.first_name', allow_blank=True, required=False)
    last_name = serializers.CharField(source='user.last_name', allow_blank=True, required=False)
    approved_by = serializers.ReadOnlyField(source='approved_by.user.username')

    class Meta:
        model = Profile
        fields = ['user', 'username', 'email', 'first_name', 'last_name', 'role', 'role_approved', 'phone_number', 'branch', 'approved_by']
        
        # Security: Prevent standard users from escalating privileges or changing groups
        read_only_fields = ['user', 'role', 'role_approved', 'branch', 'approved_by']

    def update(self, instance, validated_data):
        # 1. DRF automatically nests 'first_name', 'last_name', and 'email' 
        # inside a 'user' dictionary key because of their 'user.field' sources.
        user_data = validated_data.pop('user', None)
        
        # 2. Wrap operations inside an atomic block to prevent partial database corruption
        with transaction.atomic():
            if user_data:
                user_instance = instance.user
                # Update User fields if they were explicitly provided in the payload
                if 'email' in user_data:
                    user_instance.email = user_data['email']
                if 'first_name' in user_data:
                    user_instance.first_name = user_data['first_name']
                if 'last_name' in user_data:
                    user_instance.last_name = user_data['last_name']
                user_instance.save()
            
            # 3. Save standard profile table attributes (like phone_number)
            instance = super().update(instance, validated_data)
            
        return instance
