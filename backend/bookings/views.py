from django.shortcuts import render
from rest_framework.views import APIView
from .models import Booking
from .serializers import BookingSerializer,BookingApprovalSerializer
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.permissions import IsBranchAdmin
from core.filters import BranchFilterBackend
from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet
from fleet.models import Vehicle
from django.utils.dateparse import parse_datetime
from fleet.serializers import VehicleSerializer
# Create your views here.

class NewBookingView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        """
        Overriding create allows us to provide your custom 
        success message while maintaining generic performance.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) # Automatically throws 400 Bad Request if invalid
        self.perform_create(serializer)
        
        return Response(
            {"message": "Booking successful. Awaiting system admin approval."}, 
            status=status.HTTP_201_CREATED
        )
    
class BookingApprovalView(ModelViewSet):
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    serializer_class = BookingApprovalSerializer
    filter_backends = [BranchFilterBackend]
    queryset = Booking.objects.all()
    def partial_update(self, request, *args, **kwargs):
        """
        Overriding partial_update allows us to provide your custom 
        success message while maintaining generic performance.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) # Automatically throws 400 Bad Request if invalid
        self.perform_update(serializer)
        
        return Response(
            {"message": "Booking approval status updated successfully."}, 
            status=status.HTTP_200_OK
        )
    
class BookingListView(ModelViewSet):
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    serializer_class = BookingSerializer
    filter_backends = [BranchFilterBackend]
    queryset = Booking.objects.all()


class AvailableVehicleListView(APIView):
    """
    Returns a list of vehicles that are either fully unbooked 
    or only have 'PENDING' bookings during the requested window.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        # 1. Extract query params from the URL
        start_str = request.query_params.get('start_time')
        end_str = request.query_params.get('end_time')
        requested_vehicle_choice = request.query_params.get('vehicle_choice')

        # 2. Check that parameters exist
        if not start_str or not end_str:
            return Response(
                {"error": "Please provide both start_time and end_time query parameters."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Parse date strings into Python datetime objects
        start_time = parse_datetime(start_str)
        end_time = parse_datetime(end_str)

        # 4. Validate that dates are formatted correctly and chronology is right
        if not start_time or not end_time or start_time >= end_time:
            return Response(
                {"error": "Invalid date format or start_time occurs after end_time."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 5. Query IDs of vehicles tied up in APPROVED blocks
        unavailable_ids = Booking.objects.filter(
            status=Booking.BookingStatus.APPROVED,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).values_list('vehicle_id', flat=True)

        # 6. Exclude unavailable cars (leaves free + pending cars)
        available_vehicles = Vehicle.objects.filter(approval_status=Vehicle.status.AVAILABLE).exclude(id__in=unavailable_ids)

        if requested_vehicle_choice:
            available_vehicles = available_vehicles.filter(vehicle_choice=requested_vehicle_choice)

        if request.user.is_authenticated:
            user_branch = getattr(getattr(request.user, 'profile', None), 'branch', None)
            if user_branch is not None:
                available_vehicles = available_vehicles.filter(branch=user_branch)

        # 7. Serialize and return the filtered list
        serializer = VehicleSerializer(available_vehicles, many=True)
        return Response(serializer.data)

    
