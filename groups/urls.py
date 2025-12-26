"""
Groups URL Configuration
"""

from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    path('', views.group_list, name='list'),
    path('add/', views.group_add, name='add'),
    path('<uuid:group_id>/', views.group_detail, name='detail'),
    path('<uuid:group_id>/members/', views.group_members, name='members'),
    path('api/search-members/', views.search_members, name='search_members'),
    path('api/branch/<uuid:branch_id>/members/', views.get_branch_members, name='branch_members'),
]
