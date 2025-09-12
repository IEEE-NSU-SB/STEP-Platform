
from django.urls import path
from .views import *

app_name='emails'

urlpatterns = [
    # path('init/send_emails/', send_emails),
    path('api/send_email/', send_email, name='send_email'),
    path('init/authorise/', authorize),
    path('init/oauth2callback/', oauth2callback, name='oauth2callback'),
    # Public/user registration form (only visible when published)
    path('registration/', registration_form, name='registration_form'),
    # Staff-only admin view of the form and controls
    path('registration/admin/', registration_admin, name='registration_admin'),
    # Publish toggle endpoint (staff-only)
    path('registration/toggle-publish/', toggle_publish, name='toggle_publish'),
    path('submit-form/', submit_form, name='submit_form'),
    path('download-excel/', download_excel, name='download_excel'),
]
