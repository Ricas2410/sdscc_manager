"""
Pastor Management Views
Handles pastor listing, details, and management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from .models import User
from payroll.models import StaffPayrollProfile
from core.models import Branch, Area, District


@login_required
def pastors_list(request):
    """
    List all pastors with their branches, salaries, and positions
    """
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Get all pastors
    pastors = User.objects.filter(role='pastor', is_active=True).select_related(
        'branch', 'branch__district', 'branch__district__area', 'managed_area', 'managed_district'
    ).prefetch_related('payroll_profile')
    
    # Apply filters
    area_id = request.GET.get('area')
    district_id = request.GET.get('district')
    branch_id = request.GET.get('branch')
    has_salary = request.GET.get('has_salary')
    
    if area_id:
        pastors = pastors.filter(
            Q(branch__district__area_id=area_id) | Q(managed_area_id=area_id)
        )
    if district_id:
        pastors = pastors.filter(
            Q(branch__district_id=district_id) | Q(managed_district_id=district_id)
        )
    if branch_id:
        pastors = pastors.filter(branch_id=branch_id)
    
    if has_salary == 'yes':
        pastors = pastors.filter(payroll_profile__isnull=False, payroll_profile__is_active=True)
    elif has_salary == 'no':
        pastors = pastors.filter(Q(payroll_profile__isnull=True) | Q(payroll_profile__is_active=False))
    
    # Search
    query = request.GET.get('q')
    if query:
        pastors = pastors.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(member_id__icontains=query) |
            Q(phone__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(pastors, 25)
    page = request.GET.get('page')
    pastors = paginator.get_page(page)
    
    context = {
        'pastors': pastors,
        'areas': Area.objects.filter(is_active=True),
        'districts': District.objects.filter(is_active=True),
        'branches': Branch.objects.filter(is_active=True),
    }
    
    return render(request, 'accounts/pastors_list.html', context)


@login_required
def pastor_detail(request, pastor_id):
    """
    View detailed information about a pastor
    """
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    pastor = get_object_or_404(User, pk=pastor_id, role='pastor')
    
    # Get payroll profile if exists
    try:
        payroll_profile = StaffPayrollProfile.objects.get(user=pastor, is_active=True)
    except StaffPayrollProfile.DoesNotExist:
        payroll_profile = None
    
    # Get additional positions
    positions = []
    if pastor.managed_area:
        positions.append(f'Area Executive - {pastor.managed_area.name}')
    if pastor.managed_district:
        positions.append(f'District Executive - {pastor.managed_district.name}')
    if pastor.is_branch_executive and pastor.branch:
        positions.append(f'Branch Executive - {pastor.branch.name}')
    
    context = {
        'pastor': pastor,
        'payroll_profile': payroll_profile,
        'positions': positions,
    }
    
    return render(request, 'accounts/pastor_detail.html', context)


@login_required
def update_pastor_info(request, pastor_id):
    """
    Update pastor information
    """
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    pastor = get_object_or_404(User, pk=pastor_id, role='pastor')
    
    if request.method == 'POST':
        # Update basic info
        pastor.first_name = request.POST.get('first_name', pastor.first_name)
        pastor.last_name = request.POST.get('last_name', pastor.last_name)
        pastor.phone = request.POST.get('phone', pastor.phone)
        pastor.email = request.POST.get('email') or None
        
        # Update branch assignment
        branch_id = request.POST.get('branch')
        if branch_id:
            pastor.branch_id = branch_id
        
        pastor.save()
        
        messages.success(request, f'Pastor {pastor.get_full_name()} updated successfully.')
        return redirect('accounts:pastor_detail', pastor_id=pastor_id)
    
    context = {
        'pastor': pastor,
        'branches': Branch.objects.filter(is_active=True),
    }
    
    return render(request, 'accounts/pastor_edit.html', context)
