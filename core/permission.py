from rest_framework.permissions import BasePermission

class IsAdminOrStaff(BasePermission):
    
    def has_permission(self, request, view):
        # Check if the user is authenticated and has a role of 'admin' or 'staff'
        user = request.user
        if user.is_authenticated and user.role in ['admin', 'staff']:
            return True
        return False
