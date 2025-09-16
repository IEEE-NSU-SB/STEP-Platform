import csv
##import pandas as pd
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from emails.views import send_registration_email

from .models import EventFormStatus, Form_Participant

def _get_publish_status() -> bool:
    status = EventFormStatus.objects.order_by('-updated_at').first()
    return bool(status and status.is_published)

def registration_form(request):
    """Display the registration form for general users. Hidden if not published."""
    # If staff/superuser hits the user URL, send them to the admin view
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('registration:registration_admin')
    registration_count = Form_Participant.objects.count()
    registration_closed = registration_count >= 10000
    context = {
        'is_staff_view': False,
        'is_published': _get_publish_status(),
        'registration_closed': registration_closed,
    }
    return render(request, 'form.html', context)

@login_required
def registration_admin(request):
    """Staff-only admin view to manage and preview the form regardless of publish state."""

    registration_count = Form_Participant.objects.count()

    context = {
        'is_staff_view': True,
        'is_published': _get_publish_status(),
        'registration_count':registration_count,
    }
    return render(request, 'form.html', context)

@login_required
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
            is_student = request.POST.get('is_student_bool')
            name = request.POST.get('name')
            email = request.POST.get('email')
            contact_number = request.POST.get('contact_number')
            membership_type = request.POST.get('membership_type')
            ieee_id = request.POST.get('ieee_id')
            profession = request.POST.get('profession','')
            designation = request.POST.get('designation','')
            affiliation = request.POST.get('affiliation','')
            university = request.POST.get('university','')
            department = request.POST.get('department','')
            university_id = request.POST.get('university_id','')
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
            participant = Form_Participant.objects.create(
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
                answers=answers,
                profession = profession,
                designation = designation,
                is_student = is_student,
                affiliation = affiliation
            )

            send_registration_email(participant.email)
            
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
    
@login_required
def download_excel(request):
    participants = Form_Participant.objects.all()
    
    # Prepare data for Sheet 1: Basic Information (without questionnaire answers)
    basic_data = []
    for participant in participants:
        basic_row = {
            'ID': participant.id,
            'Name': participant.name,
            'Email': participant.email,
            'Contact Number': participant.contact_number,
            'Is Student': 'Yes' if participant.is_student else 'No',
            'Membership Type': participant.membership_type,
            'IEEE ID': participant.ieee_id,
            'Profession':participant.profession,
            'Affiliation':participant.affiliation,
            'Designation':participant.designation,
            'University': participant.university,
            'Department': participant.department,
            'University ID': participant.university_id,
            'Payment Method': participant.payment_method,
            'Transaction ID': participant.transaction_id,
            'T-shirt Size': participant.tshirt_size,
            'Comments': participant.comments,
            'Created At': participant.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        basic_data.append(basic_row)
    
    # Prepare data for Sheet 2: Questionnaire Answers
    questionnaire_data = []
    for participant in participants:
        answers = participant.answers or {}
        questionnaire_row = {
            'ID': participant.id,
            'Name': participant.name,
            'Email': participant.email,
            'Contact': participant.contact_number,
            'Q1': answers.get('question1', ''),
            'Q2': answers.get('question2', ''),
            'Q3': answers.get('question3', ''),
            'Q4': answers.get('question4', ''),
        }
        questionnaire_data.append(questionnaire_row)
    
    # Create Excel file with two sheets
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Basic Information
        if basic_data:
            df_basic = pd.DataFrame(basic_data)
            df_basic.to_excel(writer, index=False, sheet_name='Basic Information')
        else:
            # Create empty sheet if no data
            empty_df = pd.DataFrame({'Message': ['No participants registered']})
            empty_df.to_excel(writer, index=False, sheet_name='Basic Information')
        
        # Sheet 2: Questionnaire Answers
        if questionnaire_data:
            df_questionnaire = pd.DataFrame(questionnaire_data)
            df_questionnaire.to_excel(writer, index=False, sheet_name='Questionnaire Answers')
        else:
            # Create empty sheet if no data
            empty_df = pd.DataFrame({'Message': ['No participants registered']})
            empty_df.to_excel(writer, index=False, sheet_name='Questionnaire Answers')
    
    output.seek(0)
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="participants_data.xlsx"'
    return response

def dummy(request):
    # You can use a public sample video or a dummy YouTube embed
    context = {
        'video_embed_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',  # dummy YouTube
        'video_banner': None,  # or set a dummy MP4 if needed
    }
    return render(request, 'responses.html', context)

