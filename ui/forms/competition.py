from django import forms
from django.core.exceptions import ValidationError
from django.forms import SelectDateWidget
from django.utils import timezone
from django.utils.translation import gettext as _


class CreateCompetitionForm(forms.Form):
    name = forms.CharField(label="Competition Name", max_length=200)
    date = forms.DateField(label="Date", widget=SelectDateWidget)

    def clean_date(self):
        data = self.cleaned_data['date']
        if data < timezone.now().date():
            raise ValidationError(_('Competition dates must be in the future'))
        return data
