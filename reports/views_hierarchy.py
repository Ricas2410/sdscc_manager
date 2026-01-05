"""
Views for Area and District financial reports
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q
from django.http import HttpResponse
import csv
import calendar
from datetime import datetime

from .models_hierarchy import AreaFinancialReport, DistrictFinancialReport
from accounts.permissions import mission_admin_required, area_executive_required, district_executive_required
from core.models import Area, District, Branch


@login_required
def area_financial_reports(request):
    """View all area financial reports."""
    user = request.user
    
    # Get filter parameters
    selected_area = request.GET.get('area')
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')
    
    # Base queryset
    reports = AreaFinancialReport.objects.all()
    
    # Apply filters
    if selected_area:
        reports = reports.filter(area_id=selected_area)
    
    if selected_year:
        reports = reports.filter(year=selected_year)
    
    if selected_month:
        reports = reports.filter(month=selected_month)
    
    # Filter based on user role
    if not (user.is_mission_admin or user.is_auditor):
        if user.is_area_executive and user.managed_area:
            reports = reports.filter(area=user.managed_area)
        else:
            reports = AreaFinancialReport.objects.none()
    
    # Order reports
    reports = reports.order_by('-year', '-month', 'area__name')
    
    # Get data for filters
    areas = Area.objects.all().order_by('name')
    
    # Get years for filter (current year and past 5 years)
    current_year = datetime.now().year
    years = list(range(current_year, current_year - 6, -1))
    
    # Get months for filter
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    
    context = {
        'reports': reports,
        'areas': areas,
        'years': years,
        'months': months,
        'selected_area': selected_area,
        'selected_year': int(selected_year) if selected_year else None,
        'selected_month': int(selected_month) if selected_month else None,
    }
    
    return render(request, 'reports/area_financial_reports.html', context)


@login_required
def district_financial_reports(request):
    """View all district financial reports."""
    user = request.user
    
    # Get filter parameters
    selected_area = request.GET.get('area')
    selected_district = request.GET.get('district')
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')
    
    # Base queryset
    reports = DistrictFinancialReport.objects.all()
    
    # Apply filters
    if selected_area:
        reports = reports.filter(district__area_id=selected_area)
    
    if selected_district:
        reports = reports.filter(district_id=selected_district)
    
    if selected_year:
        reports = reports.filter(year=selected_year)
    
    if selected_month:
        reports = reports.filter(month=selected_month)
    
    # Filter based on user role
    if not (user.is_mission_admin or user.is_auditor):
        if user.is_area_executive and user.managed_area:
            reports = reports.filter(district__area=user.managed_area)
        elif user.is_district_executive and user.managed_district:
            reports = reports.filter(district=user.managed_district)
        else:
            reports = DistrictFinancialReport.objects.none()
    
    # Order reports
    reports = reports.order_by('-year', '-month', 'district__name')
    
    # Get data for filters
    areas = Area.objects.all().order_by('name')
    
    if selected_area:
        districts = District.objects.filter(area_id=selected_area).order_by('name')
    else:
        districts = District.objects.all().order_by('name')
    
    # Get years for filter (current year and past 5 years)
    current_year = datetime.now().year
    years = list(range(current_year, current_year - 6, -1))
    
    # Get months for filter
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    
    context = {
        'reports': reports,
        'areas': areas,
        'districts': districts,
        'years': years,
        'months': months,
        'selected_area': selected_area,
        'selected_district': selected_district,
        'selected_year': int(selected_year) if selected_year else None,
        'selected_month': int(selected_month) if selected_month else None,
    }
    
    return render(request, 'reports/district_financial_reports.html', context)


@login_required
def area_financial_report_detail(request, report_id):
    """View details of a specific area financial report."""
    report = get_object_or_404(AreaFinancialReport, pk=report_id)
    
    # Check if user has permission to view this report
    user = request.user
    if not (user.is_mission_admin or user.is_auditor):
        if user.is_area_executive and user.managed_area != report.area:
            messages.error(request, 'You do not have permission to view this report.')
            return redirect('reports:area_financial_reports')
    
    context = {
        'report': report,
    }
    
    return render(request, 'reports/area_financial_report_detail.html', context)


@login_required
def district_financial_report_detail(request, report_id):
    """View details of a specific district financial report."""
    report = get_object_or_404(DistrictFinancialReport, pk=report_id)
    
    # Check if user has permission to view this report
    user = request.user
    if not (user.is_mission_admin or user.is_auditor):
        if user.is_area_executive and user.managed_area != report.district.area:
            messages.error(request, 'You do not have permission to view this report.')
            return redirect('reports:district_financial_reports')
        elif user.is_district_executive and user.managed_district != report.district:
            messages.error(request, 'You do not have permission to view this report.')
            return redirect('reports:district_financial_reports')
    
    context = {
        'report': report,
    }
    
    return render(request, 'reports/district_financial_report_detail.html', context)


@login_required
@mission_admin_required
def area_financial_report_generate(request):
    """Generate a new area financial report."""
    if request.method == 'POST':
        # Process form data
        area_id = request.POST.get('area')
        month = int(request.POST.get('month'))
        year = int(request.POST.get('year'))
        
        # Check if report already exists
        if AreaFinancialReport.objects.filter(area_id=area_id, month=month, year=year).exists():
            messages.error(request, 'A report for this area and period already exists.')
            return redirect('reports:area_financial_reports')
        
        # Get area
        area = get_object_or_404(Area, pk=area_id)
        
        # Calculate financial data
        # In a real implementation, this would query the ledger for actual data
        # For now, we'll use placeholder values
        opening_balance = 0
        contributions_received = 0
        remittances_received = 0
        transfers_received = 0
        expenditures = 0
        transfers_sent = 0
        
        # Create report
        report = AreaFinancialReport(
            area=area,
            month=month,
            year=year,
            opening_balance=opening_balance,
            contributions_received=contributions_received,
            remittances_received=remittances_received,
            transfers_received=transfers_received,
            expenditures=expenditures,
            transfers_sent=transfers_sent,
            is_generated=True,
            generated_by=request.user,
            generated_at=timezone.now(),
            created_by=request.user,
            updated_by=request.user
        )
        
        # Calculate totals
        report.calculate_totals()
        report.save()
        
        messages.success(request, 'Area financial report generated successfully.')
        return redirect('reports:area_financial_report_detail', report_id=report.id)
    
    # Get data for form
    areas = Area.objects.all().order_by('name')
    
    # Get months for filter
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    
    # Get years for filter (current year and past 5 years)
    current_year = datetime.now().year
    years = list(range(current_year, current_year - 6, -1))
    
    context = {
        'areas': areas,
        'months': months,
        'years': years,
        'current_month': datetime.now().month,
        'current_year': current_year,
    }
    
    return render(request, 'reports/area_financial_report_generate.html', context)


@login_required
@mission_admin_required
def district_financial_report_generate(request):
    """Generate a new district financial report."""
    if request.method == 'POST':
        # Process form data
        district_id = request.POST.get('district')
        month = int(request.POST.get('month'))
        year = int(request.POST.get('year'))
        
        # Check if report already exists
        if DistrictFinancialReport.objects.filter(district_id=district_id, month=month, year=year).exists():
            messages.error(request, 'A report for this district and period already exists.')
            return redirect('reports:district_financial_reports')
        
        # Get district
        district = get_object_or_404(District, pk=district_id)
        
        # Calculate financial data
        # In a real implementation, this would query the ledger for actual data
        # For now, we'll use placeholder values
        opening_balance = 0
        contributions_received = 0
        remittances_received = 0
        transfers_received = 0
        expenditures = 0
        transfers_sent = 0
        
        # Create report
        report = DistrictFinancialReport(
            district=district,
            month=month,
            year=year,
            opening_balance=opening_balance,
            contributions_received=contributions_received,
            remittances_received=remittances_received,
            transfers_received=transfers_received,
            expenditures=expenditures,
            transfers_sent=transfers_sent,
            is_generated=True,
            generated_by=request.user,
            generated_at=timezone.now(),
            created_by=request.user,
            updated_by=request.user
        )
        
        # Calculate totals
        report.calculate_totals()
        report.save()
        
        messages.success(request, 'District financial report generated successfully.')
        return redirect('reports:district_financial_report_detail', report_id=report.id)
    
    # Get data for form
    areas = Area.objects.all().order_by('name')
    districts = District.objects.all().order_by('name')
    
    # Get months for filter
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    
    # Get years for filter (current year and past 5 years)
    current_year = datetime.now().year
    years = list(range(current_year, current_year - 6, -1))
    
    context = {
        'areas': areas,
        'districts': districts,
        'months': months,
        'years': years,
        'current_month': datetime.now().month,
        'current_year': current_year,
    }
    
    return render(request, 'reports/district_financial_report_generate.html', context)


@login_required
def area_financial_report_export(request, report_id):
    """Export an area financial report to CSV."""
    report = get_object_or_404(AreaFinancialReport, pk=report_id)
    
    # Check if user has permission to export this report
    user = request.user
    if not (user.is_mission_admin or user.is_auditor):
        if user.is_area_executive and user.managed_area != report.area:
            messages.error(request, 'You do not have permission to export this report.')
            return redirect('reports:area_financial_reports')
    
    # Generate CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report.area.name}_report_{report.month}_{report.year}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Area Financial Report'])
    writer.writerow([f'Area: {report.area.name}'])
    writer.writerow([f'Period: {calendar.month_name[report.month]} {report.year}'])
    writer.writerow([])
    writer.writerow(['Category', 'Amount'])
    writer.writerow(['Opening Balance', report.opening_balance])
    writer.writerow(['Contributions Received', report.contributions_received])
    writer.writerow(['Remittances Received', report.remittances_received])
    writer.writerow(['Transfers Received', report.transfers_received])
    writer.writerow(['Total Income', report.total_income])
    writer.writerow(['Expenditures', report.expenditures])
    writer.writerow(['Transfers Sent', report.transfers_sent])
    writer.writerow(['Total Expenditure', report.total_expenditure])
    writer.writerow(['Closing Balance', report.closing_balance])
    
    return response


@login_required
def district_financial_report_export(request, report_id):
    """Export a district financial report to CSV."""
    report = get_object_or_404(DistrictFinancialReport, pk=report_id)
    
    # Check if user has permission to export this report
    user = request.user
    if not (user.is_mission_admin or user.is_auditor):
        if user.is_area_executive and user.managed_area != report.district.area:
            messages.error(request, 'You do not have permission to export this report.')
            return redirect('reports:district_financial_reports')
        elif user.is_district_executive and user.managed_district != report.district:
            messages.error(request, 'You do not have permission to export this report.')
            return redirect('reports:district_financial_reports')
    
    # Generate CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report.district.name}_report_{report.month}_{report.year}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['District Financial Report'])
    writer.writerow([f'District: {report.district.name}'])
    writer.writerow([f'Area: {report.district.area.name}'])
    writer.writerow([f'Period: {calendar.month_name[report.month]} {report.year}'])
    writer.writerow([])
    writer.writerow(['Category', 'Amount'])
    writer.writerow(['Opening Balance', report.opening_balance])
    writer.writerow(['Contributions Received', report.contributions_received])
    writer.writerow(['Remittances Received', report.remittances_received])
    writer.writerow(['Transfers Received', report.transfers_received])
    writer.writerow(['Total Income', report.total_income])
    writer.writerow(['Expenditures', report.expenditures])
    writer.writerow(['Transfers Sent', report.transfers_sent])
    writer.writerow(['Total Expenditure', report.total_expenditure])
    writer.writerow(['Closing Balance', report.closing_balance])
    
    return response


@login_required
@mission_admin_required
def area_financial_report_delete(request, report_id):
    """Delete an area financial report."""
    report = get_object_or_404(AreaFinancialReport, pk=report_id)
    
    # Delete the report
    report.delete()
    
    messages.success(request, f'Area Financial Report for {report.area.name} ({report.get_month_display} {report.year}) has been deleted.')
    return redirect('reports:financial')


@login_required
@mission_admin_required
def district_financial_report_delete(request, report_id):
    """Delete a district financial report."""
    report = get_object_or_404(DistrictFinancialReport, pk=report_id)
    
    # Delete the report
    report.delete()
    
    messages.success(request, f'District Financial Report for {report.district.name} ({report.get_month_display} {report.year}) has been deleted.')
    return redirect('reports:financial')
