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
    path('pool/<int:pool_id>', views.pool, name='main/pool_endpoint'),
    path('de_table/<int:table_id>', views.de_table, name='main/de_table_endpoint'),
    path('competition/<int:comp_id>', views.competition, name='main/competition_endpoint'),
    path('organisation/<int:org_id>', views.organisation, name='main/organisation_endpoint'),
    path('stage/<int:stage_id>', views.stage_router, name='main/stage_endpoint'),
    path('<int:comp_id>/<int:stage_number>.pdf', views.stage_router_pdf, name='main/stage/pdf'),
    path('<int:comp_id>/<int:stage_number>/results', views.stage_router_results, name='main/stage/results'),
    path('<int:comp_id>/<int:stage_number>/results.pdf', views.stage_router_results_pdf, name='main/stage/results/pdf')
]
