from django.urls import path
from .views import AvailableVehicleListView, NewBookingView,BookingApprovalView,BookingListView

urlpatterns = [
    path('new/', NewBookingView.as_view(), name='new-booking'),
    path('list/', BookingListView.as_view({'get': 'list'}), name='booking-list'),
    path('list/<int:pk>/', BookingApprovalView.as_view({'get': 'retrieve','patch': 'partial_update','put': 'update'}), name='booking-approval-update'),
    path('available-vehicles/', AvailableVehicleListView.as_view(), name='available-vehicles'),
]