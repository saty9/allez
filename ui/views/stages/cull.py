from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext as _
from math import log2
from main.models import CullStage, Stage


def manage_cull_stage(request, cull_stage_id):
    cull = get_object_or_404(CullStage, pk=cull_stage_id)
    state = cull.stage.state
    if state == Stage.NOT_STARTED:
        context = {'stage': cull.stage}
        try:
            input_size = len(cull.stage.input())
            context['fencer_count'] = input_size
            pow_2 = int(log2(input_size))
            if 2 ** pow_2 == input_size:
                context['default_cull'] = 2 ** (int(log2(input_size)) - 1)
            else:
                context['default_cull'] = 2 ** int(log2(input_size))

        except Stage.NotCompleteError:
            return HttpResponse(_("Previous stage not complete"))
        return render(request, 'ui/stages/cull/NOT_STARTED.html', context)
    elif state == Stage.READY:
        context = {'stage': cull.stage}
        try:
            survivors = cull.stage.ordered_competitors()
            culled = [e for e in cull.stage.input() if e not in survivors]
            context['survivors'] = survivors
            context['culled'] = culled
        except Stage.NotCompleteError:
            return HttpResponse(_("Previous stage not complete"))
        return render(request, 'ui/stages/cull/READY.html', context)
    else:
        context = {'stage': cull.stage}
        try:
            survivors = cull.stage.ordered_competitors()
            culled = [e for e in cull.stage.input() if e not in survivors]
            context['survivors'] = survivors
            context['culled'] = culled
        except Stage.NotCompleteError:
            return HttpResponse(_("Previous stage not complete"))
        return render(request, 'ui/stages/cull/FINISHED.html', context)
