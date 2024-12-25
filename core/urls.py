
from django.urls import path
from .views import *

app_name='core'

urlpatterns = [
    path('', login, name="login"),
    path('logout/', logout, name="logout"),
    path('dashboard/', dashboard, name='dashboard'),
    path('api/process_qr_data/', process_qr_data, name="process_qr_data"),
    path('api/update_session/', SessionUpdateAjax.as_view(), name='update_session'),
    path('api/get_session_statuses/', GetSessionStatusAjax.as_view(), name="get_session_statuses"),
    path('api/update_participant_session', UpdateParticipantSessionAjax.as_view(), name="update_participant_session"),
    # path('init/import_csv/', import_csv, name='import_csv'),
    path('init/gen_qr/', gen),
]
