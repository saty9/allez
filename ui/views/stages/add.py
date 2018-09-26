from django.shortcuts import get_object_or_404, render
from main.models import Stage, AddStage, Entry


def manage_add_stage(request, add_stage_id):
    add = get_object_or_404(AddStage, pk=add_stage_id)
    state = add.stage.state
    if state == Stage.NOT_STARTED:
        context = {'stage': add.stage,
                   'possible_additions': add.possible_additions().order_by('seed')}
        return render(request, 'ui/stages/add/NOT_STARTED.html', context)
    elif state == Stage.READY:
        entries = Entry.objects.filter(addcompetitor__stage=add).order_by('addcompetitor__sequence').all()
        context = {'stage': add.stage,
                   'entries': entries}
        return render(request, 'ui/stages/add/READY.html', context)
    else:
        entries = add.ordered_competitors()
        currently_not_added = list(Entry.objects.filter(addcompetitor__stage=add).order_by('addcompetitor__sequence').all())
        currently_not_added = [x for x in currently_not_added if x  not in entries]
        context = {'stage': add.stage,
                   'entries': entries,
                   'not_being_added': currently_not_added}
        return render(request, 'ui/stages/add/FINISHED.html', context)
