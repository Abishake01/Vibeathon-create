"""
URL configuration for API endpoints.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='health'),
    
    # Projects endpoints
    path('projects/', views.list_projects, name='list_projects'),
    path('projects', views.create_project, name='create_project'),
    path('projects/<str:project_id>/', views.get_project, name='get_project'),
    path('projects/<str:project_id>', views.get_project, name='get_project_no_slash'),
    path('projects/<str:project_id>/update/', views.update_project, name='update_project'),
    path('projects/<str:project_id>/delete/', views.delete_project, name='delete_project'),
    path('projects/<str:project_id>/files', views.get_project_files, name='get_project_files'),
    path('projects/<str:project_id>/files/', views.get_project_files, name='get_project_files_slash'),
    path('projects/<str:project_id>/files/<str:filename>', views.get_file_content, name='get_file_content'),
    path('projects/<str:project_id>/files/<str:filename>/', views.get_file_content, name='get_file_content_slash'),
    path('projects/<str:project_id>/files/<str:filename>/update/', views.update_file, name='update_file'),
    path('projects/<str:project_id>/preview', views.preview_project, name='preview_project'),
    path('projects/<str:project_id>/preview/', views.preview_project, name='preview_project_slash'),
    
    # AI endpoints
    path('ai/create-project-stream', views.create_project_with_ai_stream, name='create_project_with_ai_stream'),
    path('ai/create-project-stream/', views.create_project_with_ai_stream, name='create_project_with_ai_stream_slash'),
    path('ai/tokens', views.get_token_info, name='get_token_info'),
    path('ai/tokens/', views.get_token_info, name='get_token_info_slash'),
    
    # Test endpoint
    path('test/imports', views.test_imports, name='test_imports'),
]

