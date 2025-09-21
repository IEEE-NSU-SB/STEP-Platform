from django import template
from access_ctrl.utils import Site_Permissions

register = template.Library()

@register.filter
def has_perm(user, codename):
    return Site_Permissions.user_has_permission(user, codename)