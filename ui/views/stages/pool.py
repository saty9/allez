from django.shortcuts import get_object_or_404
from main.models import PoolStage


def manage_pool_stage(request, pool_stage_id):
    pool = get_object_or_404(PoolStage, pk=pool_stage_id)