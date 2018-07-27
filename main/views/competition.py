from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from main.helpers.permissions import permission_required_json, direct_object
from main.models import Competition, Stage


def competition(request, comp_id):
    comp = get_object_or_404(Competition, pk=competition_id)
    if request.method == "POST":
        r_type = request.POST['type']
        if r_type == "add_stage":
            return add_stage(request, comp)


@permission_required_json('main.change_pool', fn=direct_object)
def add_stage(request, comp):
    """add a stage to a competition incrementing other stages numbers
    POST parameters:
    number: number of the stage to add a stage after
    type: type of stage to add"""
    number = request.POST['number']
    if comp.stage_set.exists():
        stage = get_object_or_404(Stage, competition=comp, number=number)
        if stage.appendable_to():
            stages = comp.stage_set.filter(number__gt=number).order_by('-number').all()
            for stage in stages:
                stage.number += 1
                stage.save()
            if comp.stage_set.create(number=number + 1, type=request['type'], state=Stage.NOT_STARTED):
                out = {'success': True}
                return JsonResponse(out)
            else:
                out = {'success': False,
                       'reason': 'Error creating stage'}
                return JsonResponse(out)
        else:
            out = {'success': False,
                   'reason': 'Stage cannot be appended to'}
            return JsonResponse(out)
    else:
        if comp.stage_set.create(type=request.POST['type'], number=0):
            out = {'success': True}
            return out
        else:
            out = {'success': False,
                   'reason': 'Error creating stage'}
            return out
