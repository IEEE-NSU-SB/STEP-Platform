from django.shortcuts import render

from core.models import Token_Session

# Create your views here.
def login(request):
    return render(request, 'login.html')

def dashboard(request):

    token_sessions = Token_Session.objects.filter(is_active=True).order_by('order_of_session')

    context = {
        'token_sessions':token_sessions
    }

    return render(request, 'dashboard.html', context)