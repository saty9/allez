import csv
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from main.helpers.permissions import permission_required_json, direct_object
from main.models import Competition, Stage, Entry
from main.utils.api_responses import api_failure, api_success


# TODO add way of rolling back the most recently finished stage to correct results (set locked after next stage starts (Use on save))


def competition(request, comp_id):
    comp = get_object_or_404(Competition, pk=comp_id)
    if request.method == "POST":
        return handle_post(request, comp)
    else:
        return api_failure('not implemented')


@permission_required_json('main.manage_competition', fn=direct_object)
def handle_post(request, comp):
    r_type = request.POST['type']
    if r_type == "add_stage":
        return add_stage(request, comp)
    elif r_type == "delete_stage":
        return delete_stage(request, comp)
    elif r_type == "entry_csv":
        return entry_csv(request, comp)
    elif r_type == "check_in_all":
        return check_in_all(comp)
    elif r_type == "check_in":
        return check_in(request, comp)
    elif r_type == "add_entry":
        return add_entry(request, comp)
    else:
        out = {'success': False,
               'reason': 'post type not recognised'}
        return api_failure('unrecognised request', _('Unrecognised request'))


def add_stage(request, comp):
    """add a stage to a competition incrementing other stages numbers

    :param request: expecting POST parameters:\n
        :param int number: number of the stage to add a stage after
        :param str stage_type: type of stage to add
    :param Competition comp: competition to delete stage from
    :return:
    """
    number = int(request.POST['number'])
    stage_type = request.POST['stage_type']
    if stage_type not in map(lambda x: x[0], Stage.stage_types):
        return api_failure('bad_type', _('Failed to add stage: unrecognised stage type'))
    if comp.stage_set.exists():
        stage = get_object_or_404(Stage, competition=comp, number=number)
        if stage.appendable_to():
            stages = comp.stage_set.filter(number__gt=number).order_by('-number').all()
            for stage in stages:
                stage.number += 1
                stage.save()
            if comp.stage_set.create(number=number + 1, type=request.POST['stage_type'], state=Stage.NOT_STARTED):
                out = {'success': True}
                return JsonResponse(out)
            else:
                return api_failure('error_adding_stage', _('Failed to add stage'))
        else:
            out = {'success': False,
                   'reason': 'stage_unappendable_to',
                   'verbose_reason': _('Stage cannot be appended to')}
            return JsonResponse(out)
    else:
        if comp.stage_set.create(type=stage_type, number=0):
            return api_success()
        else:
            return api_failure('error_adding_stage', _('Failed to add stage'))


def delete_stage(request, comp):
    """delete a stage from the competition

    :param request: expecting POST parameters:\n
        :param int id: id of the stage to delete
    :param Competition comp: competition to delete stage from
    :return:
    """
    stage_id = request.POST['id']
    stage = get_object_or_404(Stage, competition=comp, pk=stage_id)
    if stage.deletable():
        number = stage.number
        if stage.delete():
            stages = comp.stage_set.filter(number__gt=number).order_by('number')
            for stage in stages:
                stage.number -= 1
                stage.save()
            return api_success()
        else:
            return api_failure('deletion_failure', _('Failed to delete stage'))
    else:
        return api_failure('stage_undeletable', 'Cannot delete this stage')


def entry_csv(request, comp):
    """adds entries to a competition and create an add stage

    :param request: expecting POST parameters:\n
        :param File file: a csv file following the format:
            name, club name, license number
    :param Competition comp: competition to add entries to
    :return:
    """
    expected_columns = 3
    file = request.FILES['file']
    data = [row for row in csv.reader(file.read().decode("utf-8").splitlines())]
    if not data or any(map(lambda x: len(x) != expected_columns, data)):
        return api_failure('row_column_error',
                           _('Unexpected number of rows/columns in uploaded file'))
    org_competitors = comp.organisation.competitor_set
    if comp.stage_set.exists():
        number = comp.stage_set.latest().number + 1
    else:
        number = 0
    add_stage = comp.stage_set.create(type=Stage.ADD, number=number)
    for new_entry in data:
        comp.add_entry(new_entry[2], new_entry[0], new_entry[1])
    out = {'success': True,
           'added_count': len(data)}
    return JsonResponse(out)


def check_in_all(comp):
    """ Check in all Un-Checked in entries of a competition

    :param Competition comp: Competition to check in entries for
    """
    comp.entry_set.filter(state=Entry.NOT_CHECKED_IN).update(state=Entry.CHECKED_IN)
    return api_success()


def check_in(request, comp):
    """ Check in a single entry

    :param request: expecting POST parameters:\n
        :param int id: id of the stage to delete
    :param comp: Competition to check in entry for
    :return:
    """
    entry = get_object_or_404(Entry, pk=request.POST['id'], competition=comp)
    if entry.state != Entry.NOT_CHECKED_IN:
        return api_failure('already_checked_in', _('That entry has already checked in'))
    entry.state = Entry.CHECKED_IN
    entry.save()
    return api_success()


def add_entry(request, comp):
    """ Manually add a single entry to a competition

        :param request: expecting POST parameters:\n
            :param str name: name of competitor to add
            :param str license_number: license number of the competitor to add
            :param str club_name: name of the club to enter competitor under
            :param optional bool check_in: if true checks in entry at same time
        :param Competition comp: Competition to enter competitor into
        :return:
    """
    entry = comp.add_entry(request.POST['license_number'], request.POST['name'], request.POST['club_name'])
    if 'check_in' in request.POST and request.POST['check_in']:
        entry.state = Entry.CHECKED_IN
        entry.save()
    return api_success()
