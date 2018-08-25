from django.http import JsonResponse
from django.utils.translation import gettext as _
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
    elif r_type == 'finish_stage':
        return finish_stage(request, stage)
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


def finish_stage(request, stage: Stage) -> JsonResponse:
    """mark a finished de_stage as finished is it is complete"""
    if stage.state != Stage.STARTED:
        return api_failure("invalid state",
                           _("Stage not currently running"))
    de_stage = stage.destage_set.first()  # type: DeStage
    if de_stage.detable_set.filter(complete=False).exists():
        return api_failure('stage not finished',
                           _('Stage not finished'))
    stage.state = Stage.FINISHED
    stage.save()
    return api_success()
