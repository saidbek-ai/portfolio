from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress


class Command(BaseCommand):
    help = 'Verify email addresses for all staff and superusers'

    def handle(self, *args, **options):
        User = get_user_model()

        privilaged_users = User.objects.filter(is_staff=True,) | User.objects.filter(is_superuser=True)
        verified_count = 0

        for user in privilaged_users.distinct():
            if user.email:
                email_addr, created = EmailAddress.objects.get_or_create(user=user, email=user.email, defaults={'verified': True, 'primary': True})

                if not email_addr.verified:
                    email_addr.verified = True
                    email_addr.primary = True
                    email_addr.save()

                    verified_count +=1
                    self.stdout.write(self.style.SUCCESS(f'Verified email for {user.email}'))
        self.stdout.write(
            self.style.SUCCESS(f'Successfully verified {verified_count} privileged users')
        )