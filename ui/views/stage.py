from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rules.contrib.views import permission_required, objectgetter
from main.models import Stage
from .stages import manage_pool_stage, manage_cull_stage


@login_required
@permission_required('main.manage_competition', fn=objectgetter(Stage, attr_name='stage_id', field_name='pk'))
def manage_stage_router(request, org_slug, comp_id, stage_id):
    stage = get_object_or_404(Stage, pk=stage_id)
    if stage.type == Stage.POOL:
        pool_id = stage.poolstage_set.first().id
        return manage_pool_stage(request, pool_id)
    elif stage.type == Stage.CULL:
        cull_id = stage.cullstage_set.first().id
        return manage_cull_stage(request, cull_id)
    else:
        return HttpResponse("Not Implemented yet")

