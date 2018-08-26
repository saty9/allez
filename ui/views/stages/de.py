from django.db.models import F
from operator import itemgetter
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from rules.contrib.views import permission_required, objectgetter

from main.models import DeStage, Stage, DeTable


def manage_de_stage(request, de_stage_id):
    de = get_object_or_404(DeStage, pk=de_stage_id)
    state = de.stage.state
    if state == Stage.NOT_STARTED:
        previous = de.stage.competition.stage_set.get(number=de.stage.number - 1)
        if previous.state not in [Stage.FINISHED, Stage.LOCKED]:
            return HttpResponse("Previous stage not finished")
        return render(request, 'ui/stages/de/NOT_STARTED.html', {'stage': de.stage})
    elif state in [Stage.STARTED, Stage.FINISHED, Stage.LOCKED]:
        context = {'stage': de.stage}
        tables = list(de.detable_set.all())
        main_series = list(filter(lambda x: x.max_rank() <= 3, tables))
        others = [x for x in tables if x not in main_series]
        main_series = [(x, x.max_rank(), x.detableentry_set.count(), x.children.exists()) for x in main_series]
        main_series = sorted(main_series, key=itemgetter(2, 1))
        others = map(lambda x: (x, x.max_rank(), x.detableentry_set.count(), x.children.exists()), others)
        others = filter(lambda x: not x[0].automated(), others)
        others = sorted(others, key=itemgetter(2, 1))
        context['main_series'] = main_series
        context['others'] = others
        context['complete'] = not de.detable_set.filter(complete=False).exists()
        return render(request, 'ui/stages/de/STARTED.html', context)
    else:
        return HttpResponse("Not Implemented", status=404)


@login_required
@permission_required('main.manage_competition', fn=objectgetter(DeTable, 'de_table_id'))
def dt_manage_de_table(request, de_table_id):
    de_table = get_object_or_404(DeTable, pk=de_table_id)
    context = {'table': de_table,
               'comp': de_table.de.stage.competition}
    entries = de_table.detableentry_set.order_by('table_pos').annotate(seed=F('entry__deseed__seed')).all()
    if not de_table.complete:
        context['ready'] = all(map(lambda x: x.victory or x.against().victory, entries))
    return render(request, 'ui/stages/de/dt_single_round_de_edit.html', context=context)
