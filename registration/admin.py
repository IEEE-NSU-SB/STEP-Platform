from django.contrib import admin

from .models import *
# Register your models here.

@admin.register(EventFormStatus)
class EventFormStatusAdmin(admin.ModelAdmin):
    list_display = ['is_published', 'updated_at']

@admin.register(Form_Participant)
class Form_ParticipantAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'university', 'email', 'membership_type', 'is_student', 'created_at']

#TEMPORARY
@admin.register(T_Shirt_Form)
class T_Shirt_FormAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'ieee_id', 'created_at']