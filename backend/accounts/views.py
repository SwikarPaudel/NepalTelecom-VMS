from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from .serializers import UserProfileDetailSerializer, UserRegistrationSerializer, userProfileSerializer
from rest_framework.permissions import AllowAny, IsAdminUser,IsAuthenticated
from rest_framework.views import APIView, Response, status
from .models import Profile
from core.permissions import IsSuperAdmin,IsBranchAdmin
from core.filters import BranchFilterBackend
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import NotFound
from .adminserializer import AdminUserProfileManagementSerializer 
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import CreateAPIView

class RegisterUserView(CreateAPIView):
    """API view to handle user registration requests."""
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        """
        Overriding create allows us to provide your custom 
        success message while maintaining generic performance.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) # Automatically throws 400 Bad Request if invalid
        self.perform_create(serializer)
        
        return Response(
            {"message": "Registration successful. Awaiting system admin role approval."}, 
            status=status.HTTP_201_CREATED
        )
    
class UserProfileViewSet(ModelViewSet):
    """API viewset to handle user profile operations."""
    permission_classes = [IsAuthenticated,]  
    filter_backends = [BranchFilterBackend]
    queryset = Profile.objects.all()
    serializer_class = userProfileSerializer

class UserProfileViewSet(ModelViewSet):
    """API viewset to handle user profile operations."""
    permission_classes = [IsAuthenticated,]  
    filter_backends = [BranchFilterBackend]
    queryset = Profile.objects.all()
    serializer_class = userProfileSerializer


class LoginView(APIView):
    """API view to handle user login requests."""
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticate against Django's user database
        user = authenticate(username=username, password=password)

        if user is None:
            # Return error if authentication fails
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        profile = getattr(user, 'profile', None)
        role = getattr(profile, 'role', None)
        is_approved = getattr(profile, 'role_approved', False)
        branch = getattr(profile, 'branch', None)

        # Generate JWT tokens if credentials are correct
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'Role': role,
            'is approved': is_approved,
            'branch': branch.id if branch is not None else None,
            'branch_name': branch.name if branch is not None else None,
        }, status=status.HTTP_200_OK)

class UserProfileDetailView(ModelViewSet):
    """API view to retrieve the authenticated user's profile details."""
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.all()
    serializer_class = UserProfileDetailSerializer

    def get_object(self):
        # Fetch the profile linked to the logged-in user
        profile = getattr(self.request.user, 'profile', None)
        
        # If the user profile record does not exist in the DB, raise a clean 404
        if profile is None:
            raise NotFound(detail="Profile not found for this user account.")
            
        return profile
    
class AdminProfileManagementViewSet(ModelViewSet):
    """Admin-only viewset to view, update, list, and delete any user profile."""
    permission_classes = [IsBranchAdmin] # Strictly restricts to staff/admins
    queryset = Profile.objects.all().select_related('user', 'approved_by__user')
    filter_backends = [BranchFilterBackend]
    serializer_class = AdminUserProfileManagementSerializer
    pagination_class = AdminProfileTablePagination

    queryset = Profile.objects.all().select_related('user', 'approved_by__user')

    def update(self, request, *args, **kwargs):
        # Override update to pass the request
        kwargs['partial'] = True  # Allow partial updates
        return super().update(request, *args, **kwargs)