import base64
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import os
from time import sleep
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from dotenv import set_key
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from django.core.files.base import ContentFile
from django.template.loader import render_to_string

from emails.models import Registered_Participant, EventFormStatus
from insb_spac24 import settings
from django.contrib import messages
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST

# Create your views here.
@login_required
def send_emails(request):

    credentials = get_credentials()
    # if not credentials:
    #     print("NOT OKx")
    #     return False
    # try:
    service = build(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, credentials=credentials)
    print(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, 'service created successfully')

    registered_participants = Registered_Participant.objects.all()
    for participant in registered_participants:
        try:
            message = MIMEMultipart()

            message["From"] = "IEEE NSU SB Portal <ieeensusb.portal@gmail.com>"
            message["To"] = participant.email
            message["Cc"] = 'sb-nsu@ieee.org'
            message["Subject"] = 'Confirmation of Your Participation and Guidelines in SPAC’24 organised by IEEE NSU Student Branch'

            booth = '3 and 4'
            if(participant.university == 'North South University'):
                booth = '3 and 4'
            else:
                booth = '1 and 2'

            message.attach(MIMEText(render_to_string('email_template.html', {'name':participant.name, 'university':participant.university, 'booth':booth}), 'html'))

            content_file = open(f"Participant Files/Participant_QR/{participant.id}.png", "rb")

            part = MIMEBase('application', 'octet-stream')
            part.set_payload(content_file.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={participant.name}.png',
            )
            message.attach(part)

            content_file2 = open(f"Participant Files/SPAC24 Event Timeline.pdf", "rb")

            part2 = MIMEBase('application', 'octet-stream')
            part2.set_payload(content_file2.read())
            encoders.encode_base64(part2)
            part2.add_header(
                'Content-Disposition',
                f'attachment; filename=SPAC24 Event Timeline.pdf',
            )
            message.attach(part2)

            # encoded message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            create_message = {"raw": encoded_message}

            send_message = (
                service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )

            print(f'Serial: {participant.id}, Message Id: {send_message["id"]}')
            sleep(3)
        except Exception as e:
            print(e)
            return JsonResponse({'message':'error'})

    return JsonResponse({'message':'success'})

@login_required
def send_email(request):
    
    credentials = get_credentials()

    data = json.loads(request.body)
    if not credentials:
        return JsonResponse({'message':'Please re-authorise google api'})
    try:
        service = build(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, credentials=credentials)
        print(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, 'service created successfully')
        message = MIMEMultipart()
        message["From"] = "IEEE NSU SB Portal <ieeensusb.portal@gmail.com>"
        message["To"] = data['emailAddr']
        message["Subject"] = "QR Code for SPAC'24"
        message.attach(MIMEText(f'''Dear Participant,
                                
Your QR code for SPAC'24 event is attached in this email.
This QR code is essential to collect your food and goodies.
                                
Best regards,
                                
IEEE NSU SB.''', 'plain'))
        
        content_file = open(f"Participant Files/Participant_QR/{data['participant_id']}.png", "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(content_file.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={data["participant_id"]}.png',
        )
        message.attach(part)
        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        create_message = {"raw": encoded_message}
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        print(f'Message Id: {send_message["id"]}')
    except Exception as e:
        return JsonResponse({'message':'error'})
    
    return JsonResponse({'message':'success'})

@login_required
def authorize(request):

    credentials = get_credentials(request)
    if not credentials:
        flow = get_google_auth_flow(request)
        if(request.META['HTTP_HOST'] == "127.0.0.1:8000" or request.META['HTTP_HOST'] == "localhost:8000"):
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
            )
        else:
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                login_hint='ieeensusb.portal@gmail.com'
            )
        request.session['state'] = state
        return redirect(authorization_url)

    # if credentials != None:
        # messages.success(request, "Already authorized!")    
    return redirect('core:dashboard')

def oauth2callback(request):
    try:
        if(request.META['HTTP_HOST'] == "127.0.0.1:8000" or request.META['HTTP_HOST'] == "localhost:8000"):
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        state = request.GET.get('state')
        if state != request.session.pop('state', None):
            return HttpResponseBadRequest('Invalid state parameter')
        
        flow = get_google_auth_flow(request)
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        credentials = flow.credentials
        save_credentials(credentials)
        # messages.success(request, "Authorized")
        return redirect('core:dashboard')
    except:
        # messages.warning(request, "Access Denied!")
        return redirect('core:dashboard')
    
