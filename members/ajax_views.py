"""
AJAX views for member profile picture uploads.
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import InMemoryUploadedFile
from accounts.models import User

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
@login_required
@csrf_exempt
def upload_profile_picture(request, member_id):
    """Handle AJAX profile picture upload."""
    try:
        if not request.user.is_any_admin:
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        
        member = User.objects.get(pk=member_id)
        
        if 'profile_picture' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No file provided'}, status=400)
        
        file = request.FILES['profile_picture']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if file.content_type not in allowed_types:
            return JsonResponse({'success': False, 'error': 'Invalid file type. Please use JPG, PNG, GIF, or WebP.'}, status=400)
        
        # Validate file size (2MB max)
        max_size = 2 * 1024 * 1024  # 2MB
        if file.size > max_size:
            return JsonResponse({'success': False, 'error': 'File too large. Maximum size is 2MB.'}, status=400)
        
        # Delete old picture if exists
        if member.profile_picture:
            try:
                member.profile_picture.delete(save=False)
            except Exception as e:
                logger.warning(f"Failed to delete old profile picture: {e}")
        
        # Save new picture
        member.profile_picture = file
        member.save()
        
        # Return the new picture URL
        picture_url = member.profile_picture.url if member.profile_picture else None
        
        return JsonResponse({
            'success': True,
            'picture_url': picture_url,
            'message': 'Profile picture updated successfully'
        })
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Member not found'}, status=404)
    except Exception as e:
        logger.error(f"Profile picture upload error: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': 'Upload failed. Please try again.'}, status=500)


@require_http_methods(["POST"])
@login_required
@csrf_exempt
def remove_profile_picture(request, member_id):
    """Handle AJAX profile picture removal."""
    try:
        if not request.user.is_any_admin:
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        
        member = User.objects.get(pk=member_id)
        
        if not member.profile_picture:
            return JsonResponse({'success': False, 'error': 'No profile picture to remove'}, status=400)
        
        # Delete the picture
        try:
            member.profile_picture.delete(save=False)
        except Exception as e:
            logger.warning(f"Failed to delete profile picture: {e}")
        
        member.profile_picture = None
        member.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Profile picture removed successfully'
        })
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Member not found'}, status=404)
    except Exception as e:
        logger.error(f"Profile picture removal error: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': 'Failed to remove picture. Please try again.'}, status=500)
