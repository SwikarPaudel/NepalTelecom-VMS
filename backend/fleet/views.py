from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.filters import BranchFilterBackend
from core.permissions import IsBranchAdmin
from .serializers import VehicleSerializer
from .models import Vehicle

# Create your views here.
class Addnewvehicle(CreateAPIView):
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.all()

    def perform_create(self, serializer):
        """
        Intercepts creation step to attach the admin's branch context securely.
        """
        serializer.save(branch=self.request.user.profile.branch)

    def create(self, request, *args, **kwargs):
        """
        Overrides to return your custom success text message payload.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) # Automatically returns 400 JSON on error
        self.perform_create(serializer)
        
        return Response(
            {"message": "Vehicle added successfully."}, 
            status=status.HTTP_201_CREATED
        )


class VehicleListView(ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    
    # 2. Add your branch filter class to the filter_backends list
    filter_backends = [BranchFilterBackend]

    def list(self, request, *args, **kwargs):
        # 3. This line automatically calls your BranchFilterBackend.filter_queryset()
        queryset = self.filter_queryset(self.get_queryset())
        
        # 4. Handle pagination safely
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # 5. Serialize and return the filtered vehicles
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class VehicleAssignView(ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    filter_backends = [BranchFilterBackend]

    