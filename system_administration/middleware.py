# core/middleware.py
import traceback
from django.utils.deprecation import MiddlewareMixin
from core.models import ErrorLog

class GlobalExceptionLoggingMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        tb = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))

        ErrorLog.objects.create(
            path=request.path,
            method=request.method,
            user=str(request.user) if hasattr(request, "user") and request.user.is_authenticated else None,
            exception_type=type(exception).__name__,
            message=str(exception),
            traceback=tb
        )
        # Let Django continue handling (show debug page or 500 page)
        return None
