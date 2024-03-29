from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView

from ui.forms.user import UserCreationFormWithPrivacyNotice


class RegisterUser(FormView):
    template_name = 'registration/register.html'
    form_class = UserCreationFormWithPrivacyNotice
    success_url = reverse_lazy("ui/organisation/list")

    @method_decorator(sensitive_post_parameters('password1', 'password2'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        user = authenticate(self.request, username=form.cleaned_data["username"], password=form.cleaned_data["password1"])
        login(self.request, user)
        return super().form_valid(form)
