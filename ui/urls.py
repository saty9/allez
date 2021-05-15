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
from .views import CreateOrganisation

urlpatterns = [
    path('', views.front_page, name='ui/front_page'),
    path('organisation/create', CreateOrganisation.as_view(), name='ui/organisation/create'),
    path('organisation/list', views.organisation_list, name='ui/organisation/list'),
    path('change_org/', views.change_org, name='ui/change_org'),
    path('dt/pool/<int:pool_id>', views.dt_manage_pool, name='ui/dt_manage_pool'),
    path('dt/de/<int:de_table_id>', views.dt_manage_de_table, name='ui/dt_manage_de'),
    path('<slug:org_slug>', views.organisation, name='ui/organisation/show'),
    path('<slug:org_slug>/competitions', views.list_competitions, name='ui/org/competitions'),
    path('<slug:org_slug>/competitions/create', views.create_competition, name='ui/create_competition'),
    path('<slug:org_slug>/competitions/<int:comp_id>/manage', views.manage_competition, name='ui/manage_competition'),
    path('<slug:org_slug>/competitions/<int:comp_id>/manage/check_in', views.check_in, name='ui/check_in'),
    path('<slug:org_slug>/competitions/<int:comp_id>/manage/<int:stage_id>', views.manage_stage_router, name='ui/manage_stage'),
    path('<slug:org_slug>/competitions/<int:comp_id>/manage/<int:stage_id>/ranking', views.stage_ranking, name='ui/stage_ranking')
]
