from django.contrib import admin
from django.urls import path,include
from .views import AdminDriverProfileManagementViewSet, DriverProfileSetupViewSet

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
    })),]