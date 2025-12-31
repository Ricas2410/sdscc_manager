"""
Reports URL Configuration
"""

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_index, name='index'),
    path('contributions/', views.contribution_report, name='contributions'),
    path('expenditure/', views.expenditure_report, name='expenditure'),
    path('attendance/', views.attendance_report, name='attendance'),
    path('financial/', views.financial_report, name='financial'),
    path('financial-print/', views.financial_report_print, name='financial_print'),
    path('final-financial-report/', views.final_financial_report, name='final_financial_report'),
    
    # Enhanced Statistics & Reports
    path('comprehensive-statistics/', views.comprehensive_statistics, name='comprehensive_statistics'),
    path('member-contributions/', views.member_contributions_report, name='member_contributions'),
    path('export/statistics-excel/', views.export_statistics_excel, name='export_statistics_excel'),
    path('export/member-contributions-excel/', views.export_member_contributions_excel, name='export_member_contributions_excel'),
    
    # Monthly Reports
    path('monthly/', views.monthly_reports, name='monthly_reports'),
    path('monthly/<uuid:pk>/', views.monthly_report_detail, name='monthly_report_detail'),
    path('monthly/generate/', views.monthly_report_generate, name='monthly_report_generate'),
    path('monthly/export/pdf/', views.monthly_report_export_pdf, name='monthly_report_export_pdf'),
    path('monthly/<uuid:pk>/export/pdf/', views.monthly_report_export_pdf, name='monthly_report_export_single_pdf'),
]
