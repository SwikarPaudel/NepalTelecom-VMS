from django.contrib import admin
from .models import Profile
# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'role_approved', 'phone_number', 'approved_by')
    list_filter = ('role', 'role_approved')
    search_fields = ('user__username', 'user__email', 'phone_number')

admin.site.register(Profile, ProfileAdmin)