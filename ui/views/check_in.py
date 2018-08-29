from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from rules.contrib.views import permission_required, objectgetter
from main.models import Competition, Entry


@login_required
@permission_required('main.manage_competition',
                     fn=objectgetter(Competition, attr_name='comp_id', field_name='pk'),
                     raise_exception=True)
def check_in(request, org_slug, comp_id):
    competition = get_object_or_404(Competition, pk=comp_id)
    entries = competition.entry_set.order_by('competitor__name').all()
    return render(request, 'ui/competition/check_in.html', {'competition': competition,
                                                            'entries': entries})
