from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class Vehicle(models.Model):

    class status(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        IN_USE = 'IN_USE', 'In Use'
        MAINTENANCE = 'MAINTENANCE', 'Under Maintenance'
        DECOMMISSIONED = 'DECOMMISSIONED', 'Decommissioned'
    manufacturer = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    license_plate = models.CharField(max_length=20, unique=True)
    approval_status = models.CharField(max_length=20, choices=status.choices, default=status.AVAILABLE)
    created_at = models.DateTimeField(auto_now_add=True)
    branch = models.ForeignKey('branch.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    current_driver =models.OneToOneField('driver.DriverProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='AssignedVehicle')

    def clean(self):
            """
            Enforce branch cross-contamination security constraints.
            """
            super().clean()
            
            # If a driver is assigned, verify they belong to the exact same branch as the vehicle
            if self.current_driver and self.branch:
                if self.current_driver.branch_id != self.branch_id:
                    raise ValidationError({
                        'current_driver': f"Cannot assign driver from branch '{self.current_driver.branch}'. "
                                        f"This vehicle belongs to branch '{self.branch}'."
                })

    def save(self, *args, **kwargs):
        """
        Force full model validation check to execute automatically on save calls.
        """
        self.full_clean()  # This triggers the clean() method written above
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.manufacturer} {self.model} ({self.license_plate})"
    
class VehicleInfo(models.Model):
    class EngineType(models.TextChoices):
        PETROL = 'PETROL', 'Petrol'
        DIESEL = 'DIESEL', 'Diesel'
        ELECTRIC = 'ELECTRIC', 'Electric'
        HYBRID = 'HYBRID', 'Hybrid'

    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name='info')
    engine_type = models.CharField(max_length=20, choices=EngineType.choices, blank=True, null=True)
    mileage = models.PositiveIntegerField(blank=True, null=True)
    kilometers_driven = models.PositiveIntegerField(blank=True, null=True)
    last_fuel_date = models.DateField(blank=True, null=True)
    last_service_date = models.DateField(blank=True, null=True)