from django.http import HttpResponse
from django.utils.translation import gettext as _
from main.helpers.permissions import permission_required_json, direct_object
from main.models import Stage
from main.utils.api_responses import api_failure, api_success


def manage_cull_stage(request, stage):
    if request.method == "POST":
        return manage_cull_stage_post(request, stage)
    return HttpResponse("not implemented")


@permission_required_json('main.manage_competition', fn=direct_object)
def manage_cull_stage_post(request, stage):
    r_type = request.POST['type']
    if r_type == 'set_cull_level':
        return set_cull_level(request, stage)
    elif r_type == 'confirm_cull':
        return confirm_cull(request, stage)
    else:
        return api_failure('unrecognised request')


def set_cull_level(request, stage: Stage):
    """set what level a cull should happen from

    :param request: expecting POST parameters:\n
        cull_number: value to set CullStage.number at
    :param stage: Stage of type cull to set
    :return: JSONResponse with either success or an error message
    """
    cull_stage = stage.cullstage_set.first()
    if stage.state == Stage.NOT_STARTED:
        try:
            input_size = len(stage.input())
        except Stage.NotCompleteError:
            return api_failure("previous stage incomplete")
        number = int(request.POST['cull_number'])
        if 2 < number < input_size:
            cull_stage.number = number
            stage.state = Stage.READY
            cull_stage.save()
            stage.save()
            return api_success()
        else:
            return api_failure("invalid cull number",
                               "cull number must be > 2 and < size of stages input ")

    else:
        return api_failure("incorrect state",
                    "stage not in ready state")


def confirm_cull(request, stage: Stage):
    """confirm a cull

    :param request: no additional parameters
    :param stage: Stage of type cull to set
    :return: JSONResponse with either success or an error message
    """
    cull_stage = stage.cullstage_set.first()
    if stage.state == Stage.NOT_STARTED:
        return api_failure('number not set')
    elif stage.state == Stage.READY:
        stage.state = Stage.FINISHED
        stage.save()
        return api_success()
    else:
        return api_failure("stage already complete")
