from django.contrib import admin
from .models import Booking

# Register your models here.
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle', 'start_time', 'end_time', 'status','approved_by')
    search_fields = ('user__username', 'vehicle__license_plate')
    list_filter = ['status', 'start_time', 'end_time']

admin.site.register(Booking, BookingAdmin)