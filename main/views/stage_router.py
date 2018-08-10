from main.models import Stage
from django.shortcuts import get_object_or_404
from .stage_pool import pools, pools_pdf, results, results_pdf
from .manage_pool_stage import manage_pool_stage


def stage_router(request, stage_id):
    stage = get_object_or_404(Stage, pk=stage_id)
    if stage.type == Stage.POOL:
        return manage_pool_stage(request, stage)


def stage_router_pdf(request, comp_id, stage_number):
    stage = get_object_or_404(Stage, competition_id=comp_id, number=stage_number)
    if stage.type == Stage.POOL:
        return pools_pdf(request, stage)


def stage_router_results(request, comp_id, stage_number):
    stage = get_object_or_404(Stage, competition_id=comp_id, number=stage_number)
    if stage.type == Stage.POOL:
        return results(request, stage)


def stage_router_results_pdf(request, comp_id, stage_number):
    stage = get_object_or_404(Stage, competition_id=comp_id, number=stage_number)
    if stage.type == Stage.POOL:
        return results_pdf(request, stage)

