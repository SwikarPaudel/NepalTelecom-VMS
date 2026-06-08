from django.contrib import admin
from .models import DriverProfile
# Register your models here.


class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'driver_status', 'branch')
    search_fields = ('user__user__username', 'license_number')
    list_filter = ['driver_status', 'branch']

admin.site.register(DriverProfile, DriverProfileAdmin)