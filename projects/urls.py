from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path('', views.projects_list, name="projects_list"),
    # path('create/', views.create_project, name="create_project"),
    path('<slug:slug>/', views.project_detail, name='project_detail')
]

