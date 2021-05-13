from django.contrib.auth.forms import UserCreationForm
from django import forms


class UserCreationFormWithPrivacyNotice(UserCreationForm):
    privacy_consent = forms.BooleanField(
        label="""GDPR Notice HERE"""
    )

    def is_valid(self):
        return super().is_valid() and self.cleaned_data['privacy_consent']
