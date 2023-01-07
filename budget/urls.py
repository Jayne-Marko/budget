"""budgetproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.project_list, name='list'),
    path('add', views.ProjectCreateView.as_view(), name='add'),
    path('<int:pk>/edit', views.ProjectUpdateView.as_view(), name='edit'),
    path('<int:pk>/del', views.ProjectDeleteView.as_view(), name='delete'),
    path('recurrent', views.recurrent_expenses, name='recurrent'),
    path('<slug:project_slug>', views.project_detail, name='detail'),
    path('<slug:project_slug>/addrec', views.add_recurrent, name='add_recurrent')
]