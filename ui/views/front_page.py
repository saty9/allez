from django.shortcuts import render


def front_page(request):
    return render(request, 'ui/front_page.html')