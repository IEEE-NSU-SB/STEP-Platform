
from django.urls import path
from .views import *

app_name='core'

urlpatterns = [
    path('', login, name="login"),
    path('logout/', logout, name="logout"),
    path('dashboard/', dashboard, name="dashboard"),
    path('scan/', scan_qr, name="qr_scan"),
    path('scan/<int:session_id>', scan_qr, name="qr_scan"),
    path('process_qr_data/', process_qr_data, name="process_qr_data"),
    path('coordinator_dashboard/', coordinator_dashboard, name="coordinator_dashboard"),
    path('import_csv/', import_csv, name='import_csv'),
]
