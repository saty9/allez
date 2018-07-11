from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from main.models import Pool, Stage
from rules.contrib.views import permission_required
import logging


def pool(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)
    if request.method == "POST":
        return update_pool(request, pool)
    else:
        pass


@permission_required('main.change_pool')
def update_pool(request, pool):
    """handles POST requests to update pools"""
    if pool.stage.stage.state != Stage.STARTED:
        return JsonResponse({'success': False, 'reason': 'Stage not currently running'})
    else:
        r_type = request.POST['type']
        if r_type == 'bout_result':
            e1 = pool.poolentry_set.get(pk=request.POST['entry_1'])
            e2 = pool.poolentry_set.get(pk=request.POST['entry_2'])
            e1_victory = bool(int(request.POST['e1_victory']))
            e1_score = int(request.POST['e1_score'])
            e2_score = int(request.POST['e2_score'])
            if (e1_victory and e2_score > e1_score) or (not e1_victory and e2_score < e1_score):
                return JsonResponse({'success': False, 'reason': 'Bad Input (score victory mismatch)'})
            e1.fencerA_bout_set.update_or_create(fencerB=e2, defaults={'scoreA': e1_score,
                                                                       'victoryA': e1_victory})
            e2.fencerA_bout_set.update_or_create(fencerB=e1, defaults={'scoreA': e2_score,
                                                                       'victoryA': not e1_victory})
            return JsonResponse({'success': True, 'pool_complete': pool.complete()})
    logger = logging.getLogger(__name__)
    logger.error("Couldn't parse POST:{} to {}".format(request.POST, request.path))
    return JsonResponse({'success': False, 'reason': 'Unable to understand post'})

