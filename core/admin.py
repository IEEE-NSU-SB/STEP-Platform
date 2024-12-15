from django.contrib import admin
from core.models import Token_Session

# Register your models here.
@admin.register(Token_Session)
class SessionAdmin(admin.ModelAdmin):
    
    list_display = ['session_name', 'is_independent', 'is_active']

    def save_model(self, request, obj, form, change):
        print(form.data)
        if(form.data.get('is_active') == 'on' and (form.data.get('is_independent') == 'off' or obj.is_independent == False)):
                Token_Session.objects.filter(is_active=True, is_independent=False).update(is_active=False)

        super().save_model(request, obj, form, change)