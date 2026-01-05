"""
Financial Helper Functions - Correct Financial Truth Sources

FINANCIAL RULES (MUST FOLLOW EXACTLY):
1. Mission balance increases ONLY from verified remittances (Remittance model)
2. Expected mission share is a CALCULATION, not cash (obligation only)
3. Branch balance = Total Collected - Total Expenses - Total Actually Remitted
4. Local-only contributions visible to auditors but excluded from mission calculations
5. Remittance records are the ONLY authoritative source for mission income

FINANCIAL FLOW:
Contributions (Collection) → Expected Mission Amount (Obligation) → Remittance (Cash Transfer) → Mission Balance (Income)
"""

from decimal import Decimal
from datetime import date, datetime
from django.db.models import Sum, Q, F, Count
from django.utils import timezone

from contributions.models import Contribution, Remittance
from expenditure.models import Expenditure
from core.models import Branch


def get_branch_balance(branch, start_date=None, end_date=None):
    """
    Calculate accurate branch balance.
    
    Branch Balance = Total Contributions Collected - Total Branch Expenses - Total Amount Actually Remitted
    
    IMPORTANT: Excludes expected mission share (obligation), includes only actual remittances.
    Includes local-only contributions in total collected.
    """
    # Filter contributions by date range
    contributions = Contribution.objects.filter(branch=branch)
    if start_date:
        contributions = contributions.filter(date__gte=start_date)
    if end_date:
        contributions = contributions.filter(date__lte=end_date)
    
    # Filter expenditures by date range  
    expenditures = Expenditure.objects.filter(branch=branch)
    if start_date:
        expenditures = expenditures.filter(date__gte=start_date)
    if end_date:
        expenditures = expenditures.filter(date__lte=end_date)
        
    # Filter verified remittances by date range
    remittances = Remittance.objects.filter(
        branch=branch, 
        status=Remittance.Status.VERIFIED
    )
    if start_date:
        remittances = remittances.filter(year__gte=start_date.year, month__gte=start_date.month)
    if end_date:
        remittances = remittances.filter(year__lte=end_date.year, month__lte=end_date.month)
    
    # Calculate totals
    total_contributions = contributions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_expenditures = expenditures.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_remitted = remittances.aggregate(total=Sum('amount_sent'))['total'] or Decimal('0.00')
    
    # Branch balance formula (CORRECT)
    branch_balance = total_contributions - total_expenditures - total_remitted
    
    return {
        'total_contributions': total_contributions,
        'total_expenditures': total_expenditures, 
        'total_remitted': total_remitted,
        'branch_balance': branch_balance,
        'calculation': f"{total_contributions} - {total_expenditures} - {total_remitted} = {branch_balance}"
    }


def get_expected_mission_due(branch, start_date=None, end_date=None):
    """
    Calculate expected mission amount (obligation, not cash).
    
    Expected Mission Amount = SUM(Contribution Amount * Mission Percentage)
    
    IMPORTANT: This is an OBLIGATION, not actual cash. Does not affect mission balance.
    """
    contributions = Contribution.objects.filter(branch=branch)
    if start_date:
        contributions = contributions.filter(date__gte=start_date)
    if end_date:
        contributions = contributions.filter(date__lte=end_date)
    
    expected_total = Decimal('0.00')
    
    for contribution in contributions:
        mission_amount = contribution.amount * (contribution.contribution_type.mission_percentage / Decimal('100'))
        expected_total += mission_amount
    
    return expected_total


def get_mission_income(start_date=None, end_date=None):
    """
    Calculate actual mission income from verified remittances only.
    
    Mission Income = SUM of verified remittance amounts from all branches
    
    IMPORTANT: This is the ONLY authoritative source for mission income.
    Contributions are NOT mission income until verified remittance occurs.
    """
    remittances = Remittance.objects.filter(status=Remittance.Status.VERIFIED)
    if start_date:
        remittances = remittances.filter(year__gte=start_date.year, month__gte=start_date.month)
    if end_date:
        remittances = remittances.filter(year__lte=end_date.year, month__lte=end_date.month)
    
    total_income = remittances.aggregate(total=Sum('amount_sent'))['total'] or Decimal('0.00')
    
    return {
        'total_income': total_income,
        'remittance_count': remittances.count(),
        'source': 'verified_remittances_only'
    }


