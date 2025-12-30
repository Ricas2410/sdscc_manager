"""
Expenditure URL Configuration
"""

from django.urls import path
from . import views
from . import welfare_approval_views

app_name = 'expenditure'

urlpatterns = [
    # General expenditure list (legacy, shows all)
    path('', views.expenditure_list, name='list'),
    path('add/', views.expenditure_add, name='add'),
    path('categories/', views.expenditure_categories, name='categories'),
    
    # Mission-level expenditures (Mission-wide)
    path('mission/', views.mission_expenditure_list, name='mission_list'),
    path('mission/add/', views.add_mission_expenditure, name='add_mission'),
    
    # Branch-level expenditures (Branch-only)
    path('branch/', views.branch_expenditure_list, name='branch_list'),
    path('branch/add/', views.add_branch_expenditure, name='add_branch'),
    
    # Utilities, welfare, assets
    path('utilities/', views.utility_bills, name='utilities'),
    path('welfare/', views.welfare_payments, name='welfare'),
    path('assets/', views.assets_list, name='assets'),
    
    # Welfare Approval System
    path('welfare/requests/', welfare_approval_views.welfare_requests_list, name='welfare_requests'),
    path('welfare/<uuid:payment_id>/', welfare_approval_views.welfare_request_detail, name='welfare_detail'),
    path('welfare/<uuid:payment_id>/approve/', welfare_approval_views.approve_welfare_request, name='approve_welfare'),
    path('welfare/<uuid:payment_id>/decline/', welfare_approval_views.decline_welfare_request, name='decline_welfare'),
    path('welfare/bulk-approve/', welfare_approval_views.bulk_approve_welfare, name='bulk_approve_welfare'),
    
    path('<uuid:expenditure_id>/', views.expenditure_detail, name='detail'),
]
