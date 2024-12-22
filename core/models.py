from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Registered_Participant(models.Model):
    name=models.CharField(null=False, blank=False, max_length=150)
    university=models.CharField(null=True, blank=True, max_length=150)
    contact_no=models.CharField(null=True, blank=True, max_length=50)
    email=models.EmailField(null=True, blank=True)
    role=models.CharField(null=True, blank=True, max_length=100)
    t_shirt_size=models.CharField(null=True, blank=True, max_length=20)
    unique_code=models.CharField(null=False, blank=False, max_length=150, unique=True)

    class Meta:
        verbose_name="Registered Participant"

    def __str__(self):
        return str(self.pk)

class Token_Session(models.Model):
    session_name=models.CharField(null=False, blank=False, max_length=20)
    is_active=models.BooleanField(null=False, blank=False, default=False)
    is_independent=models.BooleanField(null=False, blank=False, default=False)
    order_of_session=models.IntegerField(null=False,blank=False,default=0)

    class Meta:
        verbose_name="Token Session"

    def current_session():
        return Token_Session.objects.filter(is_active=True, is_independent=False)[0]

    def save(self, *args, **kwargs):
        if (self.pk):
            if(kwargs.get('is_active') == 'on' and (kwargs.get('is_independent') == 'off' or self.is_independent == False)):
                Token_Session.objects.filter(is_active=True, is_independent=False).update(is_active=False)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.pk)

class Token_Participant(models.Model):
    registered_participant=models.ForeignKey(Registered_Participant, null=False, blank=False, on_delete=models.CASCADE)
    token_session=models.ForeignKey(Token_Session, null=False, blank=False, on_delete=models.CASCADE)
    date_time=models.DateTimeField(null=False, blank=False, auto_now_add=True)

    class Meta:
        verbose_name="Applied Participant Token"

    def __self__(self) -> str:
        return str(self.pk)
    
    
class User_Permission(models.Model):
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)
    update_session = models.BooleanField(null=False, blank=False, default=False)
    scan = models.BooleanField(null=False, blank=False, default=False)
    scan_any_session = models.BooleanField(null=False, blank=False, default=False)
    
    class Meta:
        verbose_name="User Permissions"

    def __self__(self) -> str:
        return str(self.pk)