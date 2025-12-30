"""
Mission Financial Views - Track mission-level finances separately from branch finances
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, Count
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import calendar

from core.models import Branch, Area, District, FiscalYear, SiteSettings
from contributions.models import Remittance, Contribution
from expenditure.models import Expenditure, ExpenditureCategory
from payroll.models import PayrollRun, PaySlip


@login_required
def mission_financial_dashboard(request):
    """Mission financial dashboard - shows mission-level finances."""
    # Only mission admin can access
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied. Mission Admin role required.')
        return redirect('core:dashboard')
    
    # Get date parameters
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = request.GET.get('month')
    
    if month:
        month = int(month)
        # Monthly view
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        period_type = 'monthly'
        period_name = f"{calendar.month_name[month]} {year}"
    else:
        # Yearly view
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        period_type = 'yearly'
        period_name = f"Year {year}"
    
    # Get fiscal year
    fiscal_year = FiscalYear.get_current()
    
    # INCOME: Remittances received from branches
    remittances = Remittance.objects.filter(
        status__in=['verified', 'sent'],
        payment_date__gte=start_date,
        payment_date__lte=end_date
    ) if period_type == 'monthly' else Remittance.objects.filter(
        status__in=['verified', 'sent'],
        year=year
    )
    
    total_remittances_received = remittances.aggregate(total=Sum('amount_sent'))['total'] or Decimal('0')
    remittances_count = remittances.count()
    
    # Branch-wise remittance breakdown
    branch_remittances = remittances.values(
        'branch__name', 'branch__id'
    ).annotate(
        total=Sum('amount_sent'),
        count=Count('id')
    ).order_by('-total')[:10]  # Top 10 branches
    
    # EXPENDITURES: Mission-level expenditures
    mission_expenditures = Expenditure.objects.filter(
        level='mission',
        date__gte=start_date,
        date__lte=end_date,
        fiscal_year=fiscal_year,
        status__in=['approved', 'paid']
    )
    
    total_mission_expenditures = mission_expenditures.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    expenditures_count = mission_expenditures.count()
    
    # Expenditure by category
    expenditures_by_category = mission_expenditures.values(
        'category__name'
    ).annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # MISSION BALANCE CALCULATION
    # Note: This is a simplified calculation. In production, you might want to track this in a separate model
    mission_balance = total_remittances_received - total_mission_expenditures
    
    # PENDING REMITTANCES (not yet received)
    pending_remittances = Remittance.objects.filter(
        status='pending',
        year=year
    )
    if period_type == 'monthly':
        pending_remittances = pending_remittances.filter(month=month)
    
    total_pending = pending_remittances.aggregate(total=Sum('amount_due'))['total'] or Decimal('0')
    pending_count = pending_remittances.count()
    
    # Get site settings for currency
    site_settings = SiteSettings.get_settings()
    
    # Available years for filter
    available_years = list(range(today.year - 3, today.year + 2))
    
    context = {
        'period_type': period_type,
        'period_name': period_name,
        'year': year,
        'month': month,
        'start_date': start_date,
        'end_date': end_date,
        
        # Income
        'total_remittances_received': total_remittances_received,
        'remittances_count': remittances_count,
        'branch_remittances': branch_remittances,
        
        # Expenditures
        'total_mission_expenditures': total_mission_expenditures,
        'expenditures_count': expenditures_count,
        'expenditures_by_category': expenditures_by_category,
        
        # Balance
        'mission_balance': mission_balance,
        
        # Pending
        'total_pending': total_pending,
        'pending_count': pending_count,
        
        # Filters
        'available_years': available_years,
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
        'site_settings': site_settings,
    }
    
    return render(request, 'core/mission_financial_dashboard.html', context)


@login_required
def mission_expenditure_list(request):
    """List all mission-level expenditures."""
    # Only mission admin can access
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied. Mission Admin role required.')
        return redirect('core:dashboard')

    # Get fiscal year
    fiscal_year = FiscalYear.get_current()

    # Get all mission expenditures
    expenditures = Expenditure.objects.filter(
        level='mission',
        fiscal_year=fiscal_year
    ).select_related('category', 'created_by', 'approved_by').order_by('-date')

    # Filters
    category_id = request.GET.get('category')
    status = request.GET.get('status')
    year = request.GET.get('year')
    month = request.GET.get('month')

    if category_id:
        expenditures = expenditures.filter(category_id=category_id)

    if status:
        expenditures = expenditures.filter(status=status)

    if year:
        expenditures = expenditures.filter(date__year=int(year))

    if month:
        expenditures = expenditures.filter(date__month=int(month))

    # Calculate totals
    totals = expenditures.aggregate(
        total=Sum('amount'),
        approved=Sum('amount', filter=Q(status='approved')),
        paid=Sum('amount', filter=Q(status='paid')),
        pending=Sum('amount', filter=Q(status='pending'))
    )

    # Get categories for filter
    categories = ExpenditureCategory.objects.filter(is_active=True).order_by('name')

    # Get site settings
    site_settings = SiteSettings.get_settings()

    # Available years
    today = date.today()
    available_years = list(range(today.year - 3, today.year + 2))

    context = {
        'expenditures': expenditures,
        'categories': categories,
        'totals': totals,
        'selected_category': category_id,
        'selected_status': status,
        'selected_year': year,
        'selected_month': month,
        'available_years': available_years,
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
        'site_settings': site_settings,
    }

    return render(request, 'core/mission_expenditure_list.html', context)


@login_required
def mission_remittance_tracking(request):
    """Track remittances from all branches with hierarchical filtering."""
    # Only mission admin can access
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied. Mission Admin role required.')
        return redirect('core:dashboard')

    # Get date parameters
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = request.GET.get('month')

    # Get hierarchical filter parameters
    area_id = request.GET.get('area')
    district_id = request.GET.get('district')
    branch_id = request.GET.get('branch')

    # Get all hierarchy data for filters
    areas = Area.objects.filter(is_active=True).order_by('name')
    districts = District.objects.filter(is_active=True).order_by('name')
    branches = Branch.objects.filter(is_active=True).order_by('name')

    # Apply hierarchical filtering
    if area_id:
        districts = districts.filter(area_id=area_id)
        branches = branches.filter(district__area_id=area_id)
    
    if district_id:
        branches = branches.filter(district_id=district_id)
    
    if branch_id:
        branches = branches.filter(id=branch_id)

    # Get remittances for filtered branches
    remittances = Remittance.objects.filter(year=year, branch__in=branches)

    if month:
        month = int(month)
        remittances = remittances.filter(month=month)

    # Branch-wise summary
    branch_summary = []
    for branch in branches:
        branch_remittances = remittances.filter(branch=branch)

        total_due = branch_remittances.aggregate(total=Sum('amount_due'))['total'] or Decimal('0')
        total_sent = branch_remittances.aggregate(total=Sum('amount_sent'))['total'] or Decimal('0')
        total_verified = branch_remittances.filter(status='verified').aggregate(total=Sum('amount_sent'))['total'] or Decimal('0')
        total_pending = branch_remittances.filter(status='pending').aggregate(total=Sum('amount_due'))['total'] or Decimal('0')

        branch_summary.append({
            'branch': branch,
            'total_due': total_due,
            'total_sent': total_sent,
            'total_verified': total_verified,
            'total_pending': total_pending,
            'outstanding': total_due - total_sent,
            'remittances': branch_remittances.order_by('-month')
        })

    # Overall totals
    overall_totals = {
        'total_due': sum(b['total_due'] for b in branch_summary),
        'total_sent': sum(b['total_sent'] for b in branch_summary),
        'total_verified': sum(b['total_verified'] for b in branch_summary),
        'total_pending': sum(b['total_pending'] for b in branch_summary),
        'total_outstanding': sum(b['outstanding'] for b in branch_summary),
    }

    # Get site settings
    site_settings = SiteSettings.get_settings()

    # Available years
    available_years = list(range(today.year - 3, today.year + 2))

    context = {
        'branch_summary': branch_summary,
        'overall_totals': overall_totals,
        'year': year,
        'month': month,
        'available_years': available_years,
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
        'site_settings': site_settings,
        
        # Hierarchy data for filters
        'areas': areas,
        'districts': districts,
        'branches': branches,
        'area_id': area_id,
        'district_id': district_id,
        'branch_id': branch_id,
    }

    return render(request, 'core/mission_remittance_tracking.html', context)


@login_required
def branch_financial_overview(request):
    """Overview of all branch-level finances (local finances)."""
    # Only mission admin can access
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied. Mission Admin role required.')
        return redirect('core:dashboard')

    # Get date parameters
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = request.GET.get('month')

    # Get hierarchical filter parameters
    area_id = request.GET.get('area')
    district_id = request.GET.get('district')
    branch_id = request.GET.get('branch')

    # Get all hierarchy data for filters
    areas = Area.objects.filter(is_active=True).order_by('name')
    districts = District.objects.filter(is_active=True).order_by('name')
    branches = Branch.objects.filter(is_active=True).order_by('name')

    # Apply hierarchical filtering
    if area_id:
        districts = districts.filter(area_id=area_id)
        branches = branches.filter(district__area_id=area_id)
    
    if district_id:
        branches = branches.filter(district_id=district_id)
    
    if branch_id:
        branches = branches.filter(id=branch_id)

    # Get fiscal year
    fiscal_year = FiscalYear.get_current()

    # BRANCH-LEVEL CONTRIBUTIONS (what stays at branch level)
    # These are contributions that are NOT sent to mission
    branch_contributions = Contribution.objects.filter(
        branch__in=branches,
        date__year=year,
        fiscal_year=fiscal_year
    )

    if month:
        month = int(month)
        branch_contributions = branch_contributions.filter(date__month=month)

    # Calculate total contributions that stayed at branch level
    total_branch_contributions = branch_contributions.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # BRANCH-LEVEL EXPENDITURES (local branch expenses)
    branch_expenditures = Expenditure.objects.filter(
        level='branch',
        branch__in=branches,
        date__year=year,
        fiscal_year=fiscal_year
    )

    if month:
        branch_expenditures = branch_expenditures.filter(date__month=month)

    total_branch_expenditures = branch_expenditures.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # Branch-wise summary
    branch_summary = []
    for branch in branches:
        # Branch contributions for this period
        branch_contrib = branch_contributions.filter(branch=branch).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Branch expenditures for this period
        branch_exp = branch_expenditures.filter(branch=branch).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Local balance calculation
        local_balance = branch_contrib - branch_exp

        branch_summary.append({
            'branch': branch,
            'total_contributions': branch_contrib,
            'total_expenditures': branch_exp,
            'local_balance': local_balance,
            'contribution_count': branch_contributions.filter(branch=branch).count(),
            'expenditure_count': branch_expenditures.filter(branch=branch).count(),
        })

    # Overall totals
    overall_totals = {
        'total_contributions': sum(b['total_contributions'] for b in branch_summary),
        'total_expenditures': sum(b['total_expenditures'] for b in branch_summary),
        'total_local_balance': sum(b['local_balance'] for b in branch_summary),
    }

    # Get site settings
    site_settings = SiteSettings.get_settings()

    # Available years
    available_years = list(range(today.year - 3, today.year + 2))

    context = {
        'branch_summary': branch_summary,
        'overall_totals': overall_totals,
        'year': year,
        'month': month,
        'available_years': available_years,
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
        'site_settings': site_settings,
        
        # Hierarchy data for filters
        'areas': areas,
        'districts': districts,
        'branches': branches,
        'area_id': area_id,
        'district_id': district_id,
        'branch_id': branch_id,
    }

    return render(request, 'core/branch_financial_overview.html', context)

