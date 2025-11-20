from rest_framework.permissions import BasePermission

class IsNotStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and not request.user.is_staff
    
class IsStaffORSuperUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_staff or user.is_superuser 