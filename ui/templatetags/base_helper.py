from django import template
from django.utils.html import format_html
from django.urls import reverse
from main.models import Organisation
register = template.Library()


@register.simple_tag(name="org_or_login_button")
def org_or_login(request):
    if request.user.is_authenticated:
        if request.session['org_id']:
            organisation = Organisation.objects.get(pk=request.session['org_id'])
            return format_html(organisation.name)
        else:
            return format_html('Join an Org')
    else:
        login_url = reverse('login') + '?next=' + request.path
        return format_html('<a class="nav-link" href={}>Login <i class="fas fa-sign-in-alt"></i></a>'.format(login_url))

