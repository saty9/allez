from main.models import Stage
from django.shortcuts import get_object_or_404
from .stage_pool import pools, pools_pdf, seeding


def stage_router(request, comp_id, stage_number):
    stage = get_object_or_404(Stage, competition_id=comp_id, number=stage_number)
    if stage.type == Stage.POOL:
        return pools(request, Stage)


def stage_router_pdf(request, comp_id, stage_number):
    stage = get_object_or_404(Stage, competition_id=comp_id, number=stage_number)
    if stage.type == Stage.POOL:
        return pools_pdf(request, stage)


def stage_router_seeding(request, comp_id, stage_number):
    stage = get_object_or_404(Stage, competition_id=comp_id, number=stage_number)
    if stage.type == Stage.POOL:
        return seeding(request, stage)
