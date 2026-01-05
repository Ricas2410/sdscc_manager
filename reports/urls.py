"""
Reports URL Configuration
"""

from django.urls import path
from . import views
from . import yearly_views
from . import views_hierarchy

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
    
    # Yearly Reports - Professional audit-safe yearly financial reports
    path('yearly/', yearly_views.yearly_reports_index, name='yearly_reports_index'),
    path('yearly/mission/', yearly_views.mission_yearly_report, name='mission_yearly_report'),
    path('yearly/branch/', yearly_views.branch_yearly_report, name='branch_yearly_report'),
    path('yearly/member/', yearly_views.member_yearly_statement, name='member_yearly_statement'),
    path('yearly/mission/pdf/', yearly_views.export_mission_yearly_pdf, name='export_mission_yearly_pdf'),
    path('yearly/branch/pdf/', yearly_views.export_branch_yearly_pdf, name='export_branch_yearly_pdf'),
    path('yearly/member/pdf/', yearly_views.export_member_yearly_pdf, name='export_member_yearly_pdf'),
    path('yearly/mission/excel/', yearly_views.export_mission_yearly_excel, name='export_mission_yearly_excel'),
    path('yearly/branch/excel/', yearly_views.export_branch_yearly_excel, name='export_branch_yearly_excel'),
    path('yearly/member/excel/', yearly_views.export_member_yearly_excel, name='export_member_yearly_excel'),
    
    # Area Financial Reports
    path('area-financial-reports/', views_hierarchy.area_financial_reports, name='area_financial_reports'),
    path('area-financial-reports/<uuid:report_id>/', views_hierarchy.area_financial_report_detail, name='area_financial_report_detail'),
    path('area-financial-reports/generate/', views_hierarchy.area_financial_report_generate, name='area_financial_report_generate'),
    path('area-financial-reports/<uuid:report_id>/export/', views_hierarchy.area_financial_report_export, name='area_financial_report_export'),
    path('area-financial-reports/<uuid:report_id>/delete/', views_hierarchy.area_financial_report_delete, name='area_financial_report_delete'),
    
    # District Financial Reports
    path('district-financial-reports/', views_hierarchy.district_financial_reports, name='district_financial_reports'),
    path('district-financial-reports/<uuid:report_id>/', views_hierarchy.district_financial_report_detail, name='district_financial_report_detail'),
    path('district-financial-reports/generate/', views_hierarchy.district_financial_report_generate, name='district_financial_report_generate'),
    path('district-financial-reports/<uuid:report_id>/export/', views_hierarchy.district_financial_report_export, name='district_financial_report_export'),
    path('district-financial-reports/<uuid:report_id>/delete/', views_hierarchy.district_financial_report_delete, name='district_financial_report_delete'),
]
