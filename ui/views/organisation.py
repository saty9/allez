from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
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
