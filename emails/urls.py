
from django.urls import path
from .views import *

app_name='emails'

urlpatterns = [
    # path('init/send_emails/', send_emails),
    path('api/send_email/', send_email, name='send_email'),
    path('init/authorise/', authorize),
    path('init/oauth2callback/', oauth2callback, name='oauth2callback'),
    path('registration/', registration_form, name='registration_form'),
    path('submit-form/', submit_form, name='submit_form'),
]
