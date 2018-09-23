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
