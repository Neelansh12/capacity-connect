from django.urls import path
from . import views

app_name = 'competencies'

urlpatterns = [
    path('', views.competency_library_view, name='library'),
    path('discovery/', views.trainer_discovery_view, name='trainer_discovery'),
    path('trainer/my-skills/', views.trainer_skills_view, name='trainer_skills'),
    path('employee/my-skills/', views.employee_skills_view, name='employee_skills'),
]

