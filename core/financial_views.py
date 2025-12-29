"""
Financial Tracking Views for Branch Executives and Pastors
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, F
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import calendar

from core.models import Branch, FiscalYear
from contributions.models import Contribution, Remittance, ContributionType
from expenditure.models import Expenditure
from payroll.models import PayrollRun, PaySlip


@login_required
def branch_financial_statistics(request):
    """Comprehensive financial statistics for branch executive/pastor/auditor."""
    user = request.user

    # Determine branches this user can see
    if user.is_mission_admin or user.is_auditor:
        branches = Branch.objects.filter(is_active=True)
        selected_branch_id = request.GET.get('branch')
        if selected_branch_id:
            branch = get_object_or_404(Branch, pk=selected_branch_id)
        else:
            branch = None
    elif user.is_area_executive and user.managed_area:
        branches = Branch.objects.filter(district__area=user.managed_area, is_active=True)
        branch = user.branch if user.branch else branches.first()
    elif user.is_district_executive and user.managed_district:
        branches = Branch.objects.filter(district=user.managed_district, is_active=True)
        branch = user.branch if user.branch else branches.first()
    elif user.is_branch_executive or user.is_pastor:
        branch = user.branch
        branches = Branch.objects.filter(id=branch.id) if branch else Branch.objects.none()
    else:
        return render(request, '403.html', status=403)
    
    # Get date range
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = request.GET.get('month')
    
    if month:
        month = int(month)
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        period_type = 'monthly'
    else:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        period_type = 'yearly'
    
    fiscal_year = FiscalYear.get_current()
    
    # Initialize statistics
    stats = {
        'period_type': period_type,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month] if month else None,
        'start_date': start_date,
        'end_date': end_date,
        'branches': branches,
        'selected_branch': branch,
    }
    
    if branch:
        # Contributions by type
        contributions = Contribution.objects.filter(
            branch=branch,
            date__gte=start_date,
            date__lte=end_date,
            fiscal_year=fiscal_year
        )
        
        contributions_by_type = contributions.values('contribution_type__name', 'contribution_type__category').annotate(
            total=Sum('amount'),
            count=Sum('amount')  # Using Sum as count placeholder
        ).order_by('-total')
        
        # Calculate mission remittance (10% of tithe)
        tithe_type = ContributionType.objects.filter(category='tithe', is_active=True).first()
        total_tithe = contributions.filter(contribution_type=tithe_type).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        mission_remittance = total_tithe * Decimal('0.10')
        
        # Expenditures
        expenditures = Expenditure.objects.filter(
            branch=branch,
            date__gte=start_date,
            date__lte=end_date,
            fiscal_year=fiscal_year
        )
        
        expenditures_by_category = expenditures.values('category').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        # Payroll
        payroll_runs = PayrollRun.objects.filter(
            payslips__staff__user__branch=branch,
            year=year
        ).distinct()
        
        if month:
            payroll_runs = payroll_runs.filter(month=month)
        
        payroll_total = PaySlip.objects.filter(
            payroll_run__in=payroll_runs,
            staff__user__branch=branch
        ).aggregate(total=Sum('net_pay'))['total'] or Decimal('0')
        
        # Remittances sent
        remittances = Remittance.objects.filter(
            branch=branch
        )
        
        # Filter by date range using month/year
        if period_type == 'yearly':
            remittances = remittances.filter(year=year)
        elif period_type == 'monthly':
            remittances = remittances.filter(year=year, month=month)
        
        total_remitted = remittances.aggregate(total=Sum('amount_sent'))['total'] or Decimal('0')
        
        # Calculate coffer balance
        total_income = contributions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_expenses = expenditures.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_payroll = payroll_total
        total_remittances = total_remitted
        
        # Starting balance (simplified - would need historical data for accuracy)
        starting_balance = branch.local_balance or Decimal('0')
        
        # Current coffer calculation
        coffer_balance = starting_balance + total_income - total_expenses - total_payroll - total_remittances
        
        # Monthly trend data
        monthly_data = []
        if period_type == 'yearly':
            for m in range(1, 13):
                month_start = date(year, m, 1)
                if m == 12:
                    month_end = date(year + 1, 1, 1) - timedelta(days=1)
                else:
                    month_end = date(year, m + 1, 1) - timedelta(days=1)
                
                month_contributions = Contribution.objects.filter(
                    branch=branch,
                    date__gte=month_start,
                    date__lte=month_end,
                    fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
                
                month_expenditures = Expenditure.objects.filter(
                    branch=branch,
                    date__gte=month_start,
                    date__lte=month_end,
                    fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
                
                monthly_data.append({
                    'month': m,
                    'month_name': calendar.month_name[m][:3],
                    'contributions': float(month_contributions),
                    'expenditures': float(month_expenditures),
                    'net': float(month_contributions - month_expenditures)
                })
        
        # Update stats
        stats.update({
            'total_contributions': total_income,
            'total_expenditures': total_expenses,
            'total_payroll': payroll_total,
            'total_remittances': total_remittances,
            'mission_remittance': mission_remittance,
            'coffer_balance': coffer_balance,
            'starting_balance': starting_balance,
            'contributions_by_type': contributions_by_type,
            'expenditures_by_category': expenditures_by_category,
            'remittances': remittances.order_by('-payment_date')[:10],
            'monthly_data': monthly_data,
            'tithe_total': total_tithe,
            'other_contributions': total_income - total_tithe,
        })
    
    # Available years for filter
    available_years = list(range(today.year - 3, today.year + 2))

    # Get site settings for currency
    from core.models import SiteSettings
    site_settings = SiteSettings.get_settings()

    context = {
        **stats,
        'available_years': available_years,
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
        'site_settings': site_settings,
    }

    return render(request, 'core/branch_financial_statistics.html', context)
@login_required
def auditor_branch_statistics(request):
    """Auditor view of all branches financial statistics."""
    if not (request.user.is_auditor or request.user.is_mission_admin):
        return render(request, '403.html', status=403)
    
    # Get filters
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = request.GET.get('month')
    area_id = request.GET.get('area')
    district_id = request.GET.get('district')
    
    if month:
        month = int(month)
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        period_type = 'monthly'
    else:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        period_type = 'yearly'
    
    fiscal_year = FiscalYear.get_current()
    
    # Filter branches
    branches = Branch.objects.filter(is_active=True)
    
    if area_id:
        branches = branches.filter(district__area_id=area_id)
    if district_id:
        branches = branches.filter(district_id=district_id)
    
    # Collect statistics for all branches
    branches_stats = []
    grand_total = {
        'contributions': Decimal('0'),
        'expenditures': Decimal('0'),
        'payroll': Decimal('0'),
        'remittances': Decimal('0'),
        'coffer_balance': Decimal('0'),
    }
    
    for branch in branches:
        # Contributions
        contributions = Contribution.objects.filter(
            branch=branch,
            date__gte=start_date,
            date__lte=end_date,
            fiscal_year=fiscal_year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Expenditures
        expenditures = Expenditure.objects.filter(
            branch=branch,
            date__gte=start_date,
            date__lte=end_date,
            fiscal_year=fiscal_year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Payroll
        payroll_runs = PayrollRun.objects.filter(
            payslips__staff__user__branch=branch,
            year=year
        ).distinct()
        if month:
            payroll_runs = payroll_runs.filter(month=month)
        
        payroll = PaySlip.objects.filter(
            payroll_run__in=payroll_runs,
            staff__user__branch=branch
        ).aggregate(total=Sum('net_pay'))['total'] or Decimal('0')
        
        # Remittances
        remittances = Remittance.objects.filter(
            branch=branch
        )
        
        # Filter by date range using month/year
        if period_type == 'yearly':
            remittances = remittances.filter(year=year)
        elif period_type == 'monthly':
            remittances = remittances.filter(year=year, month=month)
        
        remittances_total = remittances.aggregate(total=Sum('amount_sent'))['total'] or Decimal('0')
        
        # Coffer balance
        coffer_balance = branch.local_balance or Decimal('0')
        
        branch_stats = {
            'branch': branch,
            'contributions': contributions,
            'expenditures': expenditures,
            'payroll': payroll,
            'remittances': remittances_total,
            'coffer_balance': coffer_balance,
            'net_position': contributions - expenditures - payroll - remittances_total,
        }
        
        branches_stats.append(branch_stats)
        
        # Update grand totals
        grand_total['contributions'] += contributions
        grand_total['expenditures'] += expenditures
        grand_total['payroll'] += payroll
        grand_total['remittances'] += remittances_total
        grand_total['coffer_balance'] += coffer_balance
    
    # Sort by total contributions
    branches_stats.sort(key=lambda x: x['contributions'], reverse=True)
    
    context = {
        'period_type': period_type,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month] if month else None,
        'branches_stats': branches_stats,
        'grand_total': grand_total,
        'areas': Branch.objects.values('district__area__id', 'district__area__name').filter(district__area__isnull=False).distinct(),
        'districts': Branch.objects.values('district__id', 'district__name').filter(district__isnull=False).distinct(),
        'selected_area': area_id,
        'selected_district': district_id,
        'available_years': list(range(today.year - 3, today.year + 2)),
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
    }
    
    return render(request, 'core/auditor_branch_statistics.html', context)
