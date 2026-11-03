from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('pending-approval/', views.pending_approval_view, name='pending_approval'),
    path('dashboard-redirect/', views.dashboard_redirect_view, name='dashboard_redirect'),
    path('profile/', views.profile_view, name='profile'),

    # Admin User Management
    path('manage/users/', views.admin_user_list_view, name='admin_user_list'),
    path('manage/users/<int:user_id>/approval/', views.admin_user_approval_view, name='admin_user_approval'),
]

