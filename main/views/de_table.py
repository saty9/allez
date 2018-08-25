from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from main.helpers.permissions import permission_required_json, direct_object
from main.models import DeTable, Stage
from main.models.de_table import UnfinishedTableException
from main.utils.api_responses import api_failure, api_success


def de_table(request, table_id):
    table = get_object_or_404(DeTable, pk=table_id)
    if request.method == "POST":
        rtype = request.POST['type']
        if rtype == 'add_result':
            return add_result(request, table)
        elif rtype == 'table_complete':
            return mark_table_complete(request, table)
        else:
            return api_failure('unrecognised request')
    else:
        return get_bouts(table)


def get_bouts(table):
    entries = table.detableentry_set.order_by('table_pos').annotate(seed=F('entry__deseed__seed')).\
        values('id', 'entry_id', 'score', 'victory', 'seed', 'entry__competitor__name', 'entry__competitor__club__name')
    bouts = []
    x = 0
    while x < len(entries):
        bouts.append({'e0': entries[x], 'e1': entries[x + 1]})
        x += 2
    return JsonResponse({'bouts': bouts})


def add_result(request, table):
    """add a result to  a de table

    :param request: expecting POST parameters:\n
        :int entryA: detableentry id of the first entry the results pertain to
        :int entryB: detableentry id of the second entry the results pertain to
        :int scoreA: first entries score
        :int scoreB: second entries score
        :bool  victoryA: boolean indicating if first entry won. If false 2nd is assumed to have won
    :param DeTable table: table these results are from
    :return:
    """
    if table.de.stage.state != Stage.STARTED:
        return api_failure('incorrect state', 'stage not currently running')
    if table.children.exists():
        return api_failure('child_exists', _('Cannot add results after next round of tables made'))
    if table.complete:
        return api_failure('table_complete', _('This table has already been marked as complete'))
    e1_id = request.POST['entryA']
    e2_id = request.POST['entryB']
    e1 = table.detableentry_set.get(pk=e1_id)
    e2 = table.detableentry_set.get(pk=e2_id)
    e1_victory = bool(int(request.POST['victoryA']))
    e1_score = int(request.POST['scoreA'])
    e2_score = int(request.POST['scoreB'])
    return do_add_result(request, e1, e2, e1_score, e2_score, e1_victory)


@permission_required_json('main.change_de_table_entry', fn=direct_object)
def do_add_result(request, e1, e2, e1_score, e2_score, e1_victory):
    if e1.against() != e2:
        return api_failure('bad entry pair', "these entries aren't fighting each other this round")
    if (e1.entry is None and e1_victory) or (e2.entry is None and not e1_victory):
        return api_failure('bye_victory', _('Byes cannot win a match'))
    if (e1_victory and e2_score > e1_score) or (not e1_victory and e2_score < e1_score):
        return api_failure('score victory mismatch')
    e1.victory = e1_victory
    e1.score = e1_score
    e2.victory = not e1_victory
    e2.score = e2_score
    e1.save()
    e2.save()
    return api_success()


@permission_required_json('main.manage_competition', fn=direct_object)
def mark_table_complete(request, table):
    if table.complete:
        return api_failure('already_complete', _("This table is already marked as complete"))
    if table.detableentry_set.count() == 2:
        table.complete = True
        table.save()
        return api_success()
    try:
        table.make_children()
        return api_success()
    except UnfinishedTableException:
        return api_failure('incomplete_bouts', _('One or more bouts incomplete'))


