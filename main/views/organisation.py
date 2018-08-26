from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Subquery, OuterRef
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from main.helpers.permissions import permission_required_json, direct_object
from main.models import Organisation, OrganisationMembership, Competitor, Entry
from main.settings import MAX_AUTOCOMPLETE_RESPONSES
from main.utils.api_responses import api_success, api_failure


def organisation(request, org_id):
    org = get_object_or_404(Organisation, pk=org_id)
    if request.method == "POST":
        r_type = request.POST['type']
        if r_type == "join_request":
            return join_organisation(request, org)
        elif r_type == "accept_application":
            return accept_application(request, org)
    elif request.method == "GET":
        r_type = request.GET['type']
        if r_type == "autocomplete_competitor":
            return auto_complete_competitor(request, org)

    return api_failure('unrecognised request', _('Unrecognised request'))


@permission_required_json('main.view_organisation_competitors', fn=direct_object)
def auto_complete_competitor(request, org: Organisation):
    """get auto complete suggestions for an organisations competitors

        :param request: expecting GET parameters:\n
            :param str name: partial name of the competitor to search for must be > 3 char long for response
        :param Organisation org: organisation to search competitors for
    """
    partial_name = request.GET['name']
    if len(partial_name) < 3:
        return JsonResponse({'competitors': []})
    entries = Entry.objects.filter(competitor_id=OuterRef('pk')).order_by('-competition__date')
    vals = org.competitor_set.filter(name__icontains=partial_name) \
              .annotate(club_name=Subquery(entries.values('club__name')[:1]))[:MAX_AUTOCOMPLETE_RESPONSES] \
              .values('club_name', 'license_number', 'name')
    return JsonResponse({'competitors': list(vals)})


@login_required
def join_organisation(request, org):
    """create organisation memberships

        :param request: expecting POST parameters:\n
            :param int user_id: id of the user to create a membership for
        :param Organisation org: organisation the application is for
    """
    user = get_object_or_404(User, pk=request.POST['user_id'])
    if user == request.user or request.user.has_perm('main.manage_organisation', org):
        if request.user.has_perm('main.manage_organisation', org):
            org.organisationmembership_set.update_or_create(user=user, state=OrganisationMembership.DT)
        else:
            org.organisationmembership_set.update_or_create(user=user, state=OrganisationMembership.APPLICANT)
        return api_success()
    else:
        return JsonResponse({'success': False, 'reason': 'InsufficientPermissions'}, status=403)


@login_required
@permission_required_json('main.manage_organisation', fn=direct_object)
def accept_application(request, org):
    """Allows an organisation manager to accept applications to join an org

    :param request: expecting POST parameters:\n
        :param int user_id: id of the user who's application is being accepted
    :param Organisation org: organisation the application is for
    """
    user_id = request.POST['user_id']
    membership = get_object_or_404(OrganisationMembership, user_id=user_id, organisation=org)
    if membership.state == OrganisationMembership.APPLICANT:
        membership.state = OrganisationMembership.DT
        membership.save()
        return api_success()
    else:
        return api_failure("already_full_member", _("User is already a full member"))
