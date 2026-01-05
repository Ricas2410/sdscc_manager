"""
Monthly Reports Views - Hierarchy-aware monthly reporting for executives
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, date
import calendar

from core.models import Area, District, Branch
from contributions.models import Contribution, ContributionType
from expenditure.models import Expenditure, ExpenditureCategory


@login_required
def monthly_reports_dashboard(request):
    """Monthly reports dashboard for Area and District executives."""
    if not (request.user.is_area_executive or request.user.is_district_executive or request.user.is_mission_admin):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Initialize hierarchy-based filtering
    user_scope = 'mission'  # Default for mission admin
    if request.user.is_branch_executive and request.user.branch:
        user_scope = 'branch'
    elif request.user.is_district_executive and request.user.managed_district:
        user_scope = 'district'
    elif request.user.is_area_executive and request.user.managed_area:
        user_scope = 'area'
    
    # Get current date
    today = timezone.now().date()
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))
    
    # Calculate date range for the month
    month_start = date(selected_year, selected_month, 1)
    if selected_month == 12:
        month_end = date(selected_year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        month_end = date(selected_year, selected_month + 1, 1) - timezone.timedelta(days=1)
    
    # Base querysets
    contributions_qs = Contribution.objects.filter(
        date__gte=month_start,
        date__lte=month_end
    ).select_related('branch', 'branch__district', 'branch__district__area', 'contribution_type')
    
    expenditures_qs = Expenditure.objects.filter(
        date__gte=month_start,
        date__lte=month_end,
        status__in=['approved', 'paid']
    ).select_related('branch', 'branch__district', 'branch__district__area', 'category')
    
    # Apply hierarchy filtering
    if user_scope == 'area':
        contributions_qs = contributions_qs.filter(branch__district__area=request.user.managed_area)
        expenditures_qs = expenditures_qs.filter(Q(branch__district__area=request.user.managed_area) | Q(level='mission'))
        districts = District.objects.filter(area=request.user.managed_area, is_active=True)
        branches = Branch.objects.filter(district__area=request.user.managed_area, is_active=True)
    elif user_scope == 'district':
        contributions_qs = contributions_qs.filter(branch__district=request.user.managed_district)
        expenditures_qs = expenditures_qs.filter(Q(branch__district=request.user.managed_district) | Q(level='mission'))
        districts = District.objects.filter(pk=request.user.managed_district.pk, is_active=True)
        branches = Branch.objects.filter(district=request.user.managed_district, is_active=True)
    elif user_scope == 'branch':
        contributions_qs = contributions_qs.filter(branch=request.user.branch)
        expenditures_qs = expenditures_qs.filter(branch=request.user.branch)
        districts = District.objects.none()
        branches = Branch.objects.filter(pk=request.user.branch.pk, is_active=True)
    else:
        districts = District.objects.filter(is_active=True)
        branches = Branch.objects.filter(is_active=True)
    
    # Calculate totals
    total_contributions = contributions_qs.aggregate(total=Sum('amount'))['total'] or 0
    total_expenditures = expenditures_qs.aggregate(total=Sum('amount'))['total'] or 0
    net_amount = total_contributions - total_expenditures
    
    # District breakdown (for Area and Mission admins)
    district_breakdown = []
    if user_scope in ['mission', 'area']:
        for district in districts:
            district_contributions = contributions_qs.filter(branch__district=district).aggregate(
                total=Sum('amount'),
                count=Count('id')
            )
            district_expenditures = expenditures_qs.filter(branch__district=district).aggregate(
                total=Sum('amount'),
                count=Count('id')
            )
            
            district_breakdown.append({
                'district': district,
                'contributions': district_contributions['total'] or 0,
                'contributions_count': district_contributions['count'] or 0,
                'expenditures': district_expenditures['total'] or 0,
                'expenditures_count': district_expenditures['count'] or 0,
                'net': (district_contributions['total'] or 0) - (district_expenditures['total'] or 0)
            })
    
    # Branch breakdown
    branch_breakdown = []
    for branch in branches:
        branch_contributions = contributions_qs.filter(branch=branch).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        branch_expenditures = expenditures_qs.filter(branch=branch).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        branch_breakdown.append({
            'branch': branch,
            'contributions': branch_contributions['total'] or 0,
            'contributions_count': branch_contributions['count'] or 0,
            'expenditures': branch_expenditures['total'] or 0,
            'expenditures_count': branch_expenditures['count'] or 0,
            'net': (branch_contributions['total'] or 0) - (branch_expenditures['total'] or 0)
        })
    
    # Sort by net amount (descending)
    branch_breakdown.sort(key=lambda x: x['net'], reverse=True)
    district_breakdown.sort(key=lambda x: x['net'], reverse=True)
    
    # Top 5 branches by contributions
    top_branches = sorted(branch_breakdown, key=lambda x: x['contributions'], reverse=True)[:5]
    
    # Contribution type breakdown
    contribution_types = contributions_qs.values('contribution_type__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')[:10]
    
    # Expenditure category breakdown
    expenditure_categories = expenditures_qs.values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')[:10]
    
    # Generate month options for dropdown
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    years = list(range(today.year - 2, today.year + 2))
    
    context = {
        'user_scope': user_scope,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'month_name': calendar.month_name[selected_month],
        'months': months,
        'years': years,
        
        # Summary totals
        'total_contributions': total_contributions,
        'total_expenditures': total_expenditures,
        'net_amount': net_amount,
        
        # Breakdowns
        'district_breakdown': district_breakdown,
        'branch_breakdown': branch_breakdown,
        'top_branches': top_branches,
        
        # Categories
        'contribution_types': contribution_types,
        'expenditure_categories': expenditure_categories,
        
        # Hierarchy info
        'managed_area': request.user.managed_area if user_scope == 'area' else None,
        'managed_district': request.user.managed_district if user_scope == 'district' else None,
    }
    
    return render(request, 'reports/monthly_reports.html', context)


@login_required
def monthly_branch_detail(request, branch_id):
    """Detailed monthly report for a specific branch."""
    if not (request.user.is_any_admin):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Get current date
    today = timezone.now().date()
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))
    
    # Calculate date range for the month
    month_start = date(selected_year, selected_month, 1)
    if selected_month == 12:
        month_end = date(selected_year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        month_end = date(selected_year, selected_month + 1, 1) - timezone.timedelta(days=1)
    
    # Get branch and validate access
    branch = get_object_or_404(Branch, pk=branch_id, is_active=True)
    
    # Validate hierarchy access
    if request.user.is_branch_executive and request.user.branch:
        if branch != request.user.branch:
            messages.error(request, 'Access denied. You can only view reports for your branch.')
            return redirect('reports:monthly')
    elif request.user.is_district_executive and request.user.managed_district:
        if branch.district != request.user.managed_district:
            messages.error(request, 'Access denied. You can only view reports for branches in your district.')
            return redirect('reports:monthly')
    elif request.user.is_area_executive and request.user.managed_area:
        if branch.district.area != request.user.managed_area:
            messages.error(request, 'Access denied. You can only view reports for branches in your area.')
            return redirect('reports:monthly')
    
    # Get contributions and expenditures for this branch
    contributions = Contribution.objects.filter(
        branch=branch,
        date__gte=month_start,
        date__lte=month_end
    ).select_related('contribution_type', 'member').order_by('-date')
    
    expenditures = Expenditure.objects.filter(
        branch=branch,
        date__gte=month_start,
        date__lte=month_end,
        status__in=['approved', 'paid']
    ).select_related('category').order_by('-date')
    
    # Calculate totals
    total_contributions = contributions.aggregate(total=Sum('amount'))['total'] or 0
    total_expenditures = expenditures.aggregate(total=Sum('amount'))['total'] or 0
    
    # By contribution type
    by_type = contributions.values('contribution_type__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # By expenditure category
    by_category = expenditures.values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    context = {
        'branch': branch,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'month_name': calendar.month_name[selected_month],
        
        'contributions': contributions,
        'expenditures': expenditures,
        
        'total_contributions': total_contributions,
        'total_expenditures': total_expenditures,
        'net_amount': total_contributions - total_expenditures,
        
        'by_type': by_type,
        'by_category': by_category,
    }
    
    return render(request, 'reports/monthly_branch_detail.html', context)
