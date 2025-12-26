"""
Context processors for SDSCC templates.
"""

from django.conf import settings


def site_settings(request):
    """Add site settings to template context."""
    from core.models import SiteSettings
    
    try:
        settings_obj = SiteSettings.get_settings()
    except Exception:
        settings_obj = None
    
    context = {
        'site_settings': settings_obj,
        'sdscc_config': getattr(settings, 'SDSCC_SETTINGS', {}),
    }
    
    # Add user role info if authenticated
    if request.user.is_authenticated:
        context['user_role'] = request.user.role
        context['user_is_admin'] = request.user.is_any_admin
        context['user_branch'] = request.user.branch
    
    return context
