"""
Contributions URL Configuration
"""

from django.urls import path
from . import views
from . import tithe_tracking_views
from . import branch_type_views
from . import views_opening_balance
from . import views_transfers
from . import views_remittances
from . import views_fund_assessment

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
    path('remittances/<uuid:remittance_id>/', views.remittance_detail, name='remittance_detail'),
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

    # Opening Balances
    path('opening-balances/', views_opening_balance.opening_balance_list, name='opening_balances'),
    path('opening-balances/add/', views_opening_balance.opening_balance_add, name='opening_balance_add'),
    path('opening-balances/<uuid:balance_id>/', views_opening_balance.opening_balance_detail, name='opening_balance_detail'),
    path('opening-balances/<uuid:balance_id>/approve/', views_opening_balance.opening_balance_approve, name='opening_balance_approve'),
    path('opening-balances/<uuid:balance_id>/reject/', views_opening_balance.opening_balance_reject, name='opening_balance_reject'),
    path('opening-balances/export/', views_opening_balance.opening_balance_export, name='opening_balance_export'),
    
    # Hierarchy Transfers
    path('transfers/', views_transfers.hierarchy_transfer_list, name='hierarchy_transfers'),
    path('transfers/sent/', views_transfers.hierarchy_transfers_sent, name='hierarchy_transfers_sent'),
    path('transfers/received/', views_transfers.hierarchy_transfers_received, name='hierarchy_transfers_received'),
    path('transfers/add/', views_transfers.hierarchy_transfer_add, name='hierarchy_transfer_add'),
    path('transfers/<uuid:transfer_id>/', views_transfers.hierarchy_transfer_detail, name='hierarchy_transfer_detail'),
    path('transfers/<uuid:transfer_id>/approve/', views_transfers.hierarchy_transfer_approve, name='hierarchy_transfer_approve'),
    path('transfers/<uuid:transfer_id>/cancel/', views_transfers.hierarchy_transfer_cancel, name='hierarchy_transfer_cancel'),
    
    # Hierarchy Remittances
    path('hierarchy-remittances/', views_remittances.hierarchy_remittance_list, name='hierarchy_remittances'),
    path('hierarchy-remittances/area/', views_remittances.hierarchy_remittances_area, name='hierarchy_remittances_area'),
    path('hierarchy-remittances/district/', views_remittances.hierarchy_remittances_district, name='hierarchy_remittances_district'),
    path('hierarchy-remittances/add/', views_remittances.hierarchy_remittance_add, name='hierarchy_remittance_add'),
    path('hierarchy-remittances/<uuid:remittance_id>/', views_remittances.hierarchy_remittance_detail, name='hierarchy_remittance_detail'),
    path('hierarchy-remittances/<uuid:remittance_id>/verify/', views_remittances.hierarchy_remittance_verify, name='hierarchy_remittance_verify'),
    path('hierarchy-remittances/<uuid:remittance_id>/pay/', views_remittances.hierarchy_remittance_pay, name='hierarchy_remittance_pay'),

    # Fund Assessment
    path('fund-assessment/', views_fund_assessment.fund_assessment, name='fund_assessment'),
    path('fund-report/branch/', views_fund_assessment.fund_report_branch, name='fund_report_branch'),
    path('fund-report/branch/<uuid:branch_id>/', views_fund_assessment.fund_report_branch, name='fund_report_branch'),
    path('fund-report/mission/', views_fund_assessment.fund_report_mission, name='fund_report_mission'),

    path('<uuid:contribution_id>/', views.contribution_detail, name='detail'),
]
