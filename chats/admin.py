from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Chat, Message

# Register your models here.
@admin.register(Chat)
class ChatClass(ModelAdmin):
    list_display= ('__str__','user', 'updated_at',)
  


@admin.register(Message)
class MessageClass(ModelAdmin):
    list_display = ('chat', 'text', 'sender', 'read',  'created_at', 'deleted_at')
    list_filter = ("chat", "created_at")