import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from core.models import Registered_Participant, Token_Participant, Token_Session

# Create your views here.
def login(request):
    return render(request, 'login.html')

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

def dashboard(request):

    token_sessions = Token_Session.objects.filter(is_active=True).order_by('order_of_session')

    context = {
        'token_sessions':token_sessions
    }

    return render(request, 'dashboard.html', context)

def coordinator_dashboard(request):

    return render(request, 'coordinator_dashboard.html')