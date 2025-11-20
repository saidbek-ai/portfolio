from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
# from allauth.account.utils import send_email_confirmation
from allauth.account.models import EmailConfirmation
from django.shortcuts import redirect
from django.urls import reverse
from urllib.parse import urlencode
from django.core.cache import cache
from django.utils import timezone
import time


class AdvancedAccountAdapter(DefaultAccountAdapter):    
    def get_password_change_redirect_url(self, request):
        return reverse("users:user_profile")
    

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_connect_redirect_url(self, request, socialaccount):
        # Redirect to user profile page after connecting a social account
        return reverse("users:user_profile")


