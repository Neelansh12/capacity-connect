from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    path('<slug:course_slug>/', views.assessment_detail_view, name='detail'),
    path('<slug:course_slug>/take/', views.assessment_take_view, name='take'),
    path('<slug:course_slug>/submit/', views.submit_assessment_view, name='submit'),
    path('results/<int:attempt_id>/', views.attempt_result_view, name='result'),

    # Trainer Management
    path('trainer/<int:course_id>/configure/', views.trainer_assessment_manage_view, name='manage_assessment'),
    path('trainer/assessment/<int:assessment_id>/questions/', views.trainer_questions_manage_view, name='manage_questions'),
]

