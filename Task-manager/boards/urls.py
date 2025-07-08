from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Board URLs
    path('', views.board_list, name='board_list'),
    path('boards/create/', views.board_create, name='board_create'),
    path('boards/<int:pk>/', views.board_detail, name='board_detail'),
    path('boards/<int:pk>/edit/', views.board_edit, name='board_edit'),
    path('boards/<int:pk>/delete/', views.board_delete, name='board_delete'),
    
    # Task List URLs
    path('boards/<int:board_pk>/lists/create/', views.task_list_create, name='task_list_create'),
    path('listas/<int:lista_id>/editar/', views.editar_lista, name='editar_lista'),
    path('lists/<int:pk>/delete/', views.task_list_delete, name='task_list_delete'),
    path('lists/<int:pk>/edit/', views.task_list_edit, name='task_list_edit'),
    
    # Task URLs
    path('boards/<int:board_pk>/tasks/create/', views.task_create, name='task_create'),
    path('boards/<int:board_pk>/lists/<int:list_pk>/tasks/create/', views.task_create, name='task_create_in_list'),
    path('lists/<int:list_pk>/tasks/quick-create/', views.quick_task_create, name='quick_task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:pk>/move/', views.task_move, name='task_move'),
    path('tasks/<int:pk>/toggle-complete/', views.task_toggle_complete, name='task_toggle_complete'),
    
    # Export URLs
    path('boards/<int:pk>/export/csv/', views.export_board_csv, name='export_board_csv'),
    path('boards/<int:pk>/export/json/', views.export_board_json, name='export_board_json'),
    
    # Search URLs
    path('search/', views.search_tasks, name='search_tasks'),
]
