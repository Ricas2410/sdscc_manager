"""
URL configuration for SDSCC Church Management System.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('accounts/', include('accounts.urls')),
    
    # Core / Dashboard
    path('', include('core.urls')),
    
    # App URLs
    path('members/', include('members.urls')),
    path('contributions/', include('contributions.urls')),
    path('expenditure/', include('expenditure.urls')),
    path('attendance/', include('attendance.urls')),
    path('announcements/', include('announcements.urls')),
    path('sermons/', include('sermons.urls')),
    path('groups/', include('groups.urls')),
    path('payroll/', include('payroll.urls')),
    path('reports/', include('reports.urls')),
    path('auditing/', include('auditing.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT)


# Custom Error Handlers
handler400 = 'core.views.error_400'
handler403 = 'core.views.error_403'
handler404 = 'core.views.error_404'
handler405 = 'core.views.error_405'
handler500 = 'core.views.error_500'
