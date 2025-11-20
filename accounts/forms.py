import unicodedata
from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class CompleteProfileForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^(?!.*\.\.)[a-z0-9._]+$',
                message=_("Username may contain only lowercase Latin letters (a–z), numbers (0–9), underscores (_), and dots (.), and must not contain consecutive dots."),
                code="invalid_username"
            ),
        ],
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "bio", "organisation"]

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for field in self.fields.values():
    #         field.required = True  # make all required

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
