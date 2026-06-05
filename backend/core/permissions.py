from rest_framework import permissions
from accounts.models import Profile 

class IsSuperAdmin(permissions.BasePermission):
    message = 'Super admin access required.'

    def has_permission(self, request, view):
        user = request.user
        
        # 1. FIXED: Always check authentication FIRST to eliminate AnonymousUser crashes
        if not user or not user.is_authenticated:
            return False

        # 2. Safely authorize master command-line superusers
        if user.is_superuser:
            return True

        # 3. Fall back to checking your custom Profile tables
        profile = getattr(user, 'profile', None)
        return (
            profile is not None
            and getattr(profile, 'role', None) == Profile.ROLE.SUPERADMIN
            and getattr(profile, 'role_approved', False)
        )
    
class IsBranchAdmin(permissions.BasePermission):
    message = 'Branch admin access required.'

    def has_permission(self, request, view):
        user = request.user
        
        # 1. Always check authentication FIRST to eliminate AnonymousUser crashes
        if not user or not user.is_authenticated:
            return False

        # 2. Safely authorize master command-line superusers
        if user.is_superuser:
            return True

        # 3. Fall back to checking your custom Profile tables
        profile = getattr(user, 'profile', None)
        return (
            profile is not None
            and getattr(profile, 'role', None) == Profile.ROLE.ADMIN
            and getattr(profile, 'role_approved', False)
        )