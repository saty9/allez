from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from rules.contrib.views import permission_required, objectgetter
from main.models import Competition, Organisation
from ..forms.competition import CreateCompetitionForm


@login_required
@permission_required('main.create_competition', fn=objectgetter(Organisation, attr_name='org_slug', field_name='slug'))
def create_competition(request, org_slug):
    org = get_object_or_404(Organisation, slug=org_slug)
    if request.method == 'POST':
        form = CreateCompetitionForm(request.POST)
        if form.is_valid():
            comp = org.competition_set.create(name=form.cleaned_data['name'], date=form.cleaned_data['date'])

            return HttpResponseRedirect(reverse('competition', args=[org_slug, comp.id]))
    else:
        form = CreateCompetitionForm()

    return render(request, 'ui/competition/create.html', {'form': form})