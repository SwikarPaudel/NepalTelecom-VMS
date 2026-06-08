from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import DriverProfile
from .serializers import DriverProfileFirstTimeSetupSerializer
from rest_framework import mixins, viewsets
from rest_framework.exceptions import NotFound
from core.permissions import IsBranchAdmin
from core.filters import BranchFilterBackend
from core.pagination import AdminProfileTablePagination
from .serializers import AdminDriverProfileManagementSerializer


# Create your views here.

class DriverProfileSetupViewSet( mixins.RetrieveModelMixin,mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DriverProfileFirstTimeSetupSerializer
    queryset = DriverProfile.objects.all()

    def get_object(self):
        """
        Safely matches the request down to the driver profile instance 
        by hopping from User -> Profile -> DriverProfile.
        """
        user = self.request.user
        
        # 1. Step into your custom profile app model
        if not hasattr(user, 'profile'):
            raise NotFound({"detail": "Base profile registration record not found."})
        
        # 2. Step from custom profile down to this driver profile
        base_profile = user.profile
        if not hasattr(base_profile, 'driver_profile'):
            raise NotFound({
                "detail": "Driver account entry missing or admin authorization is pending."
            })
            
        return base_profile.driver_profile
    
class AdminDriverProfileManagementViewSet(ModelViewSet):
    """Admin-only viewset to view, update, list, and delete any driver profile."""
    permission_classes = [IsBranchAdmin]  # Strictly restricts to staff/admins
    filter_backends = [BranchFilterBackend]
    serializer_class = AdminDriverProfileManagementSerializer
    pagination_class = AdminProfileTablePagination

    # Optimizes DB hits by hopping from DriverProfile -> Profile -> User in a single SQL query
    queryset = DriverProfile.objects.all().select_related('user__user', 'branch')

    def update(self, request, *args, **kwargs):
        # Override update to pass the request
        kwargs['partial'] = True  # Allow partial updates (PATCH behavior on PUT)
        return super().update(request, *args, **kwargs)