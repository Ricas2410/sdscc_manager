"""
Groups Views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import models

from .models import Group, GroupCategory, GroupMembership


@login_required
def group_list(request):
    """List groups."""
    groups = Group.objects.filter(is_active=True).select_related('category', 'branch', 'leader')
    categories = GroupCategory.objects.filter(is_active=True)
    
    # Apply hierarchy filtering
    if request.user.is_branch_executive and request.user.branch:
        groups = groups.filter(branch=request.user.branch)
    elif request.user.is_district_executive and request.user.managed_district:
        groups = groups.filter(branch__district=request.user.managed_district)
    elif request.user.is_area_executive and request.user.managed_area:
        groups = groups.filter(branch__district__area=request.user.managed_area)
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        groups = groups.filter(category_id=category_id)
    
    return render(request, 'groups/group_list.html', {
        'groups': groups,
        'categories': categories,
    })


@login_required
def group_add(request):
    """Add a group."""
    from accounts.models import User
    from core.models import Branch, District, Area
    
    if not request.user.is_any_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    categories = GroupCategory.objects.filter(is_active=True)
    
    # Initialize hierarchy-based filtering
    user_scope = 'mission'  # Default for mission admin
    if request.user.is_branch_executive and request.user.branch:
        user_scope = 'branch'
    elif request.user.is_district_executive and request.user.managed_district:
        user_scope = 'district'
    elif request.user.is_area_executive and request.user.managed_area:
        user_scope = 'area'
    
    # Filter areas, districts, and branches based on user hierarchy
    if user_scope == 'area':
        areas = Area.objects.filter(pk=request.user.managed_area.pk, is_active=True)
        districts = District.objects.filter(area=request.user.managed_area, is_active=True)
        branches = Branch.objects.filter(district__area=request.user.managed_area, is_active=True)
    elif user_scope == 'district':
        areas = Area.objects.filter(pk=request.user.managed_district.area.pk, is_active=True)
        districts = District.objects.filter(pk=request.user.managed_district.pk, is_active=True)
        branches = Branch.objects.filter(district=request.user.managed_district, is_active=True)
    elif user_scope == 'branch':
        areas = Area.objects.filter(pk=request.user.branch.district.area.pk, is_active=True)
        districts = District.objects.filter(pk=request.user.branch.district.pk, is_active=True)
        branches = Branch.objects.filter(pk=request.user.branch.pk, is_active=True)
    else:
        areas = Area.objects.filter(is_active=True)
        districts = District.objects.filter(is_active=True)
        branches = Branch.objects.filter(is_active=True).select_related('district__area')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Handle category creation
        if action == 'add_category':
            cat_name = request.POST.get('category_name')
            cat_type = request.POST.get('category_type', 'ministry')
            if cat_name:
                cat, created = GroupCategory.objects.get_or_create(
                    name=cat_name,
                    defaults={'category_type': cat_type}
                )
                if created:
                    messages.success(request, f'Category "{cat_name}" created.')
                else:
                    messages.info(request, f'Category "{cat_name}" already exists.')
            return redirect('groups:add')
        
        # Handle group creation
        name = request.POST.get('name')
        code = request.POST.get('code', '').upper()
        description = request.POST.get('description', '')
        category_id = request.POST.get('category')
        scope = request.POST.get('scope', 'branch')
        branch_id = request.POST.get('branch')
        leader_id = request.POST.get('leader')
        assistant_id = request.POST.get('assistant_leader')
        meeting_day = request.POST.get('meeting_day', '')
        meeting_time = request.POST.get('meeting_time') or None
        meeting_location = request.POST.get('meeting_location', '')
        
        # Validate branch access based on user hierarchy
        if branch_id and user_scope != 'mission':
            try:
                selected_branch = Branch.objects.get(pk=branch_id, is_active=True)
                
                if user_scope == 'area' and selected_branch.district.area != request.user.managed_area:
                    messages.error(request, 'You can only create groups for branches in your area.')
                    return redirect('groups:add')
                elif user_scope == 'district' and selected_branch.district != request.user.managed_district:
                    messages.error(request, 'You can only create groups for branches in your district.')
                    return redirect('groups:add')
                elif user_scope == 'branch' and selected_branch != request.user.branch:
                    messages.error(request, 'You can only create groups for your branch.')
                    return redirect('groups:add')
            except Branch.DoesNotExist:
                messages.error(request, 'Invalid branch selected.')
                return redirect('groups:add')
        
        if name and code:
            try:
                group = Group.objects.create(
                    name=name,
                    code=code,
                    description=description,
                    category_id=category_id if category_id else None,
                    scope=scope,
                    branch_id=branch_id if branch_id else None,
                    leader_id=leader_id if leader_id else None,
                    assistant_leader_id=assistant_id if assistant_id else None,
                    meeting_day=meeting_day,
                    meeting_time=meeting_time,
                    meeting_location=meeting_location,
                )
                messages.success(request, f'Group "{name}" created successfully.')
                return redirect('groups:detail', group_id=group.id)
            except Exception as e:
                messages.error(request, f'Error creating group: {str(e)}')
        else:
            messages.error(request, 'Name and code are required.')
    
    # Branch admins can only create groups for their branch
    is_branch_admin = request.user.is_branch_executive and not request.user.is_mission_admin
    
    context = {
        'categories': categories,
        'areas': areas,
        'districts': districts,
        'branches': branches,
        'scopes': Group.Scope.choices,
        'category_types': GroupCategory.CategoryType.choices,
        'days': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        'is_branch_admin': is_branch_admin,
        'user_branch': request.user.branch,
        'user_scope': user_scope,
    }
    return render(request, 'groups/group_form.html', context)


@login_required
def group_detail(request, group_id):
    """View group detail."""
    group = get_object_or_404(Group, pk=group_id)
    memberships = GroupMembership.objects.filter(group=group, is_active=True).select_related('member')
    
    return render(request, 'groups/group_detail.html', {'group': group, 'memberships': memberships})


@login_required
def group_members(request, group_id):
    """Manage group members."""
    from accounts.models import User
    
    group = get_object_or_404(Group, pk=group_id)
    
    # Check if user has access to this group based on hierarchy
    if request.user.is_branch_executive and request.user.branch:
        if group.branch != request.user.branch:
            messages.error(request, 'Access denied. You can only manage groups in your branch.')
            return redirect('groups:list')
    elif request.user.is_district_executive and request.user.managed_district:
        if group.branch and group.branch.district != request.user.managed_district:
            messages.error(request, 'Access denied. You can only manage groups in your district.')
            return redirect('groups:list')
    elif request.user.is_area_executive and request.user.managed_area:
        if group.branch and group.branch.district.area != request.user.managed_area:
            messages.error(request, 'Access denied. You can only manage groups in your area.')
            return redirect('groups:list')
    
    memberships = GroupMembership.objects.filter(group=group).select_related('member')
    
    # Get available members (not already in group)
    existing_member_ids = memberships.values_list('member_id', flat=True)
    available_members = User.objects.filter(is_active=True).exclude(id__in=existing_member_ids)
    
    # Apply hierarchy filtering to available members
    if request.user.is_branch_executive and request.user.branch:
        available_members = available_members.filter(branch=request.user.branch)
    elif request.user.is_district_executive and request.user.managed_district:
        available_members = available_members.filter(branch__district=request.user.managed_district)
    elif request.user.is_area_executive and request.user.managed_area:
        available_members = available_members.filter(branch__district__area=request.user.managed_area)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_member':
            member_id = request.POST.get('member')
            role = request.POST.get('role', 'member')
            if member_id:
                member = get_object_or_404(User, pk=member_id)
                
                # Validate member access based on hierarchy
                if request.user.is_branch_executive and request.user.branch:
                    if member.branch != request.user.branch:
                        messages.error(request, 'You can only add members from your branch.')
                        return redirect('groups:members', group_id=group.id)
                elif request.user.is_district_executive and request.user.managed_district:
                    if member.branch and member.branch.district != request.user.managed_district:
                        messages.error(request, 'You can only add members from your district.')
                        return redirect('groups:members', group_id=group.id)
                elif request.user.is_area_executive and request.user.managed_area:
                    if member.branch and member.branch.district.area != request.user.managed_area:
                        messages.error(request, 'You can only add members from your area.')
                        return redirect('groups:members', group_id=group.id)
                
                membership, created = GroupMembership.objects.get_or_create(
                    group=group,
                    member=member,
                    defaults={'role': role}
                )
                if created:
                    messages.success(request, f'{member.get_full_name()} added to group.')
                else:
                    messages.info(request, f'{member.get_full_name()} is already in this group.')
        
        elif action == 'remove_member':
            membership_id = request.POST.get('membership_id')
            try:
                membership = GroupMembership.objects.get(pk=membership_id, group=group)
                name = membership.member.get_full_name()
                membership.delete()
                messages.success(request, f'{name} removed from group.')
            except GroupMembership.DoesNotExist:
                messages.error(request, 'Membership not found.')
        
        return redirect('groups:members', group_id=group.id)
    
    return render(request, 'groups/group_members.html', {
        'group': group, 
        'memberships': memberships,
        'available_members': available_members,
        'active_members_count': memberships.filter(is_active=True).count()
    })


@login_required
def search_members(request):
    """AJAX endpoint to search members by hierarchy."""
    from accounts.models import User
    from core.models import Branch
    
    q = request.GET.get('q', '')
    branch_id = request.GET.get('branch')
    limit = int(request.GET.get('limit', 20))
    
    members = User.objects.filter(is_active=True)
    
    # Apply hierarchy filtering
    if request.user.is_branch_executive and request.user.branch:
        members = members.filter(branch=request.user.branch)
    elif request.user.is_district_executive and request.user.managed_district:
        members = members.filter(branch__district=request.user.managed_district)
    elif request.user.is_area_executive and request.user.managed_area:
        members = members.filter(branch__district__area=request.user.managed_area)
    
    # Filter by branch if specified (only if user has access to that branch)
    if branch_id:
        try:
            selected_branch = Branch.objects.get(pk=branch_id, is_active=True)
            
            # Validate branch access based on hierarchy
            if request.user.is_branch_executive and request.user.branch:
                if selected_branch != request.user.branch:
                    return JsonResponse({'members': []})  # No access
            elif request.user.is_district_executive and request.user.managed_district:
                if selected_branch.district != request.user.managed_district:
                    return JsonResponse({'members': []})  # No access
            elif request.user.is_area_executive and request.user.managed_area:
                if selected_branch.district.area != request.user.managed_area:
                    return JsonResponse({'members': []})  # No access
            
            members = members.filter(branch_id=branch_id)
        except Branch.DoesNotExist:
            return JsonResponse({'members': []})
    
    # Search
    if q:
        members = members.filter(
            models.Q(first_name__icontains=q) |
            models.Q(last_name__icontains=q) |
            models.Q(member_id__icontains=q) |
            models.Q(phone__icontains=q)
        )
    
    members = members[:limit]
    
    data = [{
        'id': str(m.id),
        'name': m.get_full_name(),
        'member_id': m.member_id,
        'branch': m.branch.name if m.branch else 'No Branch',
    } for m in members]
    
    return JsonResponse({'members': data})


@login_required 
def get_branch_members(request, branch_id):
    """Get members of a specific branch for AJAX."""
    from accounts.models import User
    from core.models import Branch
    
    try:
        branch = Branch.objects.get(pk=branch_id, is_active=True)
        
        # Validate branch access based on hierarchy
        if request.user.is_branch_executive and request.user.branch:
            if branch != request.user.branch:
                return JsonResponse({'members': []})  # No access
        elif request.user.is_district_executive and request.user.managed_district:
            if branch.district != request.user.managed_district:
                return JsonResponse({'members': []})  # No access
        elif request.user.is_area_executive and request.user.managed_area:
            if branch.district.area != request.user.managed_area:
                return JsonResponse({'members': []})  # No access
        
        members = User.objects.filter(branch=branch, is_active=True).order_by('first_name')[:50]
        
        data = [{
            'id': str(m.id),
            'name': m.get_full_name(),
            'member_id': m.member_id,
        } for m in members]
        
        return JsonResponse({'members': data})
        
    except Branch.DoesNotExist:
        return JsonResponse({'members': []})
