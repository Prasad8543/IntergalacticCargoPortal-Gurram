from rest_framework import permissions

from .models import Role


class AdminUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.access_level == Role.ADMIN_USER


class StandardUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.access_level == Role.ADMIN_USER:
            return True
        user_id = view.kwargs.get('pk')
        return user_id and request.user.id == int(user_id)
