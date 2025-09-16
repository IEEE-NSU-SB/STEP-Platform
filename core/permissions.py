
from core.models import User_Permission
from django.contrib.auth.models import User


class Site_Permissions:
        
    def get_user_permissions(request):
        '''Returns all permissions from the `user_permissions` model.'''

        username = request.user.username
        try:
            user = User.objects.get(username=username)
            user_permissions = User_Permission.objects.get(user=user)
        
            return user_permissions
        except:
            return None
        
    def is_admin(request):
        '''Returns True if the user is an admin.'''
        
        username = request.user.username
        user = User.objects.get(username=username)
        
        if user.is_staff or user.is_superuser:
            return True
        else:
            return False
        
    def is_superuser(request):
        '''Returns True if the user is a superuser.'''
        
        username = request.user.username
        user = User.objects.get(username=username)
        
        if user.is_superuser:
            return True
        else:
            return False