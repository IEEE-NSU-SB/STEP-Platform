
from django.urls import path
from .views import *

app_name='emails'

urlpatterns = [
    # path('init/send_emails/', send_emails),
    path('authorise/', authorize),
    path('portal/oauth2callback/', oauth2callback, name='oauth2callback'),
]
