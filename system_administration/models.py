from django.db import models

# Create your models here.

class ErrorLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=500, blank=True, null=True)
    method = models.CharField(max_length=10, blank=True, null=True)
    user = models.CharField(max_length=255, blank=True, null=True)
    exception_type = models.CharField(max_length=255)
    message = models.TextField()
    traceback = models.TextField()

    def __str__(self):
        return f"{self.timestamp} - {self.exception_type}"