from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from rules.contrib.views import permission_required, objectgetter
from main.models import Competition, Organisation, Stage
from ..forms.competition import CreateCompetitionForm


@login_required
@permission_required('main.create_competition', fn=objectgetter(Organisation, attr_name='org_slug', field_name='slug'))
def create_competition(request, org_slug):
    org = get_object_or_404(Organisation, slug=org_slug)
    if request.method == 'POST':
        form = CreateCompetitionForm(request.POST)
        if form.is_valid():
            comp = org.competition_set.create(name=form.cleaned_data['name'], date=form.cleaned_data['date'])

            return HttpResponseRedirect(reverse('ui/manage_competition', args=[org_slug, comp.id]))
    else:
        form = CreateCompetitionForm()

    return render(request, 'ui/competition/create.html', {'form': form})


def list_competitions(request, org_slug):
    org = get_object_or_404(Organisation, slug=org_slug)
    comps = org.competition_set.all()
    return render(request, 'ui/competition/list.html', {'competitions': comps})


@login_required
@permission_required('main.manage_competition',
                     fn=objectgetter(Competition, attr_name='comp_id', field_name='pk'),
                     raise_exception=True)
def manage_competition(request, org_slug, comp_id):
    competition = get_object_or_404(Competition, pk=comp_id)
    stages_objects = competition.stage_set.order_by('number').all()
    style_map = {
        Stage.STARTED: 'table-primary',
        Stage.FINISHED: 'table-success',
        Stage.LOCKED: 'table-success'
    }
    styles = list(map(lambda x: style_map.get(x.state, ''), stages_objects))
    stages = zip(stages_objects, styles)
    types = Stage.stage_types
    entries = competition.entry_set.all()
    return render(request, 'ui/competition/manage.html', {'competition': competition,
                                                          'stages': stages,
                                                          'types': types,
                                                          'entries': entries,
                                                          'org_slug': org_slug})
