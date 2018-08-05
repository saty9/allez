from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from main.helpers.permissions import permission_required_json, direct_object
from main.models import Organisation, OrganisationMembership


def organisation(request, org_id):
    org = get_object_or_404(Organisation, pk=org_id)
    if request.method == "POST":
        r_type = request.POST['type']
        if r_type == "join_request":
            return join_organisation(request, org)
        elif r_type == "accept_application":
            return accept_application(request, org)
    return JsonResponse({'success': False,
                         'reason': 'Unrecognised request'})


@login_required
def join_organisation(request, org):
    user = get_object_or_404(User, pk=request.POST['user_id'])
    if user == request.user or request.user.has_perm('main.manage_organisation', org):
        if not org.organisationmembership_set.filter(user=user).exists():
            org.organisationmembership_set.create(user=user, state=OrganisationMembership.APPLICANT)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False,
                                 'reason': 'User is already a member'})

    else:
        return JsonResponse({'success': False, 'reason': 'InsufficientPermissions'}, status=403)


@login_required
@permission_required_json('main.manage_organisation', fn=direct_object)
def accept_application(request, org):
    """Allows an organisation manager to accept applications to join an org
    expects 'user_id' in POST to be the pk of the Organisation membership to accept"""
    user_id = request.POST['user_id']
    membership = get_object_or_404(OrganisationMembership, user_id=user_id, organisation=org)
    if membership.state == OrganisationMembership.APPLICANT:
        membership.state = OrganisationMembership.DT
        membership.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False,
                             'reason': "User is already a full member"})


