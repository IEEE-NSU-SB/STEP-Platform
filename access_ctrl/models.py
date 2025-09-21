from django.db import models
from django.contrib.auth.models import User

class Role(models.Model):
    """
    Defines a role in the system, e.g., 'Admin', 'Manager'.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """
    Assigns roles to a user. One user can have many roles.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_roles")
    roles = models.ManyToManyField(Role, blank=True, related_name="users_with_role")

    def __str__(self):
        return f"{self.user.username} roles"
    
class Permission(models.Model):
    """
    Atomic permission entity.
    """
    name = models.CharField(max_length=100)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.codename
    
class RolePermission(models.Model):
    """
    Permissions assigned to a role. One entry per role, multiple permissions via ManyToMany.
    """
    role = models.OneToOneField(Role, on_delete=models.CASCADE, related_name="role_permissions")
    permissions = models.ManyToManyField(Permission, blank=True, related_name="roles_with_permission")

    def __str__(self):
        return f"{self.role.name} permissions"


class UserPermission(models.Model):
    """
    Permissions assigned directly to a user. One entry per user, multiple permissions via ManyToMany.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="custom_user_permissions")
    permissions = models.ManyToManyField(Permission, blank=True, related_name="users_with_permission")

    def __str__(self):
        return f"{self.user.username} permissions"