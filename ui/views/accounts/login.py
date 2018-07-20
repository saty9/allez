from django.contrib.auth import get_user
from django.contrib.auth.views import LoginView


class LoginUser(LoginView):
    """extends default login view to allow extra actions to be taken when the user logs in"""
    def form_valid(self, form):
        user = form.get_user()
        if user.is_authenticated and not user.is_superuser:
            self.request.session['org_id'] = user.organisationmembership_set.order_by('last_active').first().id
        return super(LoginView, self).form_valid(form)
