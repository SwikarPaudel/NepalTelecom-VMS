from django.contrib import admin
from .models import Vehicle, VehicleInfo
# Register your models here.

class VehicleAdmin(admin.ModelAdmin):
    list_display = ('manufacturer', 'model', 'year', 'license_plate', 'approval_status', 'created_at')
    search_fields = ('manufacturer', 'model', 'license_plate')
    list_filter = ['approval_status']


class VehicleInfoAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'engine_type', 'mileage', 'kilometers_driven', 'last_fuel_date', 'last_service_date')
    search_fields = ('vehicle__manufacturer', 'vehicle__model', 'vehicle__license_plate')
    list_filter = ['engine_type']

admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(VehicleInfo, VehicleInfoAdmin)
