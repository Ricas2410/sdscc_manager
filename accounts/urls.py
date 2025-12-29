"""
Accounts URL Configuration
"""

from django.urls import path
from . import views
from . import pastor_views
from . import photo_upload_views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('force-pin-change/', views.force_pin_change_view, name='force_pin_change'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('change-pin/', views.change_pin_view, name='change_pin'),
    path('change-password/', views.change_password_view, name='change_password'),
    
    # AJAX endpoints
    path('dismiss-pin-modal/', views.dismiss_pin_change_modal, name='dismiss_pin_modal'),
    path('update-pin/', views.update_pin_ajax, name='update_pin_ajax'),
    
    # Admin - User Management
    path('users/', views.users_list, name='users'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<uuid:user_id>/', views.user_detail, name='user_detail'),
    path('users/<uuid:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<uuid:user_id>/delete/', views.delete_user, name='delete_user'),
    
    # Pastor Management
    path('pastors/', pastor_views.pastors_list, name='pastors_list'),
    path('pastors/<uuid:pastor_id>/', pastor_views.pastor_detail, name='pastor_detail'),
    path('pastors/<uuid:pastor_id>/edit/', pastor_views.update_pastor_info, name='pastor_edit'),
    
    # Photo Upload
    path('upload-photo/', photo_upload_views.upload_profile_photo, name='upload_photo'),
    path('delete-photo/', photo_upload_views.delete_profile_photo, name='delete_photo'),
    path('crop-photo/', photo_upload_views.crop_profile_photo, name='crop_photo'),
]
