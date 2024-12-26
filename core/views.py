import csv
import json
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required

from core.permissions import Site_Permissions
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
            auth.login(request, user)
            return redirect('core:dashboard')
        else:
            messages.error(request, "Credentials don't match")

    return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('core:login')

def process_qr_data(request):
    
    if request.method == 'POST':

        response = Core.process_qr_data(request)
        
        return response
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
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
def dashboard(request):

    token_sessions = Core.get_active_token_sessions()
    token_sessions_all = Core.get_all_token_sessions()
    token_sessions_with_participant_count = Core.get_all_token_sessions_with_participant_counts()
    universities = Core.get_all_participant_universities()
    registered_participants = Core.get_all_reg_participants_with_sessions()
    user_permissions = Site_Permissions.get_user_permissions(request)
    is_admin = Site_Permissions.is_admin(request)
    has_scan_any_session_permission = is_admin or user_permissions.scan_any_session

    total_participants = len(registered_participants)
            
    request.session['active_sessions'] = active_sessions

    context = {
        'token_sessions':token_sessions,
        'token_sessions_all':token_sessions_all,
        'token_sessions_with_participant_count':token_sessions_with_participant_count,
        'registered_participants':registered_participants,
        'total_participants':total_participants,
        'participant_universities':universities,
        'user_permissions':user_permissions,
        'is_admin':is_admin,
        'has_scan_any_session_permission':has_scan_any_session_permission
    }

    return render(request, 'coordinator_dashboard.html', context)

class SessionUpdateAjax(View):
    def post(self, request):
        sessions = json.loads(request.body)['sessions']
        
        if(Core.update_session(sessions=sessions)):
            global active_sessions
            active_sessions += 1

            return JsonResponse({'message':"success"})
        else:
            return JsonResponse({'message':"error"})
    
class GetSessionStatusAjax(View):
    def post(self, request):
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
    
class UpdateParticipantSessionAjax(View):
    def post(self, request):
        data = json.loads(request.body)

        response = Core.update_participant_session(data['participant_id'], data['session_id'], data['status'])
        return response
    
from .qrgenerator import *

@login_required
def gen(request):
   generate_qr()

   return JsonResponse({'message':'success'})