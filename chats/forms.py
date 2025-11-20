from django import forms
from .models import Message

class SendMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']  
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Type your message...',
                'class': 'send_message__input',
                'rows': 1,
                'oninput': 'autoResize(this)',
                'id': 'send-message__input',
                'autofocus': True
            })
        }