"""
Views for hierarchy transfers between Mission, Area, District, and Branch levels
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.http import HttpResponse
import csv

from .models_transfers import HierarchyTransfer
from accounts.permissions import mission_admin_required, area_executive_required, district_executive_required
from core.models import Area, District, Branch


@login_required
def hierarchy_transfer_list(request):
    """View all hierarchy transfers."""
    user = request.user
    
    # Filter transfers based on user role
    if user.is_mission_admin or user.is_auditor:
        transfers = HierarchyTransfer.objects.all().order_by('-date', '-created_at')
    elif user.is_area_executive and user.managed_area:
        transfers = HierarchyTransfer.objects.filter(
            source_area=user.managed_area
        ) | HierarchyTransfer.objects.filter(
            destination_area=user.managed_area
        ).order_by('-date', '-created_at')
    elif user.is_district_executive and user.managed_district:
        transfers = HierarchyTransfer.objects.filter(
            source_district=user.managed_district
        ) | HierarchyTransfer.objects.filter(
            destination_district=user.managed_district
        ).order_by('-date', '-created_at')
    elif user.is_branch_executive and user.branch:
        transfers = HierarchyTransfer.objects.filter(
            source_branch=user.branch
        ) | HierarchyTransfer.objects.filter(
            destination_branch=user.branch
        ).order_by('-date', '-created_at')
    else:
        transfers = HierarchyTransfer.objects.none()
    
    # Calculate summary statistics
    transfers_sent = transfers.filter(
        source_level__in=['mission', 'area', 'district', 'branch']
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    transfers_received = transfers.filter(
        destination_level__in=['mission', 'area', 'district', 'branch']
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    pending_count = transfers.filter(status='pending').count()
    completed_count = transfers.filter(status='completed').count()
    cancelled_count = transfers.filter(status='cancelled').count()
    
    context = {
        'transfers': transfers,
        'transfers_sent': transfers_sent,
        'transfers_received': transfers_received,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
    }
    
    return render(request, 'contributions/hierarchy_transfers.html', context)


@login_required
def hierarchy_transfers_sent(request):
    """View transfers sent by the user's entity."""
    user = request.user
    
    # Filter transfers based on user role
    if user.is_mission_admin:
        transfers = HierarchyTransfer.objects.filter(source_level='mission').order_by('-date', '-created_at')
    elif user.is_area_executive and user.managed_area:
        transfers = HierarchyTransfer.objects.filter(
            source_level='area',
            source_area=user.managed_area
        ).order_by('-date', '-created_at')
    elif user.is_district_executive and user.managed_district:
        transfers = HierarchyTransfer.objects.filter(
            source_level='district',
            source_district=user.managed_district
        ).order_by('-date', '-created_at')
    elif user.is_branch_executive and user.branch:
        transfers = HierarchyTransfer.objects.filter(
            source_level='branch',
            source_branch=user.branch
        ).order_by('-date', '-created_at')
    else:
        transfers = HierarchyTransfer.objects.none()
    
    # Calculate summary statistics
    transfers_sent = transfers.aggregate(total=Sum('amount'))['total'] or 0
    
    pending_count = transfers.filter(status='pending').count()
    completed_count = transfers.filter(status='completed').count()
    cancelled_count = transfers.filter(status='cancelled').count()
    
    context = {
        'transfers': transfers,
        'transfers_sent': transfers_sent,
        'transfers_received': 0,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'view_type': 'sent'
    }
    
    return render(request, 'contributions/hierarchy_transfers.html', context)


@login_required
def hierarchy_transfers_received(request):
    """View transfers received by the user's entity."""
    user = request.user
    
    # Filter transfers based on user role
    if user.is_mission_admin:
        transfers = HierarchyTransfer.objects.filter(destination_level='mission').order_by('-date', '-created_at')
    elif user.is_area_executive and user.managed_area:
        transfers = HierarchyTransfer.objects.filter(
            destination_level='area',
            destination_area=user.managed_area
        ).order_by('-date', '-created_at')
    elif user.is_district_executive and user.managed_district:
        transfers = HierarchyTransfer.objects.filter(
            destination_level='district',
            destination_district=user.managed_district
        ).order_by('-date', '-created_at')
    elif user.is_branch_executive and user.branch:
        transfers = HierarchyTransfer.objects.filter(
            destination_level='branch',
            destination_branch=user.branch
        ).order_by('-date', '-created_at')
    else:
        transfers = HierarchyTransfer.objects.none()
    
    # Calculate summary statistics
    transfers_received = transfers.aggregate(total=Sum('amount'))['total'] or 0
    
    pending_count = transfers.filter(status='pending').count()
    completed_count = transfers.filter(status='completed').count()
    cancelled_count = transfers.filter(status='cancelled').count()
    
    context = {
        'transfers': transfers,
        'transfers_sent': 0,
        'transfers_received': transfers_received,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'view_type': 'received'
    }
    
    return render(request, 'contributions/hierarchy_transfers.html', context)


@login_required
def hierarchy_transfer_detail(request, transfer_id):
    """View details of a specific transfer."""
    transfer = get_object_or_404(HierarchyTransfer, pk=transfer_id)
    
    context = {
        'transfer': transfer,
    }
    
    return render(request, 'contributions/hierarchy_transfer_detail.html', context)


@login_required
@mission_admin_required
def hierarchy_transfer_approve(request, transfer_id):
    """Approve a pending transfer."""
    transfer = get_object_or_404(HierarchyTransfer, pk=transfer_id)
    
    if transfer.status != 'pending':
        messages.error(request, 'Only pending transfers can be approved.')
        return redirect('contributions:hierarchy_transfer_detail', transfer_id=transfer.id)
    
    transfer.status = 'completed'
    transfer.approved_by = request.user
    transfer.approved_at = timezone.now()
    transfer.save()
    
    messages.success(request, 'Transfer has been approved successfully.')
    return redirect('contributions:hierarchy_transfer_detail', transfer_id=transfer.id)


@login_required
@mission_admin_required
def hierarchy_transfer_cancel(request, transfer_id):
    """Cancel a pending transfer."""
    transfer = get_object_or_404(HierarchyTransfer, pk=transfer_id)
    
    if transfer.status != 'pending':
        messages.error(request, 'Only pending transfers can be cancelled.')
        return redirect('contributions:hierarchy_transfer_detail', transfer_id=transfer.id)
    
    transfer.status = 'cancelled'
    transfer.save()
    
    messages.success(request, 'Transfer has been cancelled successfully.')
    return redirect('contributions:hierarchy_transfer_detail', transfer_id=transfer.id)


@login_required
@mission_admin_required
def hierarchy_transfer_add(request):
    """Add a new hierarchy transfer."""
    if request.method == 'POST':
        # Process form data
        source_level = request.POST.get('source_level')
        destination_level = request.POST.get('destination_level')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        purpose = request.POST.get('purpose')
        description = request.POST.get('description')
        reference = request.POST.get('reference')
        
        # Create transfer object
        transfer = HierarchyTransfer(
            source_level=source_level,
            destination_level=destination_level,
            amount=amount,
            date=date,
            purpose=purpose,
            description=description,
            reference=reference,
            status='pending',
            created_by=request.user,
            updated_by=request.user
        )
        
        # Set source entity
        if source_level == 'area':
            source_area_id = request.POST.get('source_area')
            transfer.source_area = get_object_or_404(Area, pk=source_area_id)
        elif source_level == 'district':
            source_district_id = request.POST.get('source_district')
            transfer.source_district = get_object_or_404(District, pk=source_district_id)
        elif source_level == 'branch':
            source_branch_id = request.POST.get('source_branch')
            transfer.source_branch = get_object_or_404(Branch, pk=source_branch_id)
        
        # Set destination entity
        if destination_level == 'area':
            destination_area_id = request.POST.get('destination_area')
            transfer.destination_area = get_object_or_404(Area, pk=destination_area_id)
        elif destination_level == 'district':
            destination_district_id = request.POST.get('destination_district')
            transfer.destination_district = get_object_or_404(District, pk=destination_district_id)
        elif destination_level == 'branch':
            destination_branch_id = request.POST.get('destination_branch')
            transfer.destination_branch = get_object_or_404(Branch, pk=destination_branch_id)
        
        try:
            transfer.full_clean()
            transfer.save()
            messages.success(request, 'Transfer created successfully.')
            return redirect('contributions:hierarchy_transfer_detail', transfer_id=transfer.id)
        except Exception as e:
            messages.error(request, f'Error creating transfer: {str(e)}')
    
    # Get data for form
    areas = Area.objects.all()
    districts = District.objects.all()
    branches = Branch.objects.all()
    
    context = {
        'areas': areas,
        'districts': districts,
        'branches': branches,
        'purposes': HierarchyTransfer.Purpose.choices,
    }
    
    return render(request, 'contributions/hierarchy_transfer_add.html', context)
