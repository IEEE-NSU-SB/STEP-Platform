
import json
import random
import string

from django.http import JsonResponse
from core.models import Registered_Participant, Token_Participant, Token_Session
from django.db.models import Count, F, Prefetch, Value
from django.db.models.functions import Coalesce

class Core:

    def get_active_token_sessions():

        return Token_Session.objects.filter(is_active=True).order_by('order_of_session')

    def get_all_token_sessions():
        
        return Token_Session.objects.all().order_by('order_of_session')

    def get_all_token_sessions_with_participant_counts():
        
        return Token_Session.objects.values('session_name',sessionid=F('id')).annotate(participant_count=Coalesce(Count('token_participant'), Value(0))).order_by('order_of_session')

    def get_all_participant_universities():
        
        return Registered_Participant.objects.values('university').distinct()
    
    def get_all_reg_participants_with_sessions():

        registered_participants = Registered_Participant.objects.prefetch_related(
            Prefetch(
                'token_participant_set',  # Related name for Token_Participant
                queryset=Token_Participant.objects.only('token_session'),  # Optimize with select_related for Token_Session
                to_attr='tokens'
            )
        )
        return registered_participants
    
    def process_qr_data(request):
        try:
            # Get the POST data from the request body
            print(f"Received RAW QR Data: {request.body}")
            session=request.headers.get('session-id')
            data = json.loads(request.body)

            participant = Registered_Participant.objects.get(unique_code=data.get('unqc'))
            print(participant.name)
            if len(Token_Participant.objects.filter(registered_participant=participant,token_session=session)) > 0:
                return JsonResponse({'message':'QR Received Successfully', 'status': 'rejected', 'participant': {'sl':participant.id, 'name': participant.name}})
            else:
                token_session = Token_Session.objects.get(id=session)
                Token_Participant.objects.create(registered_participant=participant,token_session=token_session)
                return JsonResponse({'message':'QR Received Successfully', 'status': 'accepted', 'participant': {'sl':participant.id, 'name': participant.name}})
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
    def update_session(sessions):
        all_sessions = Core.get_all_token_sessions()

        for session in all_sessions:
            if str(session.id) in sessions:
                session.is_active = True
            else:
                session.is_active = False
            
            session.save()
        
        return True
    
    
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