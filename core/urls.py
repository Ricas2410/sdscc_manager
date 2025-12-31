"""
Core URL Configuration
"""

from django.urls import path
from . import views, financial_views, mission_financial_views
from . import views_assets
from . import monthly_closing_views
from . import archive_views

app_name = 'core'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard_alt'),
    
    # Role-specific dashboards
    path('dashboard/mission/', views.mission_dashboard, name='mission_dashboard'),
    path('dashboard/area/', views.area_dashboard, name='area_dashboard'),
    path('dashboard/district/', views.district_dashboard, name='district_dashboard'),
    path('dashboard/branch/', views.branch_dashboard, name='branch_dashboard'),
    path('dashboard/auditor/', views.auditor_dashboard, name='auditor_dashboard'),
    path('dashboard/pastor/', views.pastor_dashboard, name='pastor_dashboard'),
    path('dashboard/staff/', views.staff_dashboard, name='staff_dashboard'),
    path('dashboard/member/', views.member_dashboard, name='member_dashboard'),
    
    # Search
    path('search/', views.search, name='search'),
    
    # Administration / Management Console
    path('management/areas/', views.areas_list, name='areas'),
    path('management/districts/', views.districts_list, name='districts'),
    path('management/branches/', views.branches_list, name='branches'),
    path('management/tithe-targets/', views.tithe_targets, name='tithe_targets'),
    path('management/settings/', views.settings_view, name='settings'),
    path('management/backup/', views.data_backup, name='data_backup'),
    path('management/import-members/', views.import_members, name='import_members'),
    path('management/download-member-template/', views.download_member_template, name='download_member_template'),
    path('management/month-close/', views.month_close_management, name='month_close'),
    path('management/close-month/', views.close_month_action, name='close_month_action'),
    
    # API endpoints
    path('api/branches/<uuid:branch_id>/', views.branch_detail_api, name='branch_detail_api'),
    path('api/notifications/', views.notifications_api, name='notifications_api'),
    
    # Calendar
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/manage/', views.calendar_manage, name='calendar_manage'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications'),
    
    # Prayer Requests
    path('prayer-requests/', views.prayer_requests, name='prayer_requests'),
    path('prayer-requests/add/', views.prayer_request_add, name='prayer_request_add'),
    path('prayer-requests/<uuid:pk>/edit/', views.prayer_request_edit, name='prayer_request_edit'),
    path('prayer-requests/<uuid:pk>/pray/', views.prayer_request_pray, name='prayer_request_pray'),
    
    # Visitors & Follow-up
    path('visitors/', views.visitors_list, name='visitors'),
    path('visitors/add/', views.visitor_add, name='visitor_add'),
    path('visitors/<uuid:pk>/', views.visitor_detail, name='visitor_detail'),
    
    # Celebrations (Birthdays & Anniversaries)
    path('celebrations/', views.celebrations, name='celebrations'),
    
    # Assets & Inventory
    path('assets/', views_assets.assets_list, name='assets'),
    path('assets/add/', views_assets.asset_add, name='asset_add'),
    path('assets/<uuid:asset_id>/update/', views_assets.asset_update, name='asset_update'),
    path('assets/delete/', views_assets.asset_delete, name='asset_delete'),
    path('api/assets/<uuid:asset_id>/', views_assets.asset_api_detail, name='asset_api_detail'),
    
    # Exports
    path('export/members/', views.export_members, name='export_members'),
    path('export/contributions/', views.export_contributions, name='export_contributions'),
    path('my-statement/', views.my_statement, name='my_statement'),
    
    # Financial Statistics
    path('financial-statistics/', financial_views.branch_financial_statistics, name='branch_financial_statistics'),
    path('auditor/branch-statistics/', financial_views.auditor_branch_statistics, name='auditor_branch_statistics'),

    # Mission Financial Management
    path('mission/financial-dashboard/', mission_financial_views.mission_financial_dashboard, name='mission_financial_dashboard'),
    path('mission/expenditures/', mission_financial_views.mission_expenditure_list, name='mission_expenditure_list'),
    path('mission/remittances/', mission_financial_views.mission_remittance_tracking, name='mission_remittance_tracking'),
    path('branch-financial-overview/', mission_financial_views.branch_financial_overview, name='branch_financial_overview'),
    path('branch-financial-details/<uuid:branch_id>/', mission_financial_views.branch_financial_details, name='branch_financial_details'),
    
    # Monthly Closing
    path('monthly-closing/', monthly_closing_views.monthly_closing_dashboard, name='monthly_closing'),
    path('monthly-closing/close/', monthly_closing_views.close_month, name='close_month'),
    path('monthly-closing/reopen/', monthly_closing_views.reopen_month, name='reopen_month'),
    path('monthly-closing/check-edit/', monthly_closing_views.check_edit_permission, name='check_edit_permission'),
    path('monthly-closing/check-status/', monthly_closing_views.check_monthly_closing_status, name='check_monthly_closing_status'),
    path('monthly-report/', monthly_closing_views.monthly_report_view, name='monthly_report'),
    path('monthly-report/pdf/', monthly_closing_views.monthly_report_pdf, name='monthly_report_pdf'),
    
    # Archives
    path('archives/', views.archives, name='archives'),
    
    # Year-based Archive System
    path('archive/', archive_views.archive_dashboard, name='archive_dashboard'),
    path('archive/year/<uuid:year_id>/', archive_views.year_detail, name='year_detail'),
    path('archive/create-year/', archive_views.create_fiscal_year, name='create_fiscal_year'),
    path('archive/archive-year/<uuid:year_id>/', archive_views.archive_fiscal_year_view, name='archive_fiscal_year'),

    # PWA
    path('manifest.json', views.manifest_json, name='manifest'),
    path('sw.js', views.service_worker, name='service_worker'),
    path('offline/', views.offline_page, name='offline'),
]
