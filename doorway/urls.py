from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = "doorway"

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.custom_logout, name='logout'),
    path('dashboard/', views.task_dashboard, name='dashboard'),
    path('create/', views.create_task, name='create_task'),
    path('update/<int:task_id>/', views.update_task, name='update_task'),
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('toggle/<int:task_id>/', views.toggle_task_completion, name='toggle_task_completion'),
    path('detail/<int:task_id>/', views.task_detail, name='task_detail'),
    path('export_tasks_csv/', views.export_tasks_csv, name='export_tasks_csv'),
    path('export_tasks_pdf/', views.export_tasks_pdf, name='export_tasks_pdf'),
    path('export_single_task_csv/<int:task_id>/', views.export_single_task_csv, name='export_single_task_csv'),
    path('export_single_task_pdf/<int:task_id>/', views.export_single_task_pdf, name='export_single_task_pdf'),
    path('export_options/', views.export_options, name='export_options'),
      
]
