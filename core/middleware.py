import logging
import json
from django.utils import timezone
from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse
from django.core.exceptions import RequestDataTooBig
from .models import SiteSettings

logger = logging.getLogger('core')

class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow access to admin and login pages even in maintenance mode
        path = request.path_info
        if path.startswith('/admin/') or path.startswith('/accounts/login/'):
            return self.get_response(request)

        # Check maintenance mode
        try:
            site_settings = SiteSettings.objects.first()
            if site_settings and site_settings.maintenance_mode:
                if not request.user.is_staff:
                    return render(request, 'core/maintenance.html', status=503)
        except Exception:
            pass

        return self.get_response(request)

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Update last_login efficiently using cache to avoid DB writes on every request
            cache_key = f'last_seen_{request.user.id}'
            if not cache.get(cache_key):
                request.user.last_login = timezone.now()
                request.user.save(update_fields=['last_login'])
                cache.set(cache_key, True, 300)  # Update every 5 minutes

        return self.get_response(request)

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Log dangerous methods
        if request.method in ['POST', 'PUT', 'DELETE'] and request.user.is_authenticated:
            logger.info(
                f"AUDIT: User {request.user.member_id} accessed {request.path} "
                f"via {request.method} - Status: {response.status_code}"
            )
            
        return response

class MultipartErrorHandler:
    """Handle multipart parser errors that cause SystemExit in gunicorn workers."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except (RequestDataTooBig, OSError, ValueError) as e:
            # Log the error for debugging
            logger.error(f"Multipart parser error: {e}", exc_info=True)
            
            # Return a user-friendly error response
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # AJAX request
                return HttpResponse(
                    json.dumps({'error': 'File upload too large or invalid format'}),
                    content_type='application/json',
                    status=413
                )
            else:
                # Regular form submission - redirect back with error message
                from django.contrib import messages
                messages.error(request, 'File upload failed: File too large or invalid format. Please try again.')
                # Redirect to the same page or a safe fallback
                return HttpResponse(status=413)  # Let the browser handle it
        except Exception as e:
            # Re-raise other exceptions
            raise e
