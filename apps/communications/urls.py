from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('announcements/', views.announcements_list_view, name='announcements'),
    path('announcements/new/', views.announcement_create_view, name='create_announcement'),
    path('notifications/', views.notification_list_view, name='notifications'),
    path('feedback/<slug:slug>/', views.course_feedback_view, name='course_feedback'),
    path('library/', views.resource_library_view, name='resource_library'),
    path('library/upload/', views.resource_upload_view, name='resource_upload'),
]