def get_google_auth_flow(request):
    client_config = {
        'web': {
            'client_id': settings.GOOGLE_CLOUD_CLIENT_ID,
            'project_id': settings.GOOGLE_CLOUD_PROJECT_ID,
            'auth_uri': settings.GOOGLE_CLOUD_AUTH_URI,
            'token_uri': settings.GOOGLE_CLOUD_TOKEN_URI,
            'auth_provider_x509_cert_url': settings.GOOGLE_CLOUD_AUTH_PROVIDER_x509_cert_url,
            'client_secret': settings.GOOGLE_CLOUD_CLIENT_SECRET,
        }
    }
    if(request.META['HTTP_HOST'] == "127.0.0.1:8000" or request.META['HTTP_HOST'] == "localhost:8000"):
        redirect_uri=f"http://{request.META['HTTP_HOST']}/init/oauth2callback"
    else:
        redirect_uri=f"https://{request.META['HTTP_HOST']}/init/oauth2callback"

    return Flow.from_client_config(
        client_config,
        settings.SCOPES,
        redirect_uri=redirect_uri
    )

def save_credentials(credentials):
        set_key('.env', 'GOOGLE_CLOUD_TOKEN', credentials.token)
        settings.GOOGLE_CLOUD_TOKEN = credentials.token
        if(credentials.refresh_token):
            set_key('.env', 'GOOGLE_CLOUD_REFRESH_TOKEN', credentials.refresh_token)
            settings.GOOGLE_CLOUD_REFRESH_TOKEN = credentials.refresh_token
        if(credentials.expiry):
            set_key('.env', 'GOOGLE_CLOUD_EXPIRY', credentials.expiry.isoformat())
            settings.GOOGLE_CLOUD_EXPIRY = credentials.expiry.isoformat()


def get_credentials():
    
        creds = None

        if settings.GOOGLE_CLOUD_TOKEN:
            creds = Credentials.from_authorized_user_info({
                'token':settings.GOOGLE_CLOUD_TOKEN,
                'refresh_token':settings.GOOGLE_CLOUD_REFRESH_TOKEN,
                'token_uri':settings.GOOGLE_CLOUD_TOKEN_URI,
                'client_id':settings.GOOGLE_CLOUD_CLIENT_ID,
                'client_secret':settings.GOOGLE_CLOUD_CLIENT_SECRET,
                'expiry':settings.GOOGLE_CLOUD_EXPIRY
            },scopes=settings.SCOPES)

        if not creds or not creds.valid:

            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    save_credentials(creds)
                except:
                    print("NOT OK")
                    return None
            
            return creds

        return creds

def _get_publish_status() -> bool:
    status = EventFormStatus.objects.order_by('-updated_at').first()
    return bool(status and status.is_published)

def registration_form(request):
    """Display the registration form for general users. Hidden if not published."""
    # If staff/superuser hits the user URL, send them to the admin view
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('emails:registration_admin')
    context = {
        'is_staff_view': False,
        'is_published': _get_publish_status(),
    }
    return render(request, 'form.html', context)

@staff_member_required
def registration_admin(request):
    """Staff-only admin view to manage and preview the form regardless of publish state."""
    context = {
        'is_staff_view': True,
        'is_published': _get_publish_status(),
    }
    return render(request, 'form.html', context)

@staff_member_required
@require_POST
def toggle_publish(request):
    """Toggle EventFormStatus.is_published and return current status."""
    status = EventFormStatus.objects.order_by('-updated_at').first()
    if not status:
        status = EventFormStatus.objects.create(is_published=True)
    else:
        status.is_published = not status.is_published
        status.save(update_fields=['is_published'])
    return JsonResponse({'success': True, 'is_published': status.is_published})

def submit_form(request):
    """Handle form submission and save participant data"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            email = request.POST.get('email')
            contact_number = request.POST.get('contact_number')
            membership_type = request.POST.get('membership_type')
            ieee_id = request.POST.get('ieee_id')
            university = request.POST.get('university')
            department = request.POST.get('department')
            university_id = request.POST.get('university_id')
            payment_method = request.POST.get('payment_method')
            transaction_id = request.POST.get('transaction_id')
            tshirt_size = request.POST.get('tshirt_size')
            comments = request.POST.get('comments', '')
            
            # Collect questionnaire answers
            answers = {
                'question1': request.POST.get('question1', ''),
                'question2': request.POST.get('question2', ''),
                'question3': request.POST.get('question3', ''),
                'question4': request.POST.get('question4', ''),
            }
            
            # Create and save participant
            participant = Registered_Participant.objects.create(
                name=name,
                email=email,
                contact_number=contact_number,
                membership_type=membership_type,
                ieee_id=ieee_id,
                university=university,
                department=department,
                university_id=university_id,
                payment_method=payment_method,
                transaction_id=transaction_id,
                tshirt_size=tshirt_size,
                comments=comments,
                answers=answers
            )
            
            # Return success response
            return JsonResponse({
                'success': True,
                'message': 'Registration successful! Your participant ID is: ' + str(participant.id),
                'participant_id': participant.id
            })
            
        except Exception as e:
            # Return error response
            return JsonResponse({
                'success': False,
                'message': 'Registration failed: ' + str(e)
            })
    
    # If not POST request, return error
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })
