"""
Announcements URL Configuration
"""

from django.urls import path
from . import views

app_name = 'announcements'

urlpatterns = [
    path('', views.announcement_list, name='list'),
    path('add/', views.announcement_add, name='add'),
    path('events/', views.event_list, name='events'),
    path('events/add/', views.event_add, name='event_add'),
    path('events/<uuid:event_id>/', views.event_detail, name='event_detail'),
    path('events/<uuid:event_id>/edit/', views.event_edit, name='event_edit'),
    path('events/<uuid:event_id>/delete/', views.event_delete, name='event_delete'),
    path('<uuid:announcement_id>/', views.announcement_detail, name='detail'),
    path('<uuid:announcement_id>/edit/', views.announcement_edit, name='edit'),
    path('<uuid:announcement_id>/delete/', views.announcement_delete, name='delete'),
]
