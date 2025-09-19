import mimetypes
import os

from django.http import FileResponse, Http404, HttpResponse
from insb_spac24 import settings

def protected_serve(request, path):
    if request.user.is_authenticated:
        # Build the absolute file path
        file_path = os.path.join(settings.PROTECTED_ROOT, path)

        if not os.path.exists(file_path):
            raise Http404("File not found")

        # Guess content type
        content_type, _ = mimetypes.guess_type(file_path)

        # Return the file as response
        return FileResponse(open(file_path, 'rb'), content_type=content_type)
    else:
        return HttpResponse('Access Denied')