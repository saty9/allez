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
            return render(request, 'ui/stages/NOT_STARTED/pool_manage.html', {'ready_to_progress': ready_to_progress,
                                                                              'fencer_count': count,
                                                                              'max_pool_size': MAX_POOL_SIZE,
                                                                              'stage': pool.stage})
        else:
            return HttpResponse("Pools must have an add fencers stage somewhere before them")
        pass # TODO: Menu for selecting how many pools/ of what size
    elif state == Stage.READY:
        pass  # TODO: Menu for reorganising pools after initial generation and GO button
    elif state == Stage.STARTED:
        pass  # TODO: some variant on pool_edit.html
    # TODO this should load a different template depending on the stages state with one for generating tables another for rearanging and confirming and another for adding results