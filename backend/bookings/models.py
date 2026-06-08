from django.db import models
from branch.models import Branch
from driver.models import DriverProfile

# Create your models here.
class Booking(models.Model):
    _STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    

    def __str__(self):
        return f"Booking {self.id} - Driver: {self.driver.user.username} - Branch: {self.branch.name}"
