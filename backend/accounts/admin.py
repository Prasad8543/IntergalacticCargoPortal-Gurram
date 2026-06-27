from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Role, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'mobile', 'get_access_level', 'is_active', 'date_joined')
    search_fields = ('email', 'mobile')
    ordering = ('email',)
    list_filter = ('role', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Profile', {'fields': ('mobile', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2', 'mobile', 'role')}),
    )

    @admin.display(description='Access level')
    def get_access_level(self, obj):
        return obj.access_level


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'access_level', 'seeded', 'created_at')
    search_fields = ('name', 'code')
    list_filter = ('access_level', 'seeded')
