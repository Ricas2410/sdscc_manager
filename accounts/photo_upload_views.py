"""
Photo Upload Views - Improved photo handling for all devices
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image
import io
import base64
import uuid

from accounts.models import User


@login_required
def upload_profile_photo(request):
    """Upload profile photo with compression and multiple input support."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
    user_id = request.POST.get('user_id')
    if not user_id:
        user = request.user
    else:
        if not request.user.is_any_admin:
            return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
        user = get_object_or_404(User, pk=user_id)
    
    try:
        # Check if photo is base64 encoded (from camera)
        photo_data = request.POST.get('photo_data')
        if photo_data:
            # Handle base64 encoded image (from camera)
            format, imgstr = photo_data.split(';base64,')
            ext = format.split('/')[-1]
            
            # Decode base64 image
            image_data = base64.b64decode(imgstr)
            image = Image.open(io.BytesIO(image_data))
            
        elif request.FILES.get('photo'):
            # Handle uploaded file (from gallery)
            photo_file = request.FILES['photo']
            image = Image.open(photo_file)
            ext = photo_file.name.split('.')[-1].lower()
            
        else:
            return JsonResponse({'success': False, 'message': 'No photo provided'}, status=400)
        
        # Convert RGBA to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Resize image to max 800x800 while maintaining aspect ratio
        max_size = (800, 800)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to BytesIO
        output = io.BytesIO()
        
        # Use JPEG for better compression
        if ext.lower() in ['jpg', 'jpeg']:
            image.save(output, format='JPEG', quality=85, optimize=True)
            ext = 'jpg'
        elif ext.lower() == 'png':
            image.save(output, format='PNG', optimize=True)
        else:
            image.save(output, format='JPEG', quality=85, optimize=True)
            ext = 'jpg'
        
        output.seek(0)
        
        # Generate unique filename
        filename = f"profile_photos/{user.user_id}_{uuid.uuid4().hex[:8]}.{ext}"
        
        # Delete old profile picture if exists
        if user.profile_picture:
            try:
                default_storage.delete(user.profile_picture.name)
            except:
                pass
        
        # Save new photo
        user.profile_picture.save(filename, ContentFile(output.read()), save=True)
        
        return JsonResponse({
            'success': True,
            'message': 'Photo uploaded successfully',
            'photo_url': user.profile_picture.url if user.profile_picture else None
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error uploading photo: {str(e)}'
        }, status=500)


@login_required
def delete_profile_photo(request):
    """Delete profile photo."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
    user_id = request.POST.get('user_id')
    if not user_id:
        user = request.user
    else:
        if not request.user.is_any_admin:
            return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
        user = get_object_or_404(User, pk=user_id)
    
    try:
        if user.profile_picture:
            default_storage.delete(user.profile_picture.name)
            user.profile_picture = None
            user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Photo deleted successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No photo to delete'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting photo: {str(e)}'
        }, status=500)


@login_required
def crop_profile_photo(request):
    """Crop profile photo to specified dimensions."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
    user_id = request.POST.get('user_id')
    if not user_id:
        user = request.user
    else:
        if not request.user.is_any_admin:
            return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
        user = get_object_or_404(User, pk=user_id)
    
    if not user.profile_picture:
        return JsonResponse({'success': False, 'message': 'No photo to crop'}, status=400)
    
    try:
        # Get crop coordinates
        x = int(request.POST.get('x', 0))
        y = int(request.POST.get('y', 0))
        width = int(request.POST.get('width', 0))
        height = int(request.POST.get('height', 0))
        
        # Open image
        image = Image.open(user.profile_picture.path)
        
        # Crop image
        cropped = image.crop((x, y, x + width, y + height))
        
        # Resize to standard size
        cropped = cropped.resize((400, 400), Image.Resampling.LANCZOS)
        
        # Save
        output = io.BytesIO()
        cropped.save(output, format='JPEG', quality=90, optimize=True)
        output.seek(0)
        
        # Generate new filename
        filename = f"profile_photos/{user.user_id}_{uuid.uuid4().hex[:8]}.jpg"
        
        # Delete old photo
        default_storage.delete(user.profile_picture.name)
        
        # Save cropped photo
        user.profile_picture.save(filename, ContentFile(output.read()), save=True)
        
        return JsonResponse({
            'success': True,
            'message': 'Photo cropped successfully',
            'photo_url': user.profile_picture.url
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error cropping photo: {str(e)}'
        }, status=500)
