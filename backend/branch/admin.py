from django.contrib import admin
from .models import Branch
# Register your models here.

class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name', 'location')

admin.site.register(Branch, BranchAdmin)