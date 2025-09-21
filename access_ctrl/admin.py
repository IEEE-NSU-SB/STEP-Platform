from django.contrib import admin
from .models import *

# Register your models here.

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
    filter_horizontal = ("permissions",)  # Makes ManyToMany easy to edit
    search_fields = ("role__name",)

# -----------------------------
# UserPermission Admin
# -----------------------------
@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ("user",)
    filter_horizontal = ("permissions",)  # Makes ManyToMany easy to edit
    search_fields = ("user__username",)

# -----------------------------
# UserRole Admin
# -----------------------------
@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user",)
    filter_horizontal = ("roles",)  # Many roles per user
    search_fields = ("user__username",)