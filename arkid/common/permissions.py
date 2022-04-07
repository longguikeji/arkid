from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsTenantAdmin(BasePermission):

    def has_permission(self, request, view):
        
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated
        )