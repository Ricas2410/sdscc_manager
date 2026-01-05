"""
Sermons URL Configuration
"""

from django.urls import path
from . import views

app_name = 'sermons'

urlpatterns = [
    path('', views.sermon_list, name='list'),
    path('add/', views.sermon_add, name='add'),
    path('<uuid:sermon_id>/', views.sermon_detail, name='detail'),
    path('<uuid:sermon_id>/edit/', views.sermon_edit, name='edit'),
    path('<uuid:sermon_id>/delete/', views.sermon_delete, name='delete'),
    path('<slug:slug>/', views.sermon_by_slug, name='by_slug'),
]
