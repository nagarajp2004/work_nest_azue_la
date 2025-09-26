from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.dashboard, name='dashboard'),

    # API routes
    path('api/tasks/', views.get_tasks, name='api_get_tasks'),
    path('api/users/', views.get_assignable_users, name='api_get_users'),
    path('api/tasks/create/', views.create_task, name='api_create_task'),
    path('api/tasks/update/<int:task_id>/', views.update_task_status, name='api_update_task_status'),
]
