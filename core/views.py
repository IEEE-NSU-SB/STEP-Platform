import csv
import json
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from django.db import connection

from access_ctrl.decorators import permission_required
from access_ctrl.utils import Site_Permissions
from insb_spac24 import settings
from .renderData import Core

from core.forms import CSVImportForm
from core.models import Registered_Participant

# Create your views here.
def login(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if(request.method == 'POST'):
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if(user is not None):
            # Check for the 'next' parameter in the GET request
            next_url = request.GET.get('next')

            auth.login(request, user)
            if next_url:
                # Redirect to the originally requested URL
                return redirect(next_url)
            else:
                return redirect('core:dashboard')
        else:
            messages.error(request, "Credentials don't match")

    return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('core:login')

class Process_QR_Data(View):
    def post(self, request):
        try:
            if request.user.is_authenticated:
                response = Core.process_qr_data(request)
                
                return response
            else:
                return render(request, '404.html')
        except:
            return JsonResponse({'message':'error'})
        
    def get(self, request):
        return render(request, '404.html')
    
@login_required
def import_csv(request):
    form = CSVImportForm(request.POST, request.FILES)
    if form.is_valid():
        csv_file = request.FILES['csv_file'].read().decode('utf-8').splitlines()
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            participant = Registered_Participant.objects.create(
                id=row['Serial No.'],
                name=row['Name'],
                university=row['University Name'],
                email=row['Email Address'],
                contact_no=row['Contact'],
                role=row['Role'],
                t_shirt_size=row['T-shirt Size'],
                unique_code=Core.generate_unique_code(row['Name'], row['University Name'])
            )
        
        return redirect('core:dashboard')
    else:
        form = CSVImportForm()
    
    return render(request, 'csv.html', {'form': form})

active_sessions = 0

@login_required
@permission_required('view_qr_dashboard')
def dashboard(request):
    
    token_sessions = Core.get_active_token_sessions()
    token_sessions_all = Core.get_all_token_sessions()
    token_sessions_with_participant_count = Core.get_all_token_sessions_with_participant_counts()
    universities = Core.get_all_participant_universities()
    registered_participants = Core.get_all_reg_participants_with_sessions()

    total_participants = len(registered_participants)
            
    request.session['active_sessions'] = active_sessions

    context = {
        'token_sessions':token_sessions,
        'token_sessions_all':token_sessions_all,
        'token_sessions_with_participant_count':token_sessions_with_participant_count,
        'registered_participants':registered_participants,
        'total_participants':total_participants,
        'participant_universities':universities,
    }

    return render(request, 'coordinator_dashboard.html', context)

class SessionUpdateAjax(View):
    def post(self, request):
        try:
            if request.user.is_authenticated and Site_Permissions.user_has_permission(request.user, 'update_session'):
                sessions = json.loads(request.body)['sessions']
                
                if(Core.update_session(sessions=sessions)):
                    global active_sessions
                    active_sessions += 1

                    if active_sessions > 10000:
                        active_sessions = 1

                    return JsonResponse({'message':"success"})
                else:
                    return JsonResponse({'message':"error"})
            else:
                return render(request, '404.html')
        except:
            return JsonResponse({'message':'error'})
    
    def get(self, request):
        return render(request, '404.html')

class GetSessionStatusAjax(View):
    def post(self, request):
        try:
            if request.user.is_authenticated and Site_Permissions.user_has_permission(request.user, 'view_qr_dashboard'):
                last_updated_date_time = json.loads(request.body)['last_updated_date_time']
                token_sessions_with_participant_count = Core.get_all_token_sessions_with_participant_counts()

                new_scans = Core.get_new_token_session_scans(last_updated_date_time)

                data = {}
                status = {}
                for x in token_sessions_with_participant_count:
                    status.update({x['sessionid']: x['participant_count']})
                data.update({'status':status})
                scans = {}
                for x in new_scans:
                    scans.update({x['registered_participant']: x['token_session']})
                data.update({'new_scans': scans})

                if(request.session['active_sessions'] != active_sessions):
                    data.update({'session_update':''})
                        
                return JsonResponse(data)
            else:
                return render(request, '404.html')
        except:
            return JsonResponse({'message':'error'})
        
    def get(self, request):
        return render(request, '404.html')

class UpdateParticipantSessionAjax(View):
    def post(self, request):
        try:
            if request.user.is_authenticated and Site_Permissions.user_has_permission(request.user, 'scan_session'):
                data = json.loads(request.body)

                response = Core.update_participant_session(data['participant_id'], data['session_id'], data['status'])
                return response
            else:
                return render(request, '404.html')
        except:
            return JsonResponse({'message':'error'})
    
    def get(self, request):
        return render(request, '404.html')
    
from .qrgenerator import *

@login_required
def gen(request):
   
    if(Site_Permissions.is_superuser(request.user)):
        generate_qr()
        return JsonResponse({'message':'success'})
    else:
        return render(request,'404.html')


@login_required
def import_reg_participants(request):

    if(Site_Permissions.is_superuser(request.user)):
        Core.import_participants_from_reg()
        return JsonResponse({'message':'success'})
    else:
        return render(request,'404.html')
    
@login_required
def set_db_increment_counter(request):

    if(Site_Permissions.is_superuser(request.user)):
        try:
            increment_init = int(request.GET.get('incr_v'))
            with connection.cursor() as cursor:
                db_engine = settings.DATABASES['default']['ENGINE']
                if db_engine == 'django.db.backends.mysql' or db_engine == 'django.db.backends.mariadb':
                    # MySQL or MariaDB
                    cursor.execute(f"ALTER TABLE core_registered_participant AUTO_INCREMENT = {increment_init};")
                elif db_engine == 'django.db.backends.postgresql':
                    # PostgreSQL
                    cursor.execute(f"SELECT setval('core_registered_participant_id_seq', {increment_init}, false);")
                elif db_engine == 'django.db.backends.sqlite3':
                    # SQLite
                    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name = 'core_registered_participant';")
                    cursor.execute(f"INSERT INTO sqlite_sequence (name, seq) VALUES ('core_registered_participant', {increment_init - 1});")
                else:
                    raise Exception(f"Unsupported database engine: {db_engine}")
        except Exception as e:
            return JsonResponse({'message':'error', 'details': str(e)})

        return JsonResponse({'message':'success'})
    else:
        return render(request,'404.html')

@login_required
def update_db_serial(request):

    if(Site_Permissions.is_superuser(request.user)):
        try:
            counter = 1
            participants = Registered_Participant.objects.values('id').order_by('id')
            for participant in participants:
                Registered_Participant.objects.filter(id=participant['id']).update(id=counter)
                counter += 1
        except Exception as e:
            return JsonResponse({'message':'error', 'details':str(e)})

        return JsonResponse({'message':'success'})
    else:
        return render(request,'404.html')