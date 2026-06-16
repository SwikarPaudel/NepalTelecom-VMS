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

    
    # def __str__(self):
    #     # Optimized to avoid double-join database hits if Profile holds identifying strings
    #     return f"Driver: {self.user_id} -{self.user.username} {self.driver_status}"
    def __str__(self):
        # 1. Access the underlying Django User model through the Profile relationship
        if self.user and hasattr(self.user, 'user'):
            django_user = self.user.user
            full_name = f"{django_user.first_name} {django_user.last_name}".strip()
            # Use full name if available; otherwise fall back to username
            driver_name = full_name if full_name else django_user.username
        elif self.user and hasattr(self.user, 'username'):
            # Fallback if username directly exists on the object
            driver_name = self.user.username
        else:
            # Absolute fallback to ID to prevent the admin panel from crashing
            driver_name = f"ID {self.user_id}"

        # 2. Return the clean string with your current status formatting
        return f"Driver: {driver_name} - {self.driver_status}"


class Dispatches(models.Model):

    class DispatchStatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
    dispatch_status = models.CharField(max_length=20, choices=DispatchStatusChoices.choices, default=DispatchStatusChoices.PENDING)
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE, related_name='dispatches',null=True, blank=True)
    vehicle = models.ForeignKey('fleet.Vehicle', on_delete=models.CASCADE)
    booking=models.ForeignKey('bookings.Booking', on_delete=models.CASCADE)


    def save(self, *args, **kwargs):
       if self.dispatch_status == self.DispatchStatusChoices.COMPLETED or self.dispatch_status == self.DispatchStatusChoices.CANCELLED:
            if self.pk:
                self.delete()
            return
       super().save(*args, **kwargs)

#Need modification to delete the dispatch when the status is completed or cancelled