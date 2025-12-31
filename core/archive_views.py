"""
Archive Views - Year-based data archiving and retrieval for SDSCC
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q, F, Max
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from datetime import datetime, date
from decimal import Decimal
import json

from core.models import SiteSettings, Branch, Area, District, FiscalYear
from core.archive_models import FinancialArchive, MemberArchive, BranchArchive
from contributions.models import Contribution, TitheCommission
from expenditure.models import Expenditure
from members.models import Member
from attendance.models import AttendanceRecord, AttendanceSession

@login_required
@permission_required('core.view_archives')
def archive_dashboard(request):
    """Main archive dashboard showing all fiscal years"""
    active_year = FiscalYear.get_current()
    archived_years = FiscalYear.objects.filter(is_closed=True).order_by('-year')
    
    # Get quick stats for active year if available
    active_stats = {}
    if active_year:
        active_stats = get_active_year_stats(active_year)
    
    context = {
        'active_year': active_year,
        'archived_years': archived_years,
        'active_stats': active_stats,
        'page_title': 'Archive Dashboard'
    }
    return render(request, 'core/archive_dashboard.html', context)

@login_required
@permission_required('core.view_archives')
def year_detail(request, year_id):
    """Detailed view of a specific fiscal year"""
    fiscal_year = get_object_or_404(FiscalYear, id=year_id)
    
    # Get archived data for this year
    financial_archive = FinancialArchive.objects.filter(fiscal_year=fiscal_year).first()
    member_archive = MemberArchive.objects.filter(fiscal_year=fiscal_year).first()
    branch_archives = BranchArchive.objects.filter(fiscal_year=fiscal_year).select_related('branch')
    
    # Group branches by area/district
    branches_by_area = {}
    for archive in branch_archives:
        area_name = archive.branch.area.name if archive.branch.area else 'Unassigned'
        if area_name not in branches_by_area:
            branches_by_area[area_name] = []
        branches_by_area[area_name].append(archive)
    
    context = {
        'fiscal_year': fiscal_year,
        'financial_archive': financial_archive,
        'member_archive': member_archive,
        'branch_archives': branch_archives,
        'branches_by_area': branches_by_area,
        'page_title': f'Archive - {fiscal_year.name}'
    }
    return render(request, 'core/year_detail.html', context)

@login_required
@permission_required('core.manage_archives')
def create_fiscal_year(request):
    """Create a new fiscal year"""
    if request.method == 'POST':
        year = int(request.POST.get('year'))
        start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d').date()
        
        # Archive previous year if exists
        previous_year = FiscalYear.get_current()
        if previous_year:
            archive_fiscal_year(previous_year)
            previous_year.is_current = False
            previous_year.is_closed = True
            previous_year.closed_at = timezone.now()
            previous_year.save()
        
        # Create new fiscal year
        new_year = FiscalYear.objects.create(
            year=year,
            start_date=start_date,
            end_date=end_date,
            is_current=True
        )
        
        # Update site settings
        site_settings = SiteSettings.objects.first()
        if site_settings:
            site_settings.current_fiscal_year = year
            site_settings.save()
        
        messages.success(request, f'New fiscal year "{year}" created successfully!')
        return redirect('core:archive_dashboard')
    
    # Get current year as default
    current_year = datetime.now().year
    default_start = date(current_year, 1, 1)
    default_end = date(current_year, 12, 31)
    
    context = {
        'current_year': current_year,
        'default_start': default_start,
        'default_end': default_end,
        'page_title': 'Create Fiscal Year'
    }
    return render(request, 'core/create_fiscal_year.html', context)

@login_required
@permission_required('core.manage_archives')
def archive_fiscal_year_view(request, year_id):
    """Archive a specific fiscal year"""
    fiscal_year = get_object_or_404(FiscalYear, id=year_id)
    
    if request.method == 'POST':
        try:
            archive_fiscal_year(fiscal_year)
            fiscal_year.is_current = False
            fiscal_year.is_closed = True
            fiscal_year.closed_at = timezone.now()
            fiscal_year.save()
            
            messages.success(request, f'Fiscal year "{fiscal_year}" has been archived successfully!')
            return redirect('core:year_detail', year_id=fiscal_year.id)
        except Exception as e:
            messages.error(request, f'Error archiving fiscal year: {str(e)}')
    
    context = {
        'fiscal_year': fiscal_year,
        'page_title': f'Archive {fiscal_year}'
    }
    return render(request, 'core/archive_fiscal_year.html', context)

def archive_fiscal_year(fiscal_year):
    """Archive all data for a fiscal year"""
    # Archive financial data
    archive_financial_data(fiscal_year)
    
    # Archive member data
    archive_member_data(fiscal_year)
    
    # Archive branch data
    archive_branch_data(fiscal_year)

def archive_financial_data(fiscal_year):
    """Archive financial data for a fiscal year"""
    # Mission-level financial data
    contributions = Contribution.objects.filter(
        date__gte=fiscal_year.start_date,
        date__lte=fiscal_year.end_date
    )
    
    expenditures = Expenditure.objects.filter(
        date__gte=fiscal_year.start_date,
        date__lte=fiscal_year.end_date
    )
    
    commissions = TitheCommission.objects.filter(
        created_at__gte=fiscal_year.start_date,
        created_at__lte=fiscal_year.end_date
    )
    
    # Calculate totals
    mission_total_contributions = contributions.aggregate(total=Sum('amount'))['total'] or 0
    mission_total_expenditures = expenditures.aggregate(total=Sum('amount'))['total'] or 0
    mission_total_tithes = contributions.filter(type='tithe').aggregate(total=Sum('amount'))['total'] or 0
    mission_total_offerings = contributions.filter(type='offering').aggregate(total=Sum('amount'))['total'] or 0
    
    total_commissions = commissions.aggregate(total=Sum('commission_amount'))['total'] or 0
    commissions_paid = commissions.filter(status='paid').aggregate(total=Sum('commission_amount'))['total'] or 0
    commissions_pending = commissions.filter(status='pending').aggregate(total=Sum('commission_amount'))['total'] or 0
    
    # Create or update financial archive
    financial_archive, created = FinancialArchive.objects.update_or_create(
        fiscal_year=fiscal_year,
        defaults={
            'mission_total_contributions': mission_total_contributions,
            'mission_total_expenditures': mission_total_expenditures,
            'mission_total_tithes': mission_total_tithes,
            'mission_total_offerings': mission_total_offerings,
            'total_pastor_commissions': total_commissions,
            'commissions_paid': commissions_paid,
            'commissions_pending': commissions_pending,
            'data_summary': {
                'total_transactions': contributions.count() + expenditures.count(),
                'contribution_types': contributions.values('type').annotate(count=Count('id')).order_by('-count'),
                'expenditure_categories': expenditures.values('category').annotate(total=Sum('amount')).order_by('-total'),
            }
        }
    )

def archive_member_data(fiscal_year):
    """Archive member statistics for a fiscal year"""
    # Get member statistics
    total_members = Member.objects.filter(created_at__lte=fiscal_year.end_date).count()
    new_members = Member.objects.filter(
        created_at__gte=fiscal_year.start_date,
        created_at__lte=fiscal_year.end_date
    ).count()
    
    # Attendance statistics
    attendance_sessions = AttendanceSession.objects.filter(
        date__gte=fiscal_year.start_date,
        date__lte=fiscal_year.end_date
    )
    
    total_services = attendance_sessions.count()
    attendance_records = AttendanceRecord.objects.filter(
        session__in=attendance_sessions
    )
    
    average_attendance = attendance_records.aggregate(
        avg=Avg('session__attendance_count')
    )['avg'] or 0
    
    highest_attendance = attendance_sessions.aggregate(
        max=Max('attendance_count')
    )['max'] or 0
    
    lowest_attendance = attendance_sessions.aggregate(
        min=Min('attendance_count')
    )['min'] or 0
    
    # Member distribution
    members_by_branch = dict(
        Member.objects.filter(created_at__lte=fiscal_year.end_date)
        .values('branch__name')
        .annotate(count=Count('id'))
        .order_by('-count')
        .values_list('branch__name', 'count')
    )
    
    members_by_area = dict(
        Member.objects.filter(created_at__lte=fiscal_year.end_date, branch__area__isnull=False)
        .values('branch__area__name')
        .annotate(count=Count('id'))
        .order_by('-count')
        .values_list('branch__area__name', 'count')
    )
    
    members_by_district = dict(
        Member.objects.filter(created_at__lte=fiscal_year.end_date, branch__area__district__isnull=False)
        .values('branch__area__district__name')
        .annotate(count=Count('id'))
        .order_by('-count')
        .values_list('branch__area__district__name', 'count')
    )
    
    # Create or update member archive
    member_archive, created = MemberArchive.objects.update_or_create(
        fiscal_year=fiscal_year,
        defaults={
            'total_members': total_members,
            'new_members': new_members,
            'total_services': total_services,
            'average_attendance': average_attendance,
            'highest_attendance': highest_attendance,
            'lowest_attendance': lowest_attendance,
            'members_by_branch': members_by_branch,
            'members_by_area': members_by_area,
            'members_by_district': members_by_district,
            'data_summary': {
                'attendance_trends': get_attendance_trends(fiscal_year),
                'growth_rate': calculate_growth_rate(fiscal_year),
            }
        }
    )

def archive_branch_data(fiscal_year):
    """Archive branch-specific data for a fiscal year"""
    branches = Branch.objects.all()
    
    for branch in branches:
        # Branch financial data
        branch_contributions = Contribution.objects.filter(
            branch=branch,
            date__gte=fiscal_year.start_date,
            date__lte=fiscal_year.end_date
        )
        
        branch_expenditures = Expenditure.objects.filter(
            branch=branch,
            date__gte=fiscal_year.start_date,
            date__lte=fiscal_year.end_date
        )
        
        # Calculate branch totals
        total_contributions = branch_contributions.aggregate(total=Sum('amount'))['total'] or 0
        total_tithes = branch_contributions.filter(type='tithe').aggregate(total=Sum('amount'))['total'] or 0
        total_offerings = branch_contributions.filter(type='offering').aggregate(total=Sum('amount'))['total'] or 0
        total_expenditures = branch_expenditures.aggregate(total=Sum('amount'))['total'] or 0
        
        # Branch member data
        branch_members = Member.objects.filter(branch=branch, created_at__lte=fiscal_year.end_date)
        new_members = branch_members.filter(created_at__gte=fiscal_year.start_date).count()
        
        # Branch attendance
        branch_attendance = AttendanceSession.objects.filter(
            branch=branch,
            date__gte=fiscal_year.start_date,
            date__lte=fiscal_year.end_date
        )
        
        average_attendance = branch_attendance.aggregate(
            avg=Avg('attendance_count')
        )['avg'] or 0
        
        # Pastor commission data
        pastor_commissions = PastorCommission.objects.filter(
            branch=branch,
            created_at__gte=fiscal_year.start_date,
            created_at__lte=fiscal_year.end_date
        )
        
        commission_earned = pastor_commissions.aggregate(total=Sum('commission_amount'))['total'] or 0
        commission_paid = pastor_commissions.filter(status='paid').aggregate(total=Sum('commission_amount'))['total'] or 0
        
        # Performance metrics
        tithe_target = branch.monthly_tithe_target * 12  # Annual target
        tithe_achievement = (total_tithes / tithe_target * 100) if tithe_target > 0 else 0
        
        # Create or update branch archive
        BranchArchive.objects.update_or_create(
            fiscal_year=fiscal_year,
            branch=branch,
            defaults={
                'total_contributions': total_contributions,
                'total_tithes': total_tithes,
                'total_offerings': total_offerings,
                'total_expenditures': total_expenditures,
                'member_count': branch_members.count(),
                'new_members': new_members,
                'average_attendance': average_attendance,
                'pastor_name': branch.pastor.get_full_name() if branch.pastor else '',
                'pastor_commission_earned': commission_earned,
                'pastor_commission_paid': commission_paid,
                'tithe_target_achievement': tithe_achievement,
                'data_summary': {
                    'monthly_performance': get_monthly_branch_performance(branch, fiscal_year),
                    'top_contributors': get_top_branch_contributors(branch, fiscal_year),
                }
            }
        )

def get_active_year_stats(active_year):
    """Get statistics for the currently active fiscal year"""
    # Similar to archive functions but for active year
    contributions = Contribution.objects.filter(
        date__gte=active_year.start_date,
        date__lte=active_year.end_date
    )
    
    members = Member.objects.filter(created_at__lte=active_year.end_date)
    
    return {
        'total_contributions': contributions.aggregate(total=Sum('amount'))['total'] or 0,
        'total_members': members.count(),
        'new_members': members.filter(created_at__gte=active_year.start_date).count(),
        'total_services': AttendanceSession.objects.filter(
            date__gte=active_year.start_date,
            date__lte=active_year.end_date
        ).count(),
    }

def get_attendance_trends(fiscal_year):
    """Get attendance trends for the fiscal year"""
    # Implementation for attendance trends
    return {}

def calculate_growth_rate(fiscal_year):
    """Calculate growth rate compared to previous year"""
    # Implementation for growth rate calculation
    return {}

def get_monthly_branch_performance(branch, fiscal_year):
    """Get monthly performance data for a branch"""
    # Implementation for monthly performance
    return {}

def get_top_branch_contributors(branch, fiscal_year):
    """Get top contributors for a branch"""
    # Implementation for top contributors
    return {}
