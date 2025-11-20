import unicodedata
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    username = forms.CharField(max_length=50, required=True)
    organisation = forms.CharField(max_length=255, required=False)
    bio = forms.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = ['image', 'organisation', 'first_name', 'last_name', 'username', 'bio']

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip().lower()

        if not username:
            raise forms.ValidationError(_("Username is required."))

        # Enforce ASCII (Latin-only)
        normalized = unicodedata.normalize('NFKD', username)
        try:
            normalized.encode('ascii')
        except UnicodeEncodeError:
            raise forms.ValidationError(_("Only Latin (English) letters are allowed."))

        if len(username) < 3:
            raise forms.ValidationError(_("Username must be at least 3 characters long."))

        if User.objects.exclude(id=self.instance.id).filter(username=username).exists():
            raise forms.ValidationError(_("This username is already taken."))

        return username

    def save(self, commit=True):
        user = super().save(commit=False)

        for field, value in self.cleaned_data.items():
            # If empty (including None or ""), keep the old value
            if value in [None, ''] and hasattr(self.instance, field):
                setattr(user, field, getattr(self.instance, field))

        if commit:
            user.save()
        return user

