"""
Auditing URL Configuration
"""

from django.urls import path
from . import views

app_name = 'auditing'

urlpatterns = [
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
