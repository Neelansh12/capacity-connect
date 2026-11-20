from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('catalog/', views.course_catalog_view, name='catalog'),
    path('detail/<slug:slug>/', views.course_detail_view, name='detail'),
    path('enroll/<slug:slug>/', views.enroll_view, name='enroll'),
    path('<slug:slug>/learn/', views.learn_view, name='learn'),
    path('modules/<int:module_id>/complete/', views.module_complete_view, name='module_complete'),

    # Trainer Course Management
    path('trainer/my-courses/', views.trainer_course_list_view, name='trainer_course_list'),
    path('trainer/new/', views.trainer_course_create_view, name='trainer_create'),
    path('trainer/<int:course_id>/edit/', views.trainer_course_edit_view, name='trainer_edit'),
    path('trainer/<int:course_id>/modules/', views.trainer_module_manage_view, name='manage_modules'),
    path('trainer/modules/<int:module_id>/resource/', views.trainer_resource_manage_view, name='add_resource'),
]

