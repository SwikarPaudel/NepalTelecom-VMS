from django.contrib import admin
from django.urls import path
from .views import RegisterUserView, UserProfileViewSet,UserProfileDetailView,AdminProfileManagementViewSet

urlpatterns = [
    path('newregistration/', RegisterUserView.as_view(), name='new_registration'),
    path('userprofileslist/', UserProfileViewSet.as_view({'get': 'list'}), name='user-profiles'),
    path('userdetails/', UserProfileDetailView.as_view({'get': 'retrieve','patch': 'partial_update','put': 'update' }),name='user-profile-detail'),
    path('admin/manageprofiles/<int:pk>/', AdminProfileManagementViewSet.as_view({'get': 'list','put': 'update','patch': 'partial_update' }), name='admin-manage-profiles'),
]