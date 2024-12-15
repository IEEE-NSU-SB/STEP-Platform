from django.db import models

# Create your models here.
class Registered_User(models.Model):
    university_id=models.CharField(null=False, blank=False, max_length=20)
    name=models.CharField(null=False, blank=False, max_length=150)
    university=models.CharField(null=False, blank=False, max_length=150)
    unique_code=models.CharField(null=False, blank=False, max_length=150)

    class Meta:
        verbose_name="Registered User"

    def __self__(self) -> str:
        return str(self.pk)

class Token_Session(models.Model):
    session_name=models.CharField(null=False, blank=False, max_length=20)
    is_active=models.BooleanField(null=False, blank=False, default=False)
    is_independent=models.BooleanField(null=False, blank=False, default=False)

    class Meta:
        verbose_name="Token Session"

    def current_session():
        return Token_Session.objects.filter(is_active=True)

    def save(self, *args, **kwargs):
        if (self.pk):
            if(kwargs.get('is_active') == 'on' and (kwargs.get('is_independent') == 'off' or self.is_independent == False)):
                Token_Session.objects.filter(is_active=True, is_independent=False).update(is_active=False)
        
        super().save(*args, **kwargs)


    def __self__(self):
        return self.pk