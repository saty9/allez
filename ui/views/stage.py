from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext as _
from rules.contrib.views import permission_required, objectgetter
from main.models import Stage
from .stages import manage_pool_stage, manage_cull_stage, manage_de_stage, manage_add_stage


@login_required
@permission_required('main.manage_competition',
                     fn=objectgetter(Stage, attr_name='stage_id', field_name='pk'),
                     raise_exception=True)
def manage_stage_router(request, org_slug, comp_id, stage_id):
    stage = get_object_or_404(Stage, pk=stage_id)
    if stage.type == Stage.POOL:
        pool_id = stage.poolstage_set.first().id
        return manage_pool_stage(request, pool_id)
    elif stage.type == Stage.CULL:
        cull_id = stage.cullstage_set.first().id
        return manage_cull_stage(request, cull_id)
    elif stage.type == Stage.DE:
        de_id = stage.destage_set.first().id
        return manage_de_stage(request, de_id)
    elif stage.type == Stage.ADD:
        add_id = stage.addstage_set.first().id
        return manage_add_stage(request, add_id)
    else:
        return HttpResponse("Not Implemented yet")


def stage_ranking(request, org_slug, comp_id, stage_id):
    stage = get_object_or_404(Stage, pk=stage_id, competition=comp_id)
    try:
        stage_rankings = stage.ranked_competitors()
    except Stage.NotCompleteError:
        return HttpResponse(_("Stage Not Finished"))
    rankings = []
    place = 1
    for rank in stage_rankings:
        for entry in rank:
            rankings.append((place, entry))
        place += len(rank)
    return render(request, 'ui/competition/ranking.html', context={'stage': stage,
                                                                   'rankings': rankings})

