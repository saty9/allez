from django.http import HttpResponse
from django.utils.translation import gettext as _
from main.helpers.permissions import permission_required_json, direct_object
from main.models import Stage
from main.utils.api_responses import api_failure, api_success


def manage_add_stage(request, stage):
    if request.method == "POST":
        return manage_add_stage_post(request, stage)
    return HttpResponse("not implemented")


@permission_required_json('main.manage_competition', fn=direct_object)
def manage_add_stage_post(request, stage):
    r_type = request.POST['type']
    if r_type == 'add_entries':
        return add_entries(request, stage)
    elif r_type == "confirm_add":
        return confirm_add(stage)
    else:
        return api_failure('unrecognised request')


def add_entries(request, stage: Stage):
    """add entries and set stage as ready
    entries will be ordered according to their seed

    :param request: expecting POST parameters:\n
        :param list of int ids: list of entry ids to add
    :param stage: Stage of type add
    :return: JSONResponse with either success or an error message
    """
    add_stage = stage.addstage_set.first()
    if stage.state != Stage.NOT_STARTED:
        return api_failure("incorrect state",
                           _("Stage not in NOT_STARTED state"))
    ids = request.POST.getlist('ids')
    entries = stage.competition.entry_set.filter(pk__in=ids)
    if len(entries) != len(ids) or not set(entries.all()).issubset(add_stage.possible_additions()):
        return api_failure('bad_entry', _('one of these entries has already been added or is not in this competition'))
    add_stage.add_entries(entries.order_by('seed', '?'))
    stage.state = Stage.READY
    stage.save()
    return api_success()


def confirm_add(stage: Stage):
    """advances a stage from READY -> FINISHED

    :param request: expects type: "confirm_add"
    :param stage: Stage of type add
    :return: JSONResponse with either success or an error message
    """
    if stage.state != Stage.READY:
        return api_failure("incorrect state",
                           _("Stage not in READY state"))
    stage.state = Stage.FINISHED
    stage.save()
    return api_success()
