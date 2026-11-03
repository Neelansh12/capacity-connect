from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    path('verify/', views.certificate_verify_view, name='verify'),
    path('view/<str:cert_id>/', views.certificate_view, name='view'),
    path('download/<str:cert_id>/', views.certificate_download_view, name='download'),
    path('claim/<int:enrollment_id>/', views.request_certificate_view, name='claim'),
]

