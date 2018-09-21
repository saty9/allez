import json
from django.utils.translation import gettext as _
from main.helpers.permissions import permission_required_json, direct_object
from main.models import Stage
from main.utils.api_responses import api_failure, api_success
from main.settings import MAX_POOL_SIZE
from math import ceil


def manage_pool_stage(request, stage):
    if request.method == "POST":
        r_type = request.POST['type']
        if r_type == 'generate_pools':
            return generate_pools(request, stage)
        elif r_type == "confirm_pools":
            return confirm_pools(request, stage)
        elif r_type == 'finish_stage':
            return finish_stage(request,stage)
        else:
            return api_failure('unrecognised request')


@permission_required_json('main.manage_competition', fn=direct_object)
def generate_pools(request, stage):
    pool_stage = stage.poolstage_set.first()
    previous = Stage.objects.get(competition=stage.competition, number=stage.number - 1)
    if stage.state != stage.NOT_STARTED:
        return api_failure("incorrect state",
                           _('this stage has already generated pools'))
    if previous.state not in [Stage.FINISHED, Stage.LOCKED]:
        return api_failure('previous stage not completed yet')
    number = int(request.POST['number_of_pools'])
    entry_count = len(previous.ordered_competitors())
    if entry_count / number >= 3.0 and ceil(entry_count / number) <= MAX_POOL_SIZE:
        pool_stage.start(number)
        stage.state = Stage.READY
        stage.save()
        return api_success()
    else:
        return api_failure("invalid pool size",
                           _('produces pools with less than 3 or more than %(max_pool_size)i fencers') %
                           {'max_pool_size': MAX_POOL_SIZE})


@permission_required_json('main.manage_competition', fn=direct_object)
def confirm_pools(request, stage):
    pool_stage = stage.poolstage_set.first()
    if stage.state != Stage.READY:
        return api_failure("incorrect state",
                           _("Stage not in ready state"))
    if 'pools' not in request.POST:
        stage.state = Stage.STARTED
        stage.save()
        return api_success()
    original_pools = pool_stage.pool_set.all()
    pools = json.loads(request.POST['pools'])
    if len(pools) != len(original_pools):
        return api_failure("pool count mismatch",
                           _("Number of pools submitted does not match number of pools in this round"))
    original_competitors_ids = set()
    [original_competitors_ids.update(x.poolentry_set.values_list('entry_id', flat=True)) for x in original_pools]
    competitors_ids = set()
    new_lengths = []
    for pool_num, entries in pools.items():
        competitors_ids.update(map(int, entries))
        new_lengths.append(len(entries))
    if competitors_ids != original_competitors_ids:
        return api_failure("pool entry mismatch",
                           _("Manipulation of entry ids detected"))
    if not (max(new_lengths) <= min(new_lengths) + 1):
        return api_failure("pool size difference",
                           _("Pools can differ in size by at most 1"))
    original_pools.delete()
    for index, pool in enumerate(pools.items()):
        new_pool = pool_stage.pool_set.create(number=index+1)
        for index, entry_id in enumerate(pool[1]):
            new_pool.poolentry_set.create(number=index+1, entry_id=int(entry_id))
    stage.state = Stage.STARTED
    stage.save()
    return api_success()


@permission_required_json('main.manage_competition', fn=direct_object)
def finish_stage(request, stage):
    pool_stage = stage.poolstage_set.first()
    if stage.state == Stage.STARTED:
        if all(map(lambda x: x.complete(), pool_stage.pool_set.all())):
            stage.state = Stage.FINISHED
            stage.save()
            return api_success()
        else:
            return api_failure('stage not finished')
    else:
        return api_failure("incorrect state",
                           "stage not currently running")
