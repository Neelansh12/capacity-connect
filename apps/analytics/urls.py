from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('trainer/', views.trainer_dashboard_view, name='trainer_dashboard'),
    path('employee/', views.employee_dashboard_view, name='employee_dashboard'),
    path('admin/report/pdf/', views.download_admin_report_view, name='admin_report_pdf'),
]

