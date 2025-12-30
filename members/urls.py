"""
Members URL Configuration
"""

from django.urls import path
from . import views
from . import pastor_views
from . import export_views
from . import ajax_views

app_name = 'members'

urlpatterns = [
    path('', views.member_list, name='list'),
    path('add/', views.member_add, name='add'),
    path('import/', views.member_import, name='import'),
    path('import/template/', views.download_import_template, name='import_template'),
    path('<uuid:member_id>/', views.member_detail, name='detail'),
    path('<uuid:member_id>/edit/', views.member_edit, name='edit'),
    path('api/districts/<uuid:area_id>/', views.get_districts, name='get_districts'),
    path('api/branches/<uuid:district_id>/', views.get_branches, name='get_branches'),
    
    # AJAX Profile Picture Upload
    path('<uuid:member_id>/upload-picture/', ajax_views.upload_profile_picture, name='upload_picture'),
    path('<uuid:member_id>/remove-picture/', ajax_views.remove_profile_picture, name='remove_picture'),
    
    # Member Export
    path('export-page/', export_views.export_members_page, name='export_page'),
    path('export-excel/', export_views.export_members_excel, name='export_excel'),
    path('export-csv/', export_views.export_members_csv, name='export_csv'),
    path('export-preview/', export_views.export_members_preview, name='export_preview'),
    
    # Pastor member management
    path('manage/', pastor_views.pastor_manage_members, name='pastor_manage'),
    path('pastor/add/', pastor_views.pastor_add_member, name='pastor_add'),
    path('pastor/<uuid:member_id>/', pastor_views.pastor_member_detail, name='pastor_detail'),
    path('pastor/<uuid:member_id>/transfer/', pastor_views.pastor_transfer_member, name='pastor_transfer'),
    path('pastor/<uuid:member_id>/notes/', pastor_views.pastor_edit_notes, name='pastor_edit_notes'),
    path('export/', pastor_views.pastor_export_members, name='pastor_export'),
    path('analytics/', pastor_views.pastor_member_analytics, name='pastor_analytics'),
]
