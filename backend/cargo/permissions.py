from rest_framework.permissions import BasePermission

from accounts.models import Role


class AdminUploadPermission(BasePermission):
    message = 'Clearance level inadequate.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.access_level == Role.ADMIN_USER
        )
