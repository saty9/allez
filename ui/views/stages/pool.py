from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from main.models import PoolStage, Stage
from main.settings import MAX_POOL_SIZE


def manage_pool_stage(request, pool_stage_id):
    pool = get_object_or_404(PoolStage, pk=pool_stage_id)
    state = pool.stage.state
    if state == Stage.NOT_STARTED:
        previous = pool.stage.competition.stage_set.filter(number=pool.stage.number - 1)
        if previous.exists():
            previous = previous.first()
            ready_to_progress = previous.state in [Stage.FINISHED, Stage.LOCKED]
            count = 0
            if ready_to_progress:
                count = len(previous.ordered_competitors())
            return render(request, 'ui/stages/pool/NOT_STARTED.html', {'ready_to_progress': ready_to_progress,
                                                                       'fencer_count': count,
                                                                       'max_pool_size': MAX_POOL_SIZE,
                                                                       'stage': pool.stage})
        else:
            return HttpResponse("Pools must have an add fencers stage somewhere before them")
    elif state == Stage.READY:
        pools = pool.pool_set.all()
        return render(request, 'ui/stages/pool/READY.html', {'pools': pools,
                                                             'stage_id': pool.stage.id})
    elif state == Stage.STARTED:
        pools = pool.pool_set.all()
        all_completed = all(map(lambda x: x.complete(), pools))
        return render(request, 'ui/stages/pool/STARTED.html', {'stage': pool.stage,
                                                               'pools': pools,
                                                               'all_completed': all_completed})
    else:
        pools = pool.pool_set.all().order_by('number')
        return render(request, 'ui/stages/pool/FINISHED.html', {'stage': pool.stage,
                                                                'pools': pools})


def dt_manage_pool(request, pool_id):
    return render(request, 'ui/stages/pool/dt_pool_edit.html', {'pool_id': pool_id})
