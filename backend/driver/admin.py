from django.contrib import admin
from .models import Dispatches, DriverProfile
# Register your models here.


class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'driver_status', 'branch')
    search_fields = ('user__user__username', 'license_number')
    list_filter = ['driver_status', 'branch']

admin.site.register(DriverProfile, DriverProfileAdmin)

class DispatchesAdmin(admin.ModelAdmin):
    list_display = ('driver', 'vehicle', 'booking')
    search_fields = ('driver__user__user__username', 'vehicle__license_plate', 'booking__id')
    list_filter = ['driver', 'vehicle']

admin.site.register(Dispatches, DispatchesAdmin)