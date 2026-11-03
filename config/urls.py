"""
Capacity Connect URL Configuration
SIH26075 - Ministry of Earth Sciences (MoES) Portal
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('courses/', include('apps.courses.urls')),
    path('assessments/', include('apps.assessments.urls')),
    path('competencies/', include('apps.competencies.urls')),
    path('certificates/', include('apps.certificates.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('communications/', include('apps.communications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Custom Error Handlers
handler400 = 'apps.core.views.bad_request_view'
handler403 = 'apps.core.views.permission_denied_view'
handler404 = 'apps.core.views.page_not_found_view'
handler500 = 'apps.core.views.server_error_view'