def get_mission_obligations(start_date=None, end_date=None):
    """
    Calculate total mission obligations (expected amounts).
    
    Mission Obligations = SUM of expected mission amounts from all contributions
    
    IMPORTANT: This tracks what branches OWE, not what mission HAS.
    """
    contributions = Contribution.objects.all()
    if start_date:
        contributions = contributions.filter(date__gte=start_date)
    if end_date:
        contributions = contributions.filter(date__lte=end_date)
    
    total_obligations = Decimal('0.00')
    
    for contribution in contributions:
        mission_amount = contribution.amount * (contribution.contribution_type.mission_percentage / Decimal('100'))
        total_obligations += mission_amount
    
    return total_obligations


def get_local_only_contributions(branch=None, start_date=None, end_date=None):
    """
    Get local-only contributions (mission_percentage = 0).
    
    These are visible to auditors but excluded from mission calculations.
    Included in branch balance calculations.
    """
    contributions = Contribution.objects.filter(
        contribution_type__mission_percentage=0
    )
    
    if branch:
        contributions = contributions.filter(branch=branch)
    if start_date:
        contributions = contributions.filter(date__gte=start_date)
    if end_date:
        contributions = contributions.filter(date__lte=end_date)
    
    total_local = contributions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    return {
        'total_amount': total_local,
        'contribution_count': contributions.count(),
        'types': contributions.values('contribution_type__name').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
    }


def get_mission_shared_contributions(branch=None, start_date=None, end_date=None):
    """
    Get mission-shared contributions (mission_percentage > 0).
    
    These create obligations for mission remittance.
    """
    contributions = Contribution.objects.filter(
        contribution_type__mission_percentage__gt=0
    )
    
    if branch:
        contributions = contributions.filter(branch=branch)
    if start_date:
        contributions = contributions.filter(date__gte=start_date)
    if end_date:
        contributions = contributions.filter(date__lte=end_date)
    
    total_shared = contributions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    return {
        'total_amount': total_shared,
        'contribution_count': contributions.count(),
        'types': contributions.values('contribution_type__name').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
    }


def get_financial_summary(branch=None, start_date=None, end_date=None):
    """
    Complete financial summary with correct separation of obligations vs cash.
    """
    # Get all components
    branch_balance_data = get_branch_balance(branch, start_date, end_date) if branch else None
    expected_due = get_expected_mission_due(branch, start_date, end_date) if branch else Decimal('0.00')
    mission_income = get_mission_income(start_date, end_date)
    mission_obligations = get_mission_obligations(start_date, end_date)
    local_contributions = get_local_only_contributions(branch, start_date, end_date)
    shared_contributions = get_mission_shared_contributions(branch, start_date, end_date)
    
    return {
        'branch_balance': branch_balance_data,
        'expected_mission_due': expected_due,
        'actual_mission_income': mission_income['total_income'],
        'total_mission_obligations': mission_obligations,
        'local_only_contributions': local_contributions['total_amount'],
        'mission_shared_contributions': shared_contributions['total_amount'],
        'remittance_count': mission_income['remittance_count'],
        'financial_health': {
            'obligation_vs_income': mission_obligations - mission_income['total_income'],  # Positive = underpaid
            'branch_cash_position': branch_balance_data['branch_balance'] if branch_balance_data else Decimal('0.00'),
            'remittance_rate': (mission_income['total_income'] / mission_obligations * 100) if mission_obligations > 0 else Decimal('0.00')
        }
    }


# Utility functions for reporting
def annotate_branch_financials(queryset, start_date=None, end_date=None):
    """
    Annotate a branch queryset with correct financial calculations.
    """
    # TODO: Implement query annotations for performance
    # This would use Subquery and Case/When for database-level calculations
    return queryset
