from django.contrib import admin
from django.urls import path,include
from .views import AdminDriverProfileManagementViewSet, DriverProfileSetupViewSet,DriverVehicleInfoViewSet,DispatchViewSet,DriverDispatchView

urlpatterns = [
     path('update/', DriverProfileSetupViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update'
    }), name='driver-profile-update'),
    path('admin/<int:pk>/', AdminDriverProfileManagementViewSet.as_view({
        'get': 'list',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    })),
    
    path('vehicleinfo/', DriverVehicleInfoViewSet.as_view({'get':'retrieve'}), name='driver-vehicle-info'),
    path('admindispatchlist/', DispatchViewSet.as_view({'get':'list'}), name='dispatches'),
    path('mydispatchinfo/', DriverDispatchView.as_view({'get':'list'}), name='driver-dispatches'),]