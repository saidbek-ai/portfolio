from allauth.account.adapter import DefaultAccountAdapter
from allauth.account import app_settings
from allauth.account.models import EmailAddress
from django.core.exceptions import ValidationError

class AdvancedAccountAdapter(DefaultAccountAdapter):
    def is_email_verification_required(self, user):
        if user.is_superuser or user.is_staff:
            return False
        
        if hasattr(user, 'groups'):
            exempt_groups = ["Trusted Users", "Internal Team"]

            if user.groups.filter(name__in=exempt_groups).exists():
                return False 
        

        return super().is_email_verification_required(user)
    
    def save_user(self, request, user, form, commit=True):
        
        """
        Auto-verify during user creation for privileged users
        """
        user = super().save_user(request, user, form, commit=False)

        if(user.is_staff or user.is_superuser) and user.email:
            if commit:
                user.save()
                 # Create and verify email address
                email_addr, created = EmailAddress.objects.get_or_create(user=user, email=user.email,defaults={'verified': True, 'primary': True})

                if not created:
                    email_addr.verified = True
                    email_addr.primary = True
                    email_addr.save()
            else:
                # Store flag to verify email after user is saved
                user._auto_verify_email = True
        elif commit:
            user.save()

    def login(self, request, user):
        """
          Allow login for staff/superusers even if email isn't verified
        """
        has_verified_email = EmailAddress.objects.filter(user=user, verified=True).exists()

          # Allow login for staff/superusers even without verified email
        if (user.is_staff or user.is_superuser) and not has_verified_email:
            # Bypass the email verification check
            return super().login(request, user)
        
        # Normal login flow for regular users
        return super().login(request, user)