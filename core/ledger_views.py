"""
Ledger Views - Financial reporting based on ledger entries.
Provides views for Mission Admin and Auditor to see financial positions.
"""

from decimal import Decimal
from datetime import date, timedelta
from calendar import monthrange, month_name

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.http import JsonResponse

from core.models import Branch, Area, District
from core.ledger_models import LedgerEntry
from core.ledger_service import LedgerService


@login_required
def ledger_dashboard(request):
    """
    Main ledger dashboard showing financial positions.
    Mission Admin and Auditor only.
    """
    if not (request.user.is_mission_admin or request.user.is_auditor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    today = date.today()
    
    # Mission financial position
    mission_cash = LedgerService.get_mission_cash_balance()
    mission_receivables = LedgerService.get_mission_receivables()
    mission_total_position = mission_cash + mission_receivables
    
    # Receivables by branch
    receivables_by_branch = LedgerService.get_receivables_by_branch()
    
    # Branch summaries
    branches = Branch.objects.filter(is_active=True).select_related('district__area')
    branch_summaries = []
    
    for branch in branches:
        cash = LedgerService.get_branch_cash_balance(branch)
        payables = LedgerService.get_branch_payables(branch)
        spendable = cash - payables
        
        branch_summaries.append({
            'branch': branch,
            'cash': cash,
            'payables': payables,
            'spendable': spendable,
            'area': branch.district.area.name,
            'district': branch.district.name,
        })
    
    # Sort by payables (highest first - branches that owe most)
    branch_summaries.sort(key=lambda x: x['payables'], reverse=True)
    
    # Monthly summary for current month
    monthly_summary = LedgerService.get_monthly_summary(
        LedgerEntry.OwnerType.MISSION,
        today.month,
        today.year
    )
    
    # Get areas and districts for filters
    areas = Area.objects.filter(is_active=True).order_by('name')
    districts = District.objects.filter(is_active=True).order_by('name')
    
    context = {
        'mission_cash': mission_cash,
        'mission_receivables': mission_receivables,
        'mission_total_position': mission_total_position,
        'receivables_by_branch': receivables_by_branch,
        'branch_summaries': branch_summaries,
        'monthly_summary': monthly_summary,
        'current_month': month_name[today.month],
        'current_year': today.year,
        'areas': areas,
        'districts': districts,
    }
    
    return render(request, 'core/ledger_dashboard.html', context)


@login_required
def mission_financial_position(request):
    """
    Detailed Mission financial position view.
    Shows CASH vs RECEIVABLE clearly.
    """
    if not (request.user.is_mission_admin or request.user.is_auditor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Get date range from request
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    
    start_date = date(year, month, 1)
    _, last_day = monthrange(year, month)
    end_date = date(year, month, last_day)
    
    # Mission CASH entries
    cash_entries = LedgerEntry.objects.filter(
        owner_type=LedgerEntry.OwnerType.MISSION,
        entry_type=LedgerEntry.EntryType.CASH,
        entry_date__gte=start_date,
        entry_date__lte=end_date,
        status=LedgerEntry.Status.ACTIVE
    ).order_by('-entry_date', '-created_at')
    
    # Mission RECEIVABLE entries
    receivable_entries = LedgerEntry.objects.filter(
        owner_type=LedgerEntry.OwnerType.MISSION,
        entry_type=LedgerEntry.EntryType.RECEIVABLE,
        entry_date__gte=start_date,
        entry_date__lte=end_date,
        status=LedgerEntry.Status.ACTIVE
    ).order_by('-entry_date', '-created_at')
    
    # Balances
    cash_balance = LedgerService.get_mission_cash_balance(as_of_date=end_date)
    receivables_balance = LedgerService.get_mission_receivables(as_of_date=end_date)
    
    # Monthly totals
    cash_in = cash_entries.filter(amount__gt=0).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    cash_out = cash_entries.filter(amount__lt=0).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Year options for filter
    years = list(range(date.today().year - 5, date.today().year + 1))
    
    context = {
        'cash_entries': cash_entries,
        'receivable_entries': receivable_entries,
        'cash_balance': cash_balance,
        'receivables_balance': receivables_balance,
        'total_position': cash_balance + receivables_balance,
        'cash_in': cash_in,
        'cash_out': abs(cash_out),
        'net_cash_flow': cash_in + cash_out,
        'selected_year': year,
        'selected_month': month,
        'month_name': month_name[month],
        'years': years,
        'months': [(i, month_name[i]) for i in range(1, 13)],
    }
    
    return render(request, 'core/mission_financial_position.html', context)


@login_required
def branch_financial_position(request, branch_id=None):
    """
    Branch financial position view.
    Shows branch CASH, PAYABLE, and spendable amount.
    """
    # Determine which branch to show
    if branch_id:
        branch = get_object_or_404(Branch, pk=branch_id)
        # Check permissions
        if not (request.user.is_mission_admin or request.user.is_auditor):
            if request.user.branch != branch:
                messages.error(request, 'Access denied.')
                return redirect('core:dashboard')
    else:
        if request.user.is_mission_admin or request.user.is_auditor:
            messages.error(request, 'Please select a branch.')
            return redirect('core:ledger_dashboard')
        branch = request.user.branch
        if not branch:
            messages.error(request, 'No branch assigned.')
            return redirect('core:dashboard')
    
    # Get date range
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    
    start_date = date(year, month, 1)
    _, last_day = monthrange(year, month)
    end_date = date(year, month, last_day)
    
    # Branch ledger entries
    cash_entries = LedgerEntry.objects.filter(
        owner_type=LedgerEntry.OwnerType.BRANCH,
        owner_branch=branch,
        entry_type=LedgerEntry.EntryType.CASH,
        entry_date__gte=start_date,
        entry_date__lte=end_date,
        status=LedgerEntry.Status.ACTIVE
    ).order_by('-entry_date', '-created_at')
    
    payable_entries = LedgerEntry.objects.filter(
        owner_type=LedgerEntry.OwnerType.BRANCH,
        owner_branch=branch,
        entry_type=LedgerEntry.EntryType.PAYABLE,
        entry_date__gte=start_date,
        entry_date__lte=end_date,
        status=LedgerEntry.Status.ACTIVE
    ).order_by('-entry_date', '-created_at')
    
    # Balances
    cash_balance = LedgerService.get_branch_cash_balance(branch, as_of_date=end_date)
    payables_balance = LedgerService.get_branch_payables(branch, as_of_date=end_date)
    spendable = cash_balance - payables_balance
    
    # Monthly summary
    monthly_summary = LedgerService.get_monthly_summary(
        LedgerEntry.OwnerType.BRANCH,
        month,
        year,
        owner_branch=branch
    )
    
    years = list(range(date.today().year - 5, date.today().year + 1))
    
    context = {
        'branch': branch,
        'cash_entries': cash_entries,
        'payable_entries': payable_entries,
        'cash_balance': cash_balance,
        'payables_balance': payables_balance,
        'spendable': spendable,
        'monthly_summary': monthly_summary,
        'selected_year': year,
        'selected_month': month,
        'month_name': month_name[month],
        'years': years,
        'months': [(i, month_name[i]) for i in range(1, 13)],
    }
    
    return render(request, 'core/branch_financial_position.html', context)


@login_required
def outstanding_remittances(request):
    """
    View showing all branches with outstanding remittances.
    Mission Admin and Auditor only.
    """
    if not (request.user.is_mission_admin or request.user.is_auditor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Get all branches with payables > 0
    branches = Branch.objects.filter(is_active=True).select_related('district__area')
    
    outstanding = []
    total_outstanding = Decimal('0')
    
    for branch in branches:
        payables = LedgerService.get_branch_payables(branch)
        if payables > 0:
            outstanding.append({
                'branch': branch,
                'area': branch.district.area.name,
                'district': branch.district.name,
                'amount_owed': payables,
            })
            total_outstanding += payables
    
    # Sort by amount owed (highest first)
    outstanding.sort(key=lambda x: x['amount_owed'], reverse=True)
    
    context = {
        'outstanding': outstanding,
        'total_outstanding': total_outstanding,
        'branch_count': len(outstanding),
    }
    
    return render(request, 'core/outstanding_remittances.html', context)


@login_required
def ledger_audit_trail(request):
    """
    Full audit trail of all ledger entries.
    Auditor and Mission Admin only.
    """
    if not (request.user.is_mission_admin or request.user.is_auditor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Filters
    owner_type = request.GET.get('owner_type', '')
    entry_type = request.GET.get('entry_type', '')
    source_type = request.GET.get('source_type', '')
    branch_id = request.GET.get('branch', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    entries = LedgerEntry.objects.all().select_related(
        'owner_branch', 'owner_area', 'owner_district',
        'counterparty_branch', 'contribution', 'expenditure', 'remittance'
    ).order_by('-entry_date', '-created_at')
    
    if owner_type:
        entries = entries.filter(owner_type=owner_type)
    if entry_type:
        entries = entries.filter(entry_type=entry_type)
    if source_type:
        entries = entries.filter(source_type=source_type)
    if branch_id:
        entries = entries.filter(
            Q(owner_branch_id=branch_id) | Q(counterparty_branch_id=branch_id)
        )
    if start_date:
        entries = entries.filter(entry_date__gte=start_date)
    if end_date:
        entries = entries.filter(entry_date__lte=end_date)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(entries, 50)
    page = request.GET.get('page', 1)
    entries = paginator.get_page(page)
    
    branches = Branch.objects.filter(is_active=True).order_by('name')
    
    context = {
        'entries': entries,
        'branches': branches,
        'owner_types': LedgerEntry.OwnerType.choices,
        'entry_types': LedgerEntry.EntryType.choices,
        'source_types': LedgerEntry.SourceType.choices,
        'selected_owner_type': owner_type,
        'selected_entry_type': entry_type,
        'selected_source_type': source_type,
        'selected_branch': branch_id,
        'selected_start_date': start_date,
        'selected_end_date': end_date,
    }
    
    return render(request, 'core/ledger_audit_trail.html', context)


@login_required
def branch_contributions_readonly(request, branch_id):
    """
    Mission Admin read-only view of branch contributions.
    """
    if not (request.user.is_mission_admin or request.user.is_auditor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    branch = get_object_or_404(Branch, pk=branch_id)
    
    # Get date range
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', 0))  # 0 = all months
    week = request.GET.get('week', '')
    
    from contributions.models import Contribution
    
    contributions = Contribution.objects.filter(
        branch=branch,
        date__year=year
    ).select_related('contribution_type', 'member').order_by('-date')
    
    if month:
        contributions = contributions.filter(date__month=month)
    
    if week:
        # Filter by week number
        contributions = [c for c in contributions if c.date.isocalendar()[1] == int(week)]
    
    # Summary
    total_amount = sum(c.amount for c in contributions)
    total_mission = sum(c.mission_amount for c in contributions)
    total_branch = sum(c.branch_amount for c in contributions)
    
    years = list(range(date.today().year - 5, date.today().year + 1))
    
    context = {
        'branch': branch,
        'contributions': contributions,
        'total_amount': total_amount,
        'total_mission': total_mission,
        'total_branch': total_branch,
        'selected_year': year,
        'selected_month': month,
        'selected_week': week,
        'years': years,
        'months': [(i, month_name[i]) for i in range(1, 13)],
        'is_readonly': True,
    }
    
    return render(request, 'core/branch_contributions_readonly.html', context)


@login_required
def api_ledger_balance(request):
    """
    API endpoint for getting ledger balances.
    Used for AJAX calls to check if spending is allowed.
    """
    if not request.user.can_manage_finances:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    owner_type = request.GET.get('owner_type', 'mission')
    branch_id = request.GET.get('branch_id', '')
    
    if owner_type == 'mission':
        cash = LedgerService.get_mission_cash_balance()
        receivables = LedgerService.get_mission_receivables()
        return JsonResponse({
            'cash': float(cash),
            'receivables': float(receivables),
            'spendable': float(cash),
            'can_spend': True,
        })
    elif owner_type == 'branch' and branch_id:
        branch = get_object_or_404(Branch, pk=branch_id)
        cash = LedgerService.get_branch_cash_balance(branch)
        payables = LedgerService.get_branch_payables(branch)
        spendable = cash - payables
        return JsonResponse({
            'cash': float(cash),
            'payables': float(payables),
            'spendable': float(spendable),
            'can_spend': spendable > 0,
        })
    
    return JsonResponse({'error': 'Invalid parameters'}, status=400)
