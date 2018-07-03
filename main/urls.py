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
from. import views

urlpatterns = [
    path('comp/<int:comp_id>/stage/<int:stage_number>', views.stage_router, name='main/stage'),
    path('comp/<int:comp_id>/stage/<int:stage_number>/pdf', views.stage_router_pdf, name='main/stage/pdf'),
    path('comp/<int:comp_id>/stage/<int:stage_number>/results', views.stage_router_seeding, name='main/stage/results')
]
