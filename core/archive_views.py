"""
Archive Views - Date-based historical summaries for SDSCC
REINTERPRETED: Archive views now provide date-based summaries, not year-as-state management.
Historical data is accessed via date filtering from core tables - no data movement or state changes.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q, F, Max, Min
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
def archive_dashboard(request):
    """
    Archive dashboard showing available years as date-based historical summaries.
    REINTERPRETED: Years are derived from actual data dates, not fiscal year state.
    Archive views are date-based summaries, not stateful archives.
    
    ACCESS: Mission admins see all data, branch executives see their branch only,
    members see their personal data only.
    """
    # Check access permissions
    if not (request.user.is_mission_admin or request.user.is_branch_executive or 
            request.user.is_district_executive or request.user.is_area_executive or
            request.user.is_auditor or request.user.is_pastor or request.user.is_regular_member):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    # Get available years from actual data (date-based, not fiscal year based)
    contribution_years = Contribution.objects.dates('date', 'year')
    expenditure_years = Expenditure.objects.dates('date', 'year')
    
    # Combine and get unique years
    all_years = set()
    for year in contribution_years:
        all_years.add(year.year)
    for year in expenditure_years:
        all_years.add(year.year)
    
    # Sort years descending
    available_years = sorted(all_years, reverse=True)
    
    # Generate summary stats for each year
    year_summaries = []
    for year in available_years:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        # Apply role-based filtering
        contrib_filter = {'date__gte': start_date, 'date__lte': end_date}
        expend_filter = {'date__gte': start_date, 'date__lte': end_date}
        
        if request.user.is_branch_executive and request.user.branch:
            contrib_filter['branch'] = request.user.branch
            expend_filter['branch'] = request.user.branch
        elif request.user.is_regular_member:
            # Members see only their personal contributions
            contrib_filter['member'] = request.user
            # Members don't see expenditures
        elif request.user.is_pastor and request.user.branch:
            # Pastors see their branch data
            contrib_filter['branch'] = request.user.branch
            expend_filter['branch'] = request.user.branch
        
        # Calculate year summary using date filtering
        contributions_total = Contribution.objects.filter(**contrib_filter).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Only show expenditures to users who can see them
        if not request.user.is_regular_member:
            expenditures_total = Expenditure.objects.filter(**expend_filter).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        else:
            expenditures_total = Decimal('0.00')
        
        contributions_count = Contribution.objects.filter(**contrib_filter).count()
        
        expenditures_count = Expenditure.objects.filter(**expend_filter).count() if not request.user.is_regular_member else 0
        
        # Check if archive tables have cached data (optional, not authoritative)
        has_archive_data = FinancialArchive.objects.filter(fiscal_year__year=year).exists()
        
        year_summaries.append({
            'year': year,
            'start_date': start_date,
            'end_date': end_date,
            'contributions_total': contributions_total,
            'expenditures_total': expenditures_total,
            'net_balance': contributions_total - expenditures_total,
            'contributions_count': contributions_count,
            'expenditures_count': expenditures_count,
            'has_archive_data': has_archive_data,
        })
    
    context = {
        'year_summaries': year_summaries,
        'page_title': 'Historical Archives - Date-Based Summaries',
        'total_years': len(available_years),
        'current_year': timezone.now().year,
    }
    
    return render(request, 'core/archive_dashboard.html', context)

@login_required
def year_detail(request, year_id):
    """
    Year detail view showing comprehensive date-based summary for a specific year.
    REINTERPRETED: Uses date filtering (Jan 1 - Dec 31) instead of fiscal year state.
    
    ACCESS: Mission admins see all data, branch executives see their branch only,
    members see their personal data only.
    """
    # Check access permissions
    if not (request.user.is_mission_admin or request.user.is_branch_executive or 
            request.user.is_district_executive or request.user.is_area_executive or
            request.user.is_auditor or request.user.is_pastor or request.user.is_regular_member):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    year = int(year_id)
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    # Apply role-based filtering
    contrib_filter = {'date__gte': start_date, 'date__lte': end_date}
    expend_filter = {'date__gte': start_date, 'date__lte': end_date}
    
    if request.user.is_branch_executive and request.user.branch:
        contrib_filter['branch'] = request.user.branch
        expend_filter['branch'] = request.user.branch
    elif request.user.is_regular_member:
        # Members see only their personal contributions
        contrib_filter['member'] = request.user
        # Members don't see expenditures
    elif request.user.is_pastor and request.user.branch:
        # Pastors see their branch data
        contrib_filter['branch'] = request.user.branch
        expend_filter['branch'] = request.user.branch
    
    # Verify year has data
    has_data = Contribution.objects.filter(**contrib_filter).exists() or \
               (not request.user.is_regular_member and Expenditure.objects.filter(**expend_filter).exists())
    
    if not has_data:
        messages.warning(request, f'No data found for year {year}.')
        return redirect('core:archive_dashboard')
    
    # Calculate comprehensive year statistics using date filtering
    # Contributions
    contributions = Contribution.objects.filter(**contrib_filter)
    contributions_total = contributions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    contributions_count = contributions.count()
    
    # Contribution breakdown by type
    contribution_types = contributions.values('contribution_type__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Expenditures (only for non-members)
    if not request.user.is_regular_member:
        expenditures = Expenditure.objects.filter(**expend_filter)
        expenditures_total = expenditures.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        expenditures_count = expenditures.count()
        
        # Expenditure breakdown by category
        expenditure_categories = expenditures.values('category__name').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
    else:
        expenditures = Expenditure.objects.none()
        expenditures_total = Decimal('0.00')
        expenditures_count = 0
        expenditure_categories = []
    
    # Branch-level summaries (filtered by user role)
    branch_summaries = []
    if request.user.is_branch_executive and request.user.branch:
        branches = Branch.objects.filter(id=request.user.branch.id)
    elif request.user.is_pastor and request.user.branch:
        branches = Branch.objects.filter(id=request.user.branch.id)
    elif request.user.is_regular_member:
        # Members don't see branch summaries
        branches = Branch.objects.none()
    else:
        branches = Branch.objects.filter(is_active=True)
    
    for branch in branches:
        branch_contributions = contributions.filter(branch=branch)
        branch_expenditures = expenditures.filter(branch=branch)
        
        if branch_contributions.exists() or branch_expenditures.exists():
            branch_contrib_total = branch_contributions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            branch_expend_total = branch_expenditures.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            branch_summaries.append({
                'branch': branch,
                'contributions_total': branch_contrib_total,
                'expenditures_total': branch_expend_total,
                'net_balance': branch_contrib_total - branch_expend_total,
                'contributions_count': branch_contributions.count(),
                'expenditures_count': branch_expenditures.count(),
            })
    
    # Member statistics
    active_members = Member.objects.filter(
        Q(user__contributions__date__gte=start_date, user__contributions__date__lte=end_date) |
        Q(user__attendance_records__session__date__gte=start_date, user__attendance_records__session__date__lte=end_date)
    ).distinct().count()
    
    # Attendance statistics
    attendance_sessions = AttendanceSession.objects.filter(date__gte=start_date, date__lte=end_date)
    attendance_records = AttendanceRecord.objects.filter(session__date__gte=start_date, session__date__lte=end_date)
    total_attendance = attendance_records.filter(status='present').count()
    
    # Check for cached archive data (optional, not authoritative)
    cached_archive = FinancialArchive.objects.filter(fiscal_year__year=year).first()
    has_cached_data = cached_archive is not None
    
    context = {
        'year': year,
        'start_date': start_date,
        'end_date': end_date,
        
        # Summary data
        'contributions_total': contributions_total,
        'expenditures_total': expenditures_total,
        'net_balance': contributions_total - expenditures_total,
        'contributions_count': contributions_count,
        'expenditures_count': expenditures_count,
        
        # Breakdowns
        'contribution_types': contribution_types,
        'expenditure_categories': expenditure_categories,
        'branch_summaries': branch_summaries,
        
        # Statistics
        'active_members': active_members,
        'attendance_sessions_count': attendance_sessions.count(),
        'total_attendance': total_attendance,
        
        # Archive info
        'has_cached_data': has_cached_data,
        'cached_archive': cached_archive,
        
        'page_title': f'Historical Summary - {year}',
    }
    
    return render(request, 'core/year_detail.html', context)

@login_required
@permission_required('core.manage_archives')
def create_fiscal_year(request):
    """
    Fiscal year creation is permanently disabled.
    The system now uses continuous date-based reporting without year state management.
    Archive views provide date-based summaries instead of stateful year management.
    """
    messages.info(request, 'Fiscal year creation is not needed. The system now uses continuous date-based reporting. Historical data is available through date-based archive views.')
    return redirect('core:archive_dashboard')

@login_required
@permission_required('core.manage_archives')
def archive_fiscal_year_view(request, year_id):
    """
    Fiscal year archiving is permanently disabled.
    No data movement occurs - all historical data remains in core tables.
    Archive views provide date-based summaries without state changes.
    """
    messages.info(request, 'Data archiving is not required. All historical data remains accessible through date-based archive views without data movement.')
    return redirect('core:archive_dashboard')

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
