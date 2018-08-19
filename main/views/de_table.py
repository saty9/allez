from django.shortcuts import get_object_or_404
from main.helpers.permissions import permission_required_json, direct_object
from main.models import DeTable, Stage
from main.utils.api_responses import api_failure, api_success


def de_table(request, table_id):
    table = get_object_or_404(DeTable, pk=table_id)
    if request.method == "POST":
        rtype = request.POST['type']
        if rtype == 'add_result':
            return add_result(request, table)
        else:
            return api_failure('unrecognised request')
    else:

        return api_failure('not implemented')


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
    if (e1_victory and e2_score > e1_score) or (not e1_victory and e2_score < e1_score):
        return api_failure('score victory mismatch')
    e1.victory = e1_victory
    e1.score = e1_score
    e2.victory = not e1_victory
    e2.score = e2_score
    e1.save()
    e2.save()
    return api_success()


