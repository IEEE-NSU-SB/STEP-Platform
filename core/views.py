import csv
import json
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from .renderData import Core

from core.forms import CSVImportForm
from core.models import Registered_Participant, Token_Participant, Token_Session

# Create your views here.
def login(request):
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

def scan_qr(request, session_id=None):
    if session_id:
        print(session_id)
        return render(request, 'scan.html', {'current_session':session_id})
    else:
        current_session=Token_Session.current_session()
        return render(request, 'scan.html', {'current_session':current_session.pk})

@csrf_exempt
def process_qr_data(request):
    
    if request.method == 'POST':
        try:
            # Get the POST data from the request body
            print(f"Received RAW QR Data: {request.body}")  # Print to console (optional)
            session=request.headers.get('session-id')
            data = json.loads(request.body)

            print(f"Received QR Data: {data.get('unqc')}")  # Print to console (optional)

            # Here you can save the data to the database if needed
            # Example:
            participant = Registered_Participant.objects.get(unique_code=data.get('unqc'))
            if len(Token_Participant.objects.filter(registered_participant=participant,token_session=session)) > 0:
                print('rejected')
                return JsonResponse({'error': 'Rejected'})
            else:
                token_session = Token_Session.objects.get(id=session)
                Token_Participant.objects.create(registered_participant=participant,token_session=token_session)
                print('accepted')      
                return JsonResponse({'message': 'QR data received successfully!', 'receivedData': data})
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
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

@login_required
def dashboard(request):

    token_sessions = Core.get_active_token_sessions()
    token_sessions_all = Core.get_all_token_sessions()
    token_sessions_with_participant_count = Core.get_all_token_sessions_with_participant_counts()
    universities = Core.get_all_participant_universities()
    registered_participants = Core.get_all_reg_participants_with_sessions()

    total_participants = len(registered_participants)

    context = {
        'token_sessions':token_sessions,
        'token_sessions_all':token_sessions_all,
        'token_sessions_with_participant_count':token_sessions_with_participant_count,
        'registered_participants':registered_participants,
        'total_participants':total_participants,
        'participant_universities':universities,
    }

    return render(request, 'coordinator_dashboard.html', context)
