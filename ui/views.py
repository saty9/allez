from django.shortcuts import render
from main.models import Pool


def test(request):
    context = {'pool': Pool.objects.first().poolentry_set.all()}
    return render(request, 'ui/pool_edit.html', context)
