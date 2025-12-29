"""
Branch Contribution Type Views - Allow branch admins to create contribution types
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.text import slugify
from decimal import Decimal

from contributions.models import ContributionType
from core.models import Branch, Notification
from accounts.models import User


@login_required
def branch_contribution_types(request):
    """List contribution types for branch admin."""
    if not (request.user.is_branch_executive or request.user.is_mission_admin):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    branch = request.user.branch if not request.user.is_mission_admin else None
    
    if request.user.is_mission_admin:
        # Mission admin sees all types
        mission_types = ContributionType.objects.filter(scope='mission', is_active=True)
        branch_types = ContributionType.objects.filter(scope='branch', is_active=True)
    else:
        # Branch admin sees mission types and their branch types
        mission_types = ContributionType.objects.filter(scope='mission', is_active=True)
        branch_types = ContributionType.objects.filter(
            scope='branch',
            branch=branch,
            is_active=True
        ) if branch else ContributionType.objects.none()
    
    context = {
        'mission_types': mission_types,
        'branch_types': branch_types,
        'branch': branch,
        'can_create': request.user.is_branch_executive or request.user.is_mission_admin,
    }
    
    return render(request, 'contributions/branch_contribution_types.html', context)


@login_required
def create_branch_contribution_type(request):
    """Create a new branch-level contribution type."""
    if not (request.user.is_branch_executive or request.user.is_mission_admin):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    branch = request.user.branch
    if not branch and not request.user.is_mission_admin:
        messages.error(request, 'No branch assigned.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        category = request.POST.get('category', 'offering')
        
        # Allocation percentages
        mission_pct = Decimal(request.POST.get('mission_percentage', '0'))
        area_pct = Decimal(request.POST.get('area_percentage', '0'))
        district_pct = Decimal(request.POST.get('district_percentage', '0'))
        branch_pct = Decimal(request.POST.get('branch_percentage', '100'))
        
        # Validate percentages sum to 100
        total_pct = mission_pct + area_pct + district_pct + branch_pct
        if total_pct != 100:
            messages.error(request, f'Allocation percentages must sum to 100%. Current total: {total_pct}%')
            return redirect('contributions:branch_types')
        
        # Generate unique code
        base_code = slugify(name).upper().replace('-', '_')[:15]
        code = base_code
        counter = 1
        while ContributionType.objects.filter(code=code).exists():
            code = f"{base_code}_{counter}"
            counter += 1
        
        try:
            # Create contribution type
            contrib_type = ContributionType.objects.create(
                name=name,
                code=code,
                description=description,
                category=category,
                scope='branch',
                branch=branch,
                mission_percentage=mission_pct,
                area_percentage=area_pct,
                district_percentage=district_pct,
                branch_percentage=branch_pct,
                is_individual=False,
                is_general=True,
                is_active=True,
                created_by=request.user
            )
            
            # Notify mission admin
            mission_admins = User.objects.filter(is_mission_admin=True, is_active=True)
            for admin in mission_admins:
                Notification.objects.create(
                    recipient=admin,
                    notification_type='contribution',
                    title='New Branch Contribution Type Created',
                    message=f'{branch.name} created a new contribution type: {name}',
                    link=f'/contributions/types/{contrib_type.id}/',
                    branch=branch,
                    created_by=request.user
                )
            
            messages.success(request, f'Contribution type "{name}" created successfully with code "{code}".')
            return redirect('contributions:branch_types')
            
        except Exception as e:
            messages.error(request, f'Error creating contribution type: {str(e)}')
            return redirect('contributions:branch_types')
    
    context = {
        'branch': branch,
        'categories': ContributionType.Category.choices,
    }
    
    return render(request, 'contributions/create_branch_type.html', context)


@login_required
def edit_branch_contribution_type(request, type_id):
    """Edit a branch contribution type."""
    contrib_type = get_object_or_404(ContributionType, pk=type_id)
    
    # Check permissions
    if not request.user.is_mission_admin:
        if contrib_type.scope != 'branch' or contrib_type.branch != request.user.branch:
            messages.error(request, 'Access denied.')
            return redirect('contributions:branch_types')
    
    if request.method == 'POST':
        contrib_type.name = request.POST.get('name')
        contrib_type.description = request.POST.get('description', '')
        contrib_type.category = request.POST.get('category', 'offering')
        
        # Allocation percentages
        mission_pct = Decimal(request.POST.get('mission_percentage', '0'))
        area_pct = Decimal(request.POST.get('area_percentage', '0'))
        district_pct = Decimal(request.POST.get('district_percentage', '0'))
        branch_pct = Decimal(request.POST.get('branch_percentage', '100'))
        
        # Validate percentages sum to 100
        total_pct = mission_pct + area_pct + district_pct + branch_pct
        if total_pct != 100:
            messages.error(request, f'Allocation percentages must sum to 100%. Current total: {total_pct}%')
            return redirect('contributions:edit_branch_type', type_id=type_id)
        
        contrib_type.mission_percentage = mission_pct
        contrib_type.area_percentage = area_pct
        contrib_type.district_percentage = district_pct
        contrib_type.branch_percentage = branch_pct
        contrib_type.updated_by = request.user
        
        try:
            contrib_type.save()
            messages.success(request, f'Contribution type "{contrib_type.name}" updated successfully.')
            return redirect('contributions:branch_types')
        except Exception as e:
            messages.error(request, f'Error updating contribution type: {str(e)}')
    
    context = {
        'contrib_type': contrib_type,
        'categories': ContributionType.Category.choices,
    }
    
    return render(request, 'contributions/edit_branch_type.html', context)


@login_required
def deactivate_branch_contribution_type(request, type_id):
    """Deactivate a branch contribution type."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
    contrib_type = get_object_or_404(ContributionType, pk=type_id)
    
    # Check permissions
    if not request.user.is_mission_admin:
        if contrib_type.scope != 'branch' or contrib_type.branch != request.user.branch:
            return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
    
    try:
        contrib_type.is_active = False
        contrib_type.updated_by = request.user
        contrib_type.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Contribution type "{contrib_type.name}" deactivated successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@login_required
def activate_branch_contribution_type(request, type_id):
    """Reactivate a branch contribution type."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
    contrib_type = get_object_or_404(ContributionType, pk=type_id)
    
    # Check permissions
    if not request.user.is_mission_admin:
        if contrib_type.scope != 'branch' or contrib_type.branch != request.user.branch:
            return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
    
    try:
        contrib_type.is_active = True
        contrib_type.updated_by = request.user
        contrib_type.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Contribution type "{contrib_type.name}" activated successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)
