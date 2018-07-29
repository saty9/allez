from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from main.models import Organisation, OrganisationMembership


@login_required
def change_org(request):
    if request.method == "GET":
        user_organisations = request.user.organisationmembership_set.all()
        context = {
            'user_orgs': user_organisations,
            'orgs': Organisation.objects.values('name', 'id')
        }
        return render(request, 'ui/user/change_org.html', context)
    elif request.method == "POST":
        id = request.POST['org_id']
        org = Organisation.objects.get(id=id)
        query = OrganisationMembership.objects.filter(organisation=org, user=request.user)
        if query.exists():
            query.update(last_active=timezone.now())
            request.session['org_id'] = id
            slug = org.slug
            return JsonResponse({'success': True,
                                 'next': reverse('ui/org/competitions', kwargs={'org_slug': slug})})
        else:
            return JsonResponse({'success': False,
                                 'reason': 'User not a member of given organisation'})
