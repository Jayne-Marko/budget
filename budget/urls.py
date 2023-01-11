from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login_user', views.login_user, name="login"),
    path('logout_user', views.logout_user, name='logout'),
    path('register_user', views.register_user, name='register_user'),
    path('list', views.project_list, name='list'),
    path('add', views.ProjectCreateView.as_view(), name='add'),
    path('<int:pk>/edit', views.ProjectUpdateView.as_view(), name='edit'),
    path('<int:pk>/del', views.ProjectDeleteView.as_view(), name='delete'),
    path('recurrent', views.recurrent_expenses, name='recurrent'),
    path('<slug:project_slug>', views.project_detail, name='detail'),
    path('<slug:project_slug>/addrec', views.add_recurrent, name='add_recurrent'),
]