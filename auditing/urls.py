"""
Auditing URL Configuration
"""

from django.urls import path
from . import views
from . import comprehensive_views

app_name = 'auditing'

urlpatterns = [
    # Comprehensive Auditor Dashboard
    path('dashboard/', comprehensive_views.auditor_dashboard, name='dashboard'),
    path('financial-audit/', comprehensive_views.financial_audit_report, name='financial_audit'),
    path('financial-audit/export-excel/', comprehensive_views.export_audit_report_excel, name='export_audit_excel'),
    path('contribution-trail/', comprehensive_views.contribution_audit_trail, name='contribution_trail'),
    path('expenditure-trail/', comprehensive_views.expenditure_audit_trail, name='expenditure_trail'),
    path('variance-analysis/', comprehensive_views.variance_analysis, name='variance_analysis'),
    
    # Original audit views
    path('logs/', views.audit_logs, name='logs'),
    path('reports/', views.audit_reports, name='reports'),
    path('financial-reports/', views.auditor_financial_reports, name='financial_reports'),
    path('financial-reports/export-pdf/', views.export_financial_report_pdf, name='export_financial_report_pdf'),
    path('member-lookup/', views.member_lookup_report, name='member_lookup'),
    path('member-lookup/export-pdf/', views.export_member_report_pdf, name='export_member_report_pdf'),
    path('flags/', views.audit_flags, name='flags'),
    path('contributions/', views.auditor_contributions, name='contributions'),
    path('expenditures/', views.auditor_expenditures, name='expenditures'),
]
