from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import Profile

# Create your models here.

class DriverProfile(models.Model):

    class DriverStatusChoices(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        UNAVAILABLE = 'UNAVAILABLE', 'Unavailable'
        ON_TRIP = 'ON_TRIP', 'On Trip'
        
    user = models.OneToOneField('accounts.Profile', on_delete=models.CASCADE, related_name='driver_profile')
    license_number = models.CharField(max_length=20, unique=True)
    license_image = models.ImageField(upload_to='driver_licenses/')
    address = models.TextField()
    driver_status = models.CharField(max_length=20, choices=DriverStatusChoices.choices, default=DriverStatusChoices.AVAILABLE)
    branch = models.ForeignKey('branch.Branch', on_delete=models.SET_NULL, null=True, blank=True)

    
    def __str__(self):
        # Optimized to avoid double-join database hits if Profile holds identifying strings
        return f"Driver: {self.user_id} - {self.driver_status}"


# class Dispatches(models.Model):
#     driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE, related_name='dispatches')
#     vehicle = models.ForeignKey('fleet.Vehicle', on_delete=models.CASCADE)
#     booking=models.ForeignKey('bookings.Booking', on_delete=models.CASCADE)