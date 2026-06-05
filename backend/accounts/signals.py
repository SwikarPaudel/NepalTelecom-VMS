from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile
from django.contrib.auth.models import User
# # from driver.models import DriverProfile as Driver



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Signal to automatically create a Profile instance whenever a new User is created."""
    if created:
        default_role = Profile.ROLE.SUPERADMIN if instance.is_superuser else Profile.ROLE.NOT_ASSIGNED
        
        Profile.objects.get_or_create(
            user=instance,
            defaults={
                'role': default_role,
                'role_approved': instance.is_superuser 
            }
        )

# @receiver(post_save, sender=Profile)
# def sync_driver_profile(sender, instance, created, **kwargs):
#     """Signal to create or delete a DriverProfile based on the Profile's role and approval status."""
    
#     if instance.role == Profile.ROLE.DRIVER and instance.role_approved:
#         print("-> Condition MET: Creating/Getting Driver row.")
#         Driver.objects.get_or_create(user=instance)
#     else:
#         print("-> Condition FAILED: Deleting Driver row if it exists.")
#         Driver.objects.filter(user=instance).delete()