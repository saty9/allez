from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from main.models import Organisation, OrganisationMembership


def organisation(request, org_id):
    org = get_object_or_404(Organisation, pk=org_id)
    if request.method == "POST":
        r_type = request.POST['type']
        if r_type == "join_request":
            return join_organisation(request, org)
    return JsonResponse({'success': False,
                         'reason': 'Unrecognised response'})


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

