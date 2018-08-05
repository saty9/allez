"""allez URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('hi', views.test),
    path('change_org/', views.change_org, name='ui/change_org'),
    path('<slug:org_slug>', views.organisation, name='ui/organisation/show'),
    path('<slug:org_slug>/competitions', views.list_competitions, name='ui/org/competitions'),
    path('<slug:org_slug>/competitions/create', views.create_competition, name='ui/create_competition'),
    path('<slug:org_slug>/competitions/<int:comp_id>/manage', views.manage_competition, name='ui/manage_competition'),
]
