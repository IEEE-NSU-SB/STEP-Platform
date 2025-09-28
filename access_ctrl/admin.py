from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.

class CustomUserAdmin(BaseUserAdmin):
    # Remove 'groups' and 'user_permissions' from the fieldsets
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Status', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
    )

    # Remove them from add_fieldsets too (user creation form)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    # Hide columns in the list display if you don’t want them there
    def get_fieldsets(self, request, obj=None):
        return super().get_fieldsets(request, obj)

# Unregister the original UserAdmin
admin.site.unregister(User)
# Register our custom one
admin.site.register(User, CustomUserAdmin)

# -----------------------------
# Permission Admin
# -----------------------------
@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("name", "codename", "description")
    search_fields = ("name", "codename")
    ordering = ("codename",)

# -----------------------------
# Role Admin
# -----------------------------
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    ordering = ("name",)

# -----------------------------
# RolePermission Admin
# -----------------------------
@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("role",)
    filter_horizontal = ("permissions",)
    search_fields = ("role__name",)

# -----------------------------
# UserPermission Admin
# -----------------------------
@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ("user",)
    filter_horizontal = ("permissions",)
    search_fields = ("user__username",)

# -----------------------------
# UserRole Admin
# -----------------------------
@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user",)
    filter_horizontal = ("roles",)  # Many roles per user
    search_fields = ("user__username",)