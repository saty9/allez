import csv
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from main.helpers.permissions import permission_required_json, direct_object
from main.models import Competition, Stage, Club, Competitor


def competition(request, comp_id):
    comp = get_object_or_404(Competition, pk=comp_id)
    if request.method == "POST":
        r_type = request.POST['type']
        if r_type == "add_stage":
            return add_stage(request, comp)
        elif r_type == "delete_stage":
            return delete_stage(request, comp)
        elif r_type == "entry_csv":
            return entry_csv(request, comp)
        else:
            out = {'success': False,
                   'reason': 'post type not recognised'}
            return JsonResponse(out)


@permission_required_json('main.manage_competition', fn=direct_object)
def add_stage(request, comp):
    """add a stage to a competition incrementing other stages numbers
    POST parameters:
    number: number of the stage to add a stage after
    type: type of stage to add"""
    number = int(request.POST['number'])
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
                out = {'success': False,
                       'reason': 'Error creating stage'}
                return JsonResponse(out)
        else:
            out = {'success': False,
                   'reason': 'Stage cannot be appended to'}
            return JsonResponse(out)
    else:
        if comp.stage_set.create(type=request.POST['stage_type'], number=0):
            out = {'success': True}
            return JsonResponse(out)
        else:
            out = {'success': False,
                   'reason': 'Error creating stage'}
            return JsonResponse(out)


@permission_required_json('main.manage_competition', fn=direct_object)
def delete_stage(request, comp):
    stage_id = request.POST['id']
    stage = get_object_or_404(Stage, competition=comp, pk=stage_id)
    if stage.deletable():
        number = stage.number
        if stage.delete():
            stages = comp.stage_set.filter(number__gt=number).order_by('number')
            for stage in stages:
                stage.number -= 1
                stage.save()
            out = {'success': True}
            return JsonResponse(out)
        else:
            out = {'success': False,
                   'reason': 'Failed to delete stage'}
            return JsonResponse(out)
    else:
        out = {'success': False,
               'reason': 'Stage not deletable'}
        return JsonResponse(out)


@permission_required_json('main.manage_competition', fn=direct_object)
def entry_csv(request, comp):
    """adds entries to a competition based on a csv file following the format:
    name, club name, license number"""
    expected_columns = 3
    if comp.entry_set.exists():
        out = {'success': False,
               'reason': 'Competition already has entries'}
        return JsonResponse(out)
    else:
        file = request.FILES['file']
        data = [row for row in csv.reader(file.read().decode("utf-8").splitlines())]
        if not data or any(map(lambda x: len(x) != expected_columns, data)):
            out = {'success': False,
                   'reason': 'unexpected number of rows/columns'}
            return JsonResponse(out)
        else:
            org_competitiors = comp.organisation.competitor_set
            for new_entry in data:
                query = org_competitiors.filter(license_number=new_entry[2])
                if query.exists():
                    competitor = query.first()
                else:
                    name = new_entry[1]
                    club = Club.objects.filter(name=name)
                    if club.exists():
                        club = club.first()
                    else:
                        name = Club.simplify_name(new_entry[1])
                        club = Club.objects.filter(name__icontains=name)
                        if club.exists():
                            club = club.first()
                        else:
                            club = Club.objects.create(name=new_entry[1])
                    competitor = org_competitiors.create(name=new_entry[0], license_number=new_entry[2])
                comp.entry_set.create(competitor=competitor, club=club)
            out = {'success': True,
                   'added_count': len(data)}
            return JsonResponse(out)
