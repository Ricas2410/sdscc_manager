"""
Views for Fund Assessment / Fund Register
Read-only view showing fund balances derived from ledger data
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from decimal import Decimal
from datetime import date

from contributions.models import ContributionType, Contribution
from contributions.models_opening_balance import OpeningBalance
from expenditure.models import Expenditure
from core.ledger_service import LedgerService
from core.models import Branch, Area, District


@login_required
def fund_assessment(request):
    """
    Fund Assessment / Fund Register page
    Shows fund balances without allowing edits
    """
    user = request.user
    
    # Get filter parameters
    branch_id = request.GET.get('branch')
    area_id = request.GET.get('area')
    district_id = request.GET.get('district')
    
    # Build context based on user role
    context = {
        'user': user,
        'branches': [],
        'areas': [],
        'districts': [],
        'selected_branch': branch_id,
        'selected_area': area_id,
        'selected_district': district_id,
    }
    
    # Get available entities based on user role and implement hierarchical filtering
    if user.is_mission_admin or user.is_auditor:
        context['areas'] = Area.objects.all().order_by('name')
        
        if area_id:
            context['districts'] = District.objects.filter(area_id=area_id).order_by('name')
        else:
            context['districts'] = District.objects.all().order_by('name')
            
        if district_id:
            context['branches'] = Branch.objects.filter(district_id=district_id).order_by('name')
        else:
            context['branches'] = Branch.objects.all().order_by('name')
            
        entity_type = 'all'
    elif user.is_area_executive and user.managed_area:
        context['districts'] = District.objects.filter(area=user.managed_area).order_by('name')
        
        if district_id:
            context['branches'] = Branch.objects.filter(district_id=district_id).order_by('name')
        else:
            context['branches'] = Branch.objects.filter(district__area=user.managed_area).order_by('name')
            
        entity_type = 'area'
        area_id = area_id or str(user.managed_area.id)
    elif user.is_district_executive and user.managed_district:
        context['branches'] = Branch.objects.filter(district=user.managed_district).order_by('name')
        entity_type = 'district'
        district_id = district_id or str(user.managed_district.id)
    elif user.is_branch_executive and user.branch:
        entity_type = 'branch'
        branch_id = branch_id or str(user.branch.id)
    else:
        # No access
        return render(request, 'contributions/fund_assessment.html', {
            'funds': [],
            'no_access': True
        })
    
    # Get fund data
    funds = []
    
    # Determine which contribution types to show
    if entity_type == 'all' or entity_type == 'mission':
        contribution_types = ContributionType.objects.filter(
            Q(scope=ContributionType.Scope.MISSION)
        ).order_by('name')
    elif entity_type == 'area':
        area = Area.objects.get(pk=area_id) if area_id else None
        contribution_types = ContributionType.objects.filter(
            Q(scope=ContributionType.Scope.MISSION) |
            Q(scope=ContributionType.Scope.AREA, area=area)
        ).order_by('name')
    elif entity_type == 'district':
        district = District.objects.get(pk=district_id) if district_id else None
        contribution_types = ContributionType.objects.filter(
            Q(scope=ContributionType.Scope.MISSION) |
            Q(scope=ContributionType.Scope.DISTRICT, district=district)
        ).order_by('name')
    else:  # branch
        branch = Branch.objects.get(pk=branch_id) if branch_id else None
        contribution_types = ContributionType.objects.filter(
            Q(scope=ContributionType.Scope.MISSION) |
            Q(scope=ContributionType.Scope.AREA, area=branch.district.area) |
            Q(scope=ContributionType.Scope.DISTRICT, district=branch.district) |
            Q(scope=ContributionType.Scope.BRANCH, branch=branch)
        ).distinct().order_by('name')
    
    # Calculate fund balances for each contribution type
    for fund_type in contribution_types:
        # Opening balance
        opening_balance = Decimal('0')
        if branch_id:
            opening_balance = OpeningBalance.objects.filter(
                branch_id=branch_id,
                contribution_type=fund_type,
                status='approved'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        elif entity_type == 'all':
            # Mission level opening balance
            opening_balance = OpeningBalance.objects.filter(
                branch__isnull=True,
                contribution_type=fund_type,
                status='approved'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Contributions
        contributions = Decimal('0')
        if branch_id:
            contributions = Contribution.objects.filter(
                branch_id=branch_id,
                contribution_type=fund_type,
                status='verified'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        elif entity_type == 'all':
            # All contributions for this fund type
            contributions = Contribution.objects.filter(
                contribution_type=fund_type,
                status='verified'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Expenditures
        expenditures = Decimal('0')
        if branch_id:
            expenditures = Expenditure.objects.filter(
                branch_id=branch_id,
                contribution_type=fund_type,
                status='approved'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        elif entity_type == 'all':
            expenditures = Expenditure.objects.filter(
                contribution_type=fund_type,
                status='approved'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Current balance
        current_balance = opening_balance + contributions - expenditures
        
        # Status
        if current_balance < 0:
            status = 'overspent'
            status_class = 'text-red-600 font-semibold'
        elif current_balance < (contributions * Decimal('0.1')):
            status = 'low'
            status_class = 'text-yellow-600'
        else:
            status = 'healthy'
            status_class = 'text-green-600'
        
        funds.append({
            'fund_name': fund_type.name,
            'fund_code': fund_type.code,
            'scope': fund_type.get_scope_display(),
            'opening_balance': opening_balance,
            'contributions': contributions,
            'expenditures': expenditures,
            'current_balance': current_balance,
            'status': status,
            'status_class': status_class,
        })
    
    context['funds'] = funds
    
    # Calculate totals
    context['total_opening_balance'] = sum(fund['opening_balance'] for fund in funds)
    context['total_contributions'] = sum(fund['contributions'] for fund in funds)
    context['total_expenditures'] = sum(fund['expenditures'] for fund in funds)
    context['total_current_balance'] = sum(fund['current_balance'] for fund in funds)
    
    return render(request, 'contributions/fund_assessment.html', context)


@login_required
def fund_report_branch(request, branch_id=None):
    """
    Branch Fund Report - Opening balance to current
    """
    user = request.user
    
    # Determine which branch to show
    if branch_id:
        branch = Branch.objects.get(pk=branch_id)
        # Check permissions
        if not (user.is_mission_admin or user.is_auditor or 
                (user.is_area_executive and user.managed_area == branch.district.area) or
                (user.is_district_executive and user.managed_district == branch.district) or
                (user.is_branch_executive and user.branch == branch)):
            messages.error(request, 'You do not have permission to view this report.')
            return redirect('contributions:fund_assessment')
    else:
        # Show user's own branch
        if user.is_branch_executive and user.branch:
            branch = user.branch
        else:
            messages.error(request, 'Please select a branch to view report.')
            return redirect('contributions:fund_assessment')
    
    # Get date range
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    # Build report data
    report_data = []
    
    contribution_types = ContributionType.objects.filter(
        Q(scope=ContributionType.Scope.MISSION) |
        Q(scope=ContributionType.Scope.AREA, area=branch.district.area) |
        Q(scope=ContributionType.Scope.DISTRICT, district=branch.district) |
        Q(scope=ContributionType.Scope.BRANCH, branch=branch)
    ).distinct().order_by('name')
    
    for fund_type in contribution_types:
        # Get opening balance as of start date
        opening_balance = Decimal('0')
        if from_date:
            opening_balance = OpeningBalance.objects.filter(
                branch=branch,
                contribution_type=fund_type,
                status='approved',
                date__lt=from_date
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        else:
            # All opening balances
            opening_balance = OpeningBalance.objects.filter(
                branch=branch,
                contribution_type=fund_type,
                status='approved'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Get contributions in period
        contributions_query = Contribution.objects.filter(
            branch=branch,
            contribution_type=fund_type,
            status='verified'
        )
        if from_date:
            contributions_query = contributions_query.filter(date__gte=from_date)
        if to_date:
            contributions_query = contributions_query.filter(date__lte=to_date)
        contributions = contributions_query.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Get expenditures in period
        expenditures_query = Expenditure.objects.filter(
            branch=branch,
            contribution_type=fund_type,
            status='approved'
        )
        if from_date:
            expenditures_query = expenditures_query.filter(date__gte=from_date)
        if to_date:
            expenditures_query = expenditures_query.filter(date__lte=to_date)
        expenditures = expenditures_query.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Calculate closing balance
        closing_balance = opening_balance + contributions - expenditures
        
        report_data.append({
            'fund_name': fund_type.name,
            'opening_balance': opening_balance,
            'contributions': contributions,
            'expenditures': expenditures,
            'closing_balance': closing_balance,
        })
    
    context = {
        'branch': branch,
        'report_data': report_data,
        'from_date': from_date,
        'to_date': to_date,
        'total_opening': sum(item['opening_balance'] for item in report_data),
        'total_contributions': sum(item['contributions'] for item in report_data),
        'total_expenditures': sum(item['expenditures'] for item in report_data),
        'total_closing': sum(item['closing_balance'] for item in report_data),
    }
    
    return render(request, 'contributions/fund_report_branch.html', context)


@login_required
def fund_report_mission(request):
    """
    Mission Oversight Fund Report - Shows fund totals across all branches
    """
    user = request.user
    
    # Check permissions
    if not (user.is_mission_admin or user.is_auditor):
        messages.error(request, 'You do not have permission to view this report.')
        return redirect('contributions:fund_assessment')
    
    # Get date range
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    # Build report data by fund type
    report_data = []
    
    contribution_types = ContributionType.objects.filter(
        scope=ContributionType.Scope.MISSION
    ).order_by('name')
    
    for fund_type in contribution_types:
        # Mission opening balance
        opening_balance = OpeningBalance.objects.filter(
            branch__isnull=True,
            contribution_type=fund_type,
            status='approved'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # All contributions for this fund type
        contributions_query = Contribution.objects.filter(
            contribution_type=fund_type,
            status='verified'
        )
        if from_date:
            contributions_query = contributions_query.filter(date__gte=from_date)
        if to_date:
            contributions_query = contributions_query.filter(date__lte=to_date)
        contributions = contributions_query.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # All expenditures for this fund type
        expenditures_query = Expenditure.objects.filter(
            contribution_type=fund_type,
            status='approved'
        )
        if from_date:
            expenditures_query = expenditures_query.filter(date__gte=from_date)
        if to_date:
            expenditures_query = expenditures_query.filter(date__lte=to_date)
        expenditures = expenditures_query.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Calculate closing balance
        closing_balance = opening_balance + contributions - expenditures
        
        # Branch breakdown
        branch_breakdown = []
        for branch in Branch.objects.all():
            branch_opening = OpeningBalance.objects.filter(
                branch=branch,
                contribution_type=fund_type,
                status='approved'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            branch_contributions = Contribution.objects.filter(
                branch=branch,
                contribution_type=fund_type,
                status='verified'
            )
            if from_date:
                branch_contributions = branch_contributions.filter(date__gte=from_date)
            if to_date:
                branch_contributions = branch_contributions.filter(date__lte=to_date)
            branch_contrib_total = branch_contributions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            branch_expenditures = Expenditure.objects.filter(
                branch=branch,
                contribution_type=fund_type,
                status='approved'
            )
            if from_date:
                branch_expenditures = branch_expenditures.filter(date__gte=from_date)
            if to_date:
                branch_expenditures = branch_expenditures.filter(date__lte=to_date)
            branch_exp_total = branch_expenditures.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            branch_balance = branch_opening + branch_contrib_total - branch_exp_total
            
            if branch_balance > 0:
                branch_breakdown.append({
                    'branch_name': branch.name,
                    'balance': branch_balance,
                })
        
        report_data.append({
            'fund_name': fund_type.name,
            'opening_balance': opening_balance,
            'contributions': contributions,
            'expenditures': expenditures,
            'closing_balance': closing_balance,
            'branch_breakdown': sorted(branch_breakdown, key=lambda x: x['balance'], reverse=True)[:10],
        })
    
    context = {
        'report_data': report_data,
        'from_date': from_date,
        'to_date': to_date,
        'total_opening': sum(item['opening_balance'] for item in report_data),
        'total_contributions': sum(item['contributions'] for item in report_data),
        'total_expenditures': sum(item['expenditures'] for item in report_data),
        'total_closing': sum(item['closing_balance'] for item in report_data),
    }
    
    return render(request, 'contributions/fund_report_mission.html', context)
