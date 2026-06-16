from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Dispatches, DriverProfile
from .serializers import DispatchSerializers, DriverProfileFirstTimeSetupSerializer
from rest_framework import mixins, viewsets
from rest_framework.exceptions import NotFound
from core.permissions import IsBranchAdmin,IsDriver
from core.filters import BranchFilterBackend
from core.pagination import AdminProfileTablePagination
from fleet.models import Vehicle
from .serializers import AdminDriverProfileManagementSerializer, DriverVehicleInfoSerializer


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
    

class DriverVehicleInfoViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsDriver]
    serializer_class = DriverVehicleInfoSerializer

    def get_queryset(self):
        """
        Filters the vehicles to only return the one assigned 
        to the currently authenticated driver.
        """
        # Assumes your DriverProfile model has a OneToOne relationship with Django's User model
        return Vehicle.objects.filter(current_driver__id=self.request.user.profile.driver_profile.id)

    def retrieve(self, request, *args, **kwargs):
        """
        Intercepts requests matching /vehicleinfo/<id>/ 
        and always returns the logged-in driver's actual vehicle.
        """
        vehicle = self.get_queryset().first()
        
        if not vehicle:
            return Response(
                {"detail": "No vehicle assigned to your profile."}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = self.get_serializer(vehicle)
        return Response(serializer.data)
    
class DispatchViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    serializer_class = DispatchSerializers
    queryset = Dispatches.objects.all().select_related('driver__user__user', 'vehicle', 'booking__user')

class DriverDispatchView(ModelViewSet):
    permission_classes = [IsAuthenticated, IsDriver]
    serializer_class = DispatchSerializers

    def get_queryset(self):
        """
        Filters dispatches to only those assigned to the currently authenticated driver.
        """
        if not Dispatches.objects.filter(driver__id=self.request.user.profile.driver_profile.id).exists():
            
            return Dispatches.objects.none() 
        else:
            return Dispatches.objects.filter(driver__id=self.request.user.profile.driver_profile.id).select_related('driver__user__user', 'vehicle', 'booking__user')
        

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        if not queryset.exists():
            return Response(
                {"detail": "No dispatches found for your profile."}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)