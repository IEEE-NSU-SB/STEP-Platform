import csv
import json
import random
import string
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required

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
            return redirect('main:dashboard')
        else:
            messages.error(request, "Credentials don't match")

    return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('core:index')

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
                unique_code=generate_unique_code(row['Name'], row['University Name'])
            )
        
        return redirect('core:dashboard')
    else:
        form = CSVImportForm()
    
    return render(request, 'csv.html', {'form': form})

def generate_unique_code(name: str, university: str) -> str:
    # Function to pick a random part of a string
    def get_random_part(s):
        if len(s) > 1:  # Ensure there are at least 2 characters to pick from
            start = random.randint(0, len(s) - 1)
            end = random.randint(start + 1, len(s))  # Ensure end > start
            return s[start:end]
        return s  # Return the whole string if it's too short
    
    # Pick random parts of the name and university
    name_part = get_random_part(name.replace(" ", "").replace(".", ""))
    university_part = get_random_part(university.replace(" ", "").replace(".", ""))
    
    # Combine the random parts
    base_string = name_part + university_part
    
    # Randomly shuffle the base string
    shuffled = ''.join(random.sample(base_string, len(base_string)))
    
    # Add random characters to make the code between 13 and 16 characters
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    # Combine shuffled string with random characters
    combined = shuffled + random_chars
    
    # Ensure the length is between 13 and 16 characters
    unique_code = combined[:random.randint(13, 16)]
    
    return unique_code

def dashboard(request):

    token_sessions = Token_Session.objects.filter(is_active=True).order_by('order_of_session')

    context = {
        'token_sessions':token_sessions
    }

    return render(request, 'dashboard.html', context)

def coordinator_dashboard(request):

    return render(request, 'coordinator_dashboard.html')