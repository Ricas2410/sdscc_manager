"""
Payroll URL Configuration
"""

from django.urls import path
from . import views
from . import staff_payroll_views

app_name = 'payroll'

urlpatterns = [
    # Old routes (keeping for compatibility)
    path('staff/', views.staff_list, name='staff_list'),
    path('runs/', views.payroll_runs, name='runs'),
    path('commissions/', views.commissions_list, name='commissions'),
    path('commissions/calculate/', views.calculate_commissions, name='calculate_commissions'),
    
    # New comprehensive staff & payroll management
    path('staff-management/', staff_payroll_views.staff_payroll_management, name='staff_management'),
    path('staff/add-to-payroll/', staff_payroll_views.add_staff_to_payroll, name='add_to_payroll'),
    path('staff/update-salary/<uuid:profile_id>/', staff_payroll_views.update_staff_salary, name='update_salary'),
    path('payroll-processing/', staff_payroll_views.payroll_processing, name='payroll_processing'),
    path('my-payroll/', staff_payroll_views.my_payroll, name='my_payroll'),
    path('payment-history/', staff_payroll_views.payment_history, name='payment_history'),
    path('payment-history/export/', staff_payroll_views.export_payment_history, name='export_payment_history'),
    path('payslip/<uuid:payslip_id>/', staff_payroll_views.payslip_detail, name='payslip_detail'),
    path('payslip/<uuid:payslip_id>/download/', staff_payroll_views.download_payslip, name='download_payslip'),
    path('export/', staff_payroll_views.export_payroll, name='export_payroll'),
]
