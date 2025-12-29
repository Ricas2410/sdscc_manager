"""
Contributions URL Configuration
"""

from django.urls import path
from . import views
from . import tithe_tracking_views
from . import branch_type_views

app_name = 'contributions'

urlpatterns = [
    path('', views.contribution_list, name='list'),
    path('my-contributions/', views.my_contributions, name='my_contributions'),
    path('my-history/', views.my_contribution_history, name='my_history'),
    path('add/', views.contribution_add, name='add'),
    path('import/', views.contribution_import, name='import'),
    path('import/template/', views.download_contribution_template, name='import_template'),
    path('weekly/', views.weekly_entry, name='weekly_entry'),
    path('individual/', views.individual_entry, name='individual_entry'),
    path('types/', views.contribution_types, name='types'),
    path('types/<uuid:type_id>/', views.contribution_type_detail, name='type_detail'),
    path('remittances/', views.remittance_list, name='remittances'),
    path('remittances/add/', views.remittance_add, name='remittance_add'),
    path('my-commission/', views.my_commission, name='my_commission'),
    path('mission-returns/', views.mission_returns, name='mission_returns'),
    path('mission-returns/mark-paid/<uuid:branch_id>/', views.mark_return_paid, name='mark_return_paid'),
    
    # Tithe Tracking & Commission Management
    path('tithe-performance/', tithe_tracking_views.tithe_performance, name='tithe_performance'),
    path('commission-management/', tithe_tracking_views.commission_management, name='commission_management'),
    path('commission-report/print/', tithe_tracking_views.commission_report_print, name='commission_report_print'),
    
    # Branch Contribution Types
    path('branch-types/', branch_type_views.branch_contribution_types, name='branch_types'),
    path('branch-types/create/', branch_type_views.create_branch_contribution_type, name='create_branch_type'),
    path('branch-types/<uuid:type_id>/edit/', branch_type_views.edit_branch_contribution_type, name='edit_branch_type'),
    path('branch-types/<uuid:type_id>/deactivate/', branch_type_views.deactivate_branch_contribution_type, name='deactivate_branch_type'),
    path('branch-types/<uuid:type_id>/activate/', branch_type_views.activate_branch_contribution_type, name='activate_branch_type'),
    path('api/branch-type/<uuid:type_id>/', branch_type_views.get_branch_contribution_type_api, name='get_branch_type_api'),

    path('<uuid:contribution_id>/', views.contribution_detail, name='detail'),
]
