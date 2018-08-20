from django.http import JsonResponse
from main.helpers.permissions import permission_required_json, direct_object
from main.models import Stage, DeStage
from main.utils.api_responses import api_failure, api_success


def manage_de_stage(request, stage):
    if request.method == "POST":
        return manage_de_stage_post(request, stage)


@permission_required_json('main.manage_competition', fn=direct_object)
def manage_de_stage_post(request, stage):
    r_type = request.POST['type']
    if r_type == 'start_stage':
        return start_stage(request, stage)
    else:
        return api_failure('unrecognised request')


def start_stage(request, stage: Stage) -> JsonResponse:
    """start a not running de stage and generate its head table"""
    if stage.state != Stage.NOT_STARTED:
        return api_failure("invalid state",
                           "Stage has already started")
    de_stage = stage.destage_set.first()  # type: DeStage
    try:
        de_stage.start()
    except Stage.NotCompleteError:
        return api_failure('previous stage incomplete',
                           'Previous stage not finished yet')
    stage.state = Stage.STARTED
    stage.save()
    return api_success()
