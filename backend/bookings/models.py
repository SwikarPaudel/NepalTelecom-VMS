from django.db import models
from branch.models import Branch
from driver.models import DriverProfile
from accounts.models import User
from fleet.models import Vehicle
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist

# Create your models here.
class Booking(models.Model):
    
    class BookingStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        ONGOING = 'ongoing', 'Ongoing'
        COMPLETED = 'completed', 'Completed'
        REJECTED = 'rejected', 'Rejected'

    vehicle = models.ForeignKey('fleet.Vehicle', on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_bookings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    purpose = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.PENDING)
    created_at=models.DateTimeField(auto_now_add=True)
    start_location = models.CharField(max_length=255, blank=True, null=True)    
    end_location = models.CharField(max_length=255, blank=True, null=True)
    branch = models.ForeignKey('branch.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='booking_branch')
    
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_bookings',
        limit_choices_to={'profile__role':['ADMIN', 'SUPERADMIN'],'profile__role_approved': True} # Traverses to UserProfile model
    )

    assigned_vehicle = models.ForeignKey(
        'fleet.Vehicle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_bookings'
    )

    assigned_driver = models.ForeignKey(
        'driver.DriverProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_bookings'
    )

    def __str__(self):
        vehicle_label = self.vehicle if self.vehicle is not None else 'Unassigned vehicle'
        return f"Booking {self.id} - {vehicle_label} by {self.user}"
    
    def is_available_during(self, start_time, end_time, exclude_dispatch_id=None):
        """
        Checks the Dispatches table to see if this driver has any overlapping, 
        approved bookings during the requested timeframe.
        """
        if self.vehicle is None:
            return False
        # Avoid circular imports by importing the Dispatches model from driver app
        from driver.models import Dispatches

        # Build a query to check for overlapping intervals for the same vehicle
        overlapping_dispatches = Dispatches.objects.filter(
            vehicle=self.vehicle,
            booking__status='approved',  # Only check finalized, active bookings
            booking__start_time__lt=end_time,  # Starts before requested end
            booking__end_time__gt=start_time   # Ends after requested start
        )

        # If we are updating an existing dispatch record, ignore itself
        if exclude_dispatch_id:
            overlapping_dispatches = overlapping_dispatches.exclude(id=exclude_dispatch_id)

        # Returns True if no overlapping trips are found (i.e. vehicle available)
        return not overlapping_dispatches.exists()
    
    def clean(self):
        """
        Validate that the booking's user belongs to the same branch as the vehicle.
        Uses `user.profile.branch` since the branch is stored on the UserProfile.
        """
        errors = {}

        user_branch = None
        try:
            user_branch = self.user.profile.branch
        except (AttributeError, ObjectDoesNotExist):
            user_branch = None

        vehicle_branch = getattr(self.vehicle, 'branch', None) if self.vehicle is not None else None

        if user_branch is None:
            errors['user'] = 'User must have an assigned branch before booking a vehicle.'

        if self.vehicle is not None:
            if vehicle_branch is None:
                errors['vehicle'] = 'Vehicle must be assigned to a branch before booking.'

            if user_branch is not None and vehicle_branch is not None and user_branch != vehicle_branch:
                errors['vehicle'] = 'User can book vehicles only from their assigned branch.'

        if errors:
            raise ValidationError(errors)