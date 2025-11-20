# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

@receiver(post_save, sender=get_user_model())
def auto_verify_privileged_users(sender, instance, created, **kwargs):
    """
    Auto-verify email when user becomes staff/superuser
    """
    if (instance.is_staff or instance.is_superuser) and instance.email:
        email_addr, created = EmailAddress.objects.get_or_create(
            user=instance,
            email=instance.email,
            defaults={'verified': True, 'primary': True}
        )
        if not email_addr.verified:
            email_addr.verified = True
            email_addr.primary = True
            email_addr.save()