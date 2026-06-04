from django.db import models
from django.contrib.auth.models import User
# from django.utils.translation import post_save
# from django.dispatch import receiver

# Create your models here.
class Profile(models.Model):

    class ROLE(models.TextChoices):
        SUPERADMIN = 'super admin', 'Super Admin'
        ADMIN = 'admin', 'Admin'
        EMPLOYEE = 'employee', 'Employee'
        DRIVER = 'driver', 'Driver'
        NOT_ASSIGNED = 'not assigned', 'Not Assigned'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE.choices, default=ROLE.NOT_ASSIGNED)
    role_approved = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=10, blank=True, null=True) 

    # FIX: Uses __in to allow multiple roles to approve profiles
    approved_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='approved_profiles',
        limit_choices_to={'role__in': [ROLE.SUPERADMIN, ROLE.ADMIN]}
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"