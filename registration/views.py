import csv
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import EventFormStatus, Form_Participant

def _get_publish_status() -> bool:
    status = EventFormStatus.objects.order_by('-updated_at').first()
    return bool(status and status.is_published)

def registration_form(request):
    """Display the registration form for general users. Hidden if not published."""
    # If staff/superuser hits the user URL, send them to the admin view
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('registration:registration_admin')
    context = {
        'is_staff_view': False,
        'is_published': _get_publish_status(),
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
    
@login_required
def download_excel(request):
    participants = Form_Participant.objects.all().values()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="participants.csv"'
    writer = csv.writer(response)
    rows = list(participants)
    if rows:
        writer.writerow(rows[0].keys())
        for row in rows:
            writer.writerow(row.values())
    else:
        writer.writerow(['message'])
        writer.writerow(['No participants'])
    return response

