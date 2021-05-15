from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import CreateView

from main.models import Organisation, OrganisationMembership


@login_required
def organisation(request, org_slug):
    org = get_object_or_404(Organisation, slug=org_slug)
    full_members = org.organisationmembership_set.exclude(state=OrganisationMembership.APPLICANT)
    applicants = org.organisationmembership_set.filter(state=OrganisationMembership.APPLICANT)
    can_manage = request.user.has_perm('main.manage_organisation', org)
    return render(request, 'ui/organisation/show.html', context={'org': org,
                                                                 'full_members': full_members,
                                                                 'applicants': applicants,
                                                                 'can_manage': can_manage})


class CreateOrganisation(LoginRequiredMixin, CreateView):
    model = Organisation
    template_name = "ui/organisation/create.html"
    fields = ["name", "email", "slug"]

    def get_success_url(self):
        org = self.object
        self.request.session['org_id'] = org.id
        slug = org.slug
        return reverse('ui/org/competitions', kwargs={'org_slug': slug})

    def form_valid(self, form):
        response = super().form_valid(form)
        org = self.object
        org.organisationmembership_set.create(state=OrganisationMembership.MANAGER, user=self.request.user)
        return response


def organisation_list(request):
    orgs = Organisation.objects
    if request.user.is_active:
        user_orgs = request.user.organisationmembership_set.values_list('organisation', flat=True)
        other_orgs = orgs.exclude(pk__in=user_orgs)
        user_orgs = orgs.filter(pk__in=user_orgs)
    else:
        user_orgs = []
        other_orgs = orgs.all()
    return render(request, 'ui/organisation/list.html', context={'user_orgs': user_orgs,
                                                                 'other_orgs': other_orgs})
