from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from main.helpers.permissions import permission_required_json, direct_object
from main.models import Pool, Stage, PoolBout
from main.utils.api_responses import api_failure


def pool(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)
    if request.method == "POST":
        return update_pool(request, pool)
    else:
        entry_data = list(pool.poolentry_set.values('id', 'number', name=F('entry__competitor__name')).all())
        bouts_data = list(PoolBout.objects.filter(fencerA__in=pool.poolentry_set.all())
                          .values().all())
        return JsonResponse({'entries': entry_data, 'bouts': bouts_data})


@permission_required_json('main.change_pool', fn=direct_object)
def update_pool(request, pool):
    """handles POST requests to update pools"""
    if pool.stage.stage.state != Stage.STARTED:
        return JsonResponse({'success': False, 'reason': 'stage not currently running'})
    else:
        r_type = request.POST['type']
        if r_type == 'bout_result':
            e1 = pool.poolentry_set.get(pk=request.POST['entry_1'])
            e2 = pool.poolentry_set.get(pk=request.POST['entry_2'])
            e1_victory = bool(int(request.POST['e1_victory']))
            e1_score = int(request.POST['e1_score'])
            e2_score = int(request.POST['e2_score'])
            if (e1_victory and e2_score > e1_score) or (not e1_victory and e2_score < e1_score):
                return api_failure('score victory mismatch')
            e1.fencerA_bout_set.update_or_create(fencerB=e2, defaults={'scoreA': e1_score,
                                                                       'victoryA': e1_victory})
            e2.fencerA_bout_set.update_or_create(fencerB=e1, defaults={'scoreA': e2_score,
                                                                       'victoryA': not e1_victory})
            return JsonResponse({'success': True, 'pool_complete': pool.complete()})
    return JsonResponse({'success': False, 'reason': 'unable to understand post'})

