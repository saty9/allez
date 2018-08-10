from main.models import Stage
from main.utils.api_responses import api_failure, api_success
from main.settings import MAX_POOL_SIZE
from math import ceil


def manage_pool_stage(request, stage):
    pool_stage = stage.poolstage_set.first()
    if request.method == "POST":
        r_type = request.POST['type']
        if r_type == 'generate_pools':
            previous = Stage.objects.get(competition=stage.competition, number=stage.number - 1)
            if stage.state == stage.NOT_STARTED:
                if previous.state in [Stage.FINISHED, Stage.LOCKED]:
                    number = int(request.POST['number_of_pools'])
                    entry_count = len(previous.ordered_competitors())
                    if entry_count / number >= 3.0 and ceil(entry_count/number) <= MAX_POOL_SIZE:
                        pool_stage.start(number)
                        stage.state = Stage.READY
                        stage.save()
                        return api_success()
                    else:
                        return api_failure('produces pools with less than 3 or more than ' + MAX_POOL_SIZE + ' fencers')
                else:
                    return api_failure('previous stage not completed yet')
            else:
                return api_failure('this stage has already generated pools')
        else:
            return api_failure('unrecognised request')
