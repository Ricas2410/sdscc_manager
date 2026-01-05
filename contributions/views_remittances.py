"""
Views for hierarchy remittances to Area and District levels
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.http import HttpResponse
import csv

from .models_remittance import HierarchyRemittance
from accounts.permissions import mission_admin_required, area_executive_required, district_executive_required
from core.models import Area, District, Branch


from django.db.models import Q

@login_required
def hierarchy_remittance_list(request):
    """View all hierarchy remittances."""
    user = request.user

    # Filter remittances based on user role
    if user.is_mission_admin or user.is_auditor:
        # Mission admins and auditors can see everything
        remittances = HierarchyRemittance.objects.all().order_by('-year', '-month', 'branch__name')
    elif user.is_area_executive and user.managed_area:
        # Area executives can see:
        # 1. Area-level remittances to their area
        # 2. District-level remittances for districts under their area
        remittances = HierarchyRemittance.objects.filter(
            Q(destination_level='area', area=user.managed_area) |
            Q(destination_level='district', district__area=user.managed_area)
        ).order_by('-year', '-month', 'branch__name')
    elif user.is_district_executive and user.managed_district:
        # District executives can see:
        # 1. District-level remittances to their district
        # 2. Area-level remittances for branches under their district
        remittances = HierarchyRemittance.objects.filter(
            Q(destination_level='district', district=user.managed_district) |
            Q(destination_level='area', branch__district=user.managed_district)
        ).order_by('-year', '-month', 'branch__name')
    elif user.is_branch_executive and user.branch:
        # Branch executives can only see remittances for their own branch
        remittances = HierarchyRemittance.objects.filter(
            branch=user.branch
        ).order_by('-year', '-month')
    else:
        remittances = HierarchyRemittance.objects.none()
    
    # Calculate summary statistics
    total_due = remittances.aggregate(total=Sum('amount_due'))['total'] or 0
    total_sent = remittances.aggregate(total=Sum('amount_sent'))['total'] or 0
    
    pending_count = remittances.filter(status='pending').count()
    sent_count = remittances.filter(status='sent').count()
    verified_count = remittances.filter(status='verified').count()
    
    context = {
        'remittances': remittances,
        'total_due': total_due,
        'total_sent': total_sent,
        'pending_count': pending_count,
        'sent_count': sent_count,
        'verified_count': verified_count,
    }
    
    return render(request, 'contributions/hierarchy_remittances.html', context)


@login_required
def hierarchy_remittances_area(request):
    """View remittances to Areas."""
    user = request.user

    # Filter remittances based on user role
    if user.is_mission_admin or user.is_auditor:
        # Mission admins and auditors can see all area remittances
        remittances = HierarchyRemittance.objects.filter(
            destination_level='area'
        ).order_by('-year', '-month', 'branch__name')
    elif user.is_area_executive and user.managed_area:
        # Area executives can only see area-level remittances to their area
        remittances = HierarchyRemittance.objects.filter(
            destination_level='area',
            area=user.managed_area
        ).order_by('-year', '-month', 'branch__name')
    elif user.is_district_executive and user.managed_district:
        # District executives can see area-level remittances for branches under their district
        remittances = HierarchyRemittance.objects.filter(
            destination_level='area',
            branch__district=user.managed_district
        ).order_by('-year', '-month', 'branch__name')
    elif user.is_branch_executive and user.branch:
        # Branch executives can only see area-level remittances for their branch
        remittances = HierarchyRemittance.objects.filter(
            branch=user.branch,
            destination_level='area'
        ).order_by('-year', '-month')
    else:
        remittances = HierarchyRemittance.objects.none()
    
    # Calculate summary statistics
    total_due = remittances.aggregate(total=Sum('amount_due'))['total'] or 0
    total_sent = remittances.aggregate(total=Sum('amount_sent'))['total'] or 0
    
    pending_count = remittances.filter(status='pending').count()
    sent_count = remittances.filter(status='sent').count()
    verified_count = remittances.filter(status='verified').count()
    
    context = {
        'remittances': remittances,
        'total_due': total_due,
        'total_sent': total_sent,
        'pending_count': pending_count,
        'sent_count': sent_count,
        'verified_count': verified_count,
        'view_type': 'area'
    }
    
    return render(request, 'contributions/hierarchy_remittances.html', context)


@login_required
def hierarchy_remittances_district(request):
    """View remittances to Districts."""
    user = request.user

    # Filter remittances based on user role
    if user.is_mission_admin or user.is_auditor:
        # Mission admins and auditors can see all district remittances
        remittances = HierarchyRemittance.objects.filter(
            destination_level='district'
        ).order_by('-year', '-month', 'branch__name')
    elif user.is_area_executive and user.managed_area:
        # Area executives can see district-level remittances for districts under their area
        remittances = HierarchyRemittance.objects.filter(
            destination_level='district',
            district__area=user.managed_area
        ).order_by('-year', '-month', 'branch__name')
    elif user.is_district_executive and user.managed_district:
        # District executives can only see district-level remittances to their district
        remittances = HierarchyRemittance.objects.filter(
            destination_level='district',
            district=user.managed_district
        ).order_by('-year', '-month', 'branch__name')
    elif user.is_branch_executive and user.branch:
        # Branch executives can only see district-level remittances for their branch
        remittances = HierarchyRemittance.objects.filter(
            branch=user.branch,
            destination_level='district'
        ).order_by('-year', '-month')
    else:
        remittances = HierarchyRemittance.objects.none()
    
    # Calculate summary statistics
    total_due = remittances.aggregate(total=Sum('amount_due'))['total'] or 0
    total_sent = remittances.aggregate(total=Sum('amount_sent'))['total'] or 0
    
    pending_count = remittances.filter(status='pending').count()
    sent_count = remittances.filter(status='sent').count()
    verified_count = remittances.filter(status='verified').count()
    
    context = {
        'remittances': remittances,
        'total_due': total_due,
        'total_sent': total_sent,
        'pending_count': pending_count,
        'sent_count': sent_count,
        'verified_count': verified_count,
        'view_type': 'district'
    }
    
    return render(request, 'contributions/hierarchy_remittances.html', context)


@login_required
def hierarchy_remittance_detail(request, remittance_id):
    """View details of a specific remittance."""
    remittance = get_object_or_404(HierarchyRemittance, pk=remittance_id)
    
    context = {
        'remittance': remittance,
    }
    
    return render(request, 'contributions/hierarchy_remittance_detail.html', context)


@login_required
@area_executive_required
def hierarchy_remittance_verify(request, remittance_id):
    """Verify a sent remittance."""
    remittance = get_object_or_404(HierarchyRemittance, pk=remittance_id)
    
    # Check if user has permission to verify this remittance
    if remittance.destination_level == 'area' and request.user.managed_area != remittance.area:
        messages.error(request, 'You do not have permission to verify this remittance.')
        return redirect('contributions:hierarchy_remittance_detail', remittance_id=remittance.id)
    
    if remittance.destination_level == 'district' and request.user.managed_district != remittance.district:
        messages.error(request, 'You do not have permission to verify this remittance.')
        return redirect('contributions:hierarchy_remittance_detail', remittance_id=remittance.id)
    
    if remittance.status != 'sent':
        messages.error(request, 'Only sent remittances can be verified.')
        return redirect('contributions:hierarchy_remittance_detail', remittance_id=remittance.id)
    
    remittance.status = 'verified'
    remittance.verified_by = request.user
    remittance.verified_at = timezone.now()
    remittance.save()
    
    messages.success(request, 'Remittance has been verified successfully.')
    return redirect('contributions:hierarchy_remittance_detail', remittance_id=remittance.id)


@login_required
@mission_admin_required
def hierarchy_remittance_add(request):
    """Add a new hierarchy remittance."""
    if request.method == 'POST':
        # Process form data
        branch_id = request.POST.get('branch')
        destination_level = request.POST.get('destination_level')
        month = request.POST.get('month')
        year = request.POST.get('year')
        amount_due = request.POST.get('amount_due')
        notes = request.POST.get('notes')
        
        # Create remittance object
        remittance = HierarchyRemittance(
            branch=get_object_or_404(Branch, pk=branch_id),
            destination_level=destination_level,
            month=month,
            year=year,
            amount_due=amount_due,
            amount_sent=0,
            status='pending',
            notes=notes,
            created_by=request.user,
            updated_by=request.user
        )
        
        # Set destination entity
        if destination_level == 'area':
            area_id = request.POST.get('area')
            remittance.area = get_object_or_404(Area, pk=area_id)
        elif destination_level == 'district':
            district_id = request.POST.get('district')
            remittance.district = get_object_or_404(District, pk=district_id)
        
        try:
            remittance.full_clean()
            remittance.save()
            messages.success(request, 'Remittance created successfully.')
            return redirect('contributions:hierarchy_remittance_detail', remittance_id=remittance.id)
        except Exception as e:
            messages.error(request, f'Error creating remittance: {str(e)}')
    
    # Get data for form
    branches = Branch.objects.all()
    areas = Area.objects.all()
    districts = District.objects.all()
    
    context = {
        'branches': branches,
        'areas': areas,
        'districts': districts,
    }
    
    return render(request, 'contributions/hierarchy_remittance_add.html', context)


@login_required
def hierarchy_remittance_pay(request, remittance_id):
    """Pay a pending remittance."""
    remittance = get_object_or_404(HierarchyRemittance, pk=remittance_id)
    
    # Check if user has permission to pay this remittance
    if request.user.branch != remittance.branch and not request.user.is_mission_admin:
        messages.error(request, 'You do not have permission to pay this remittance.')
        return redirect('contributions:hierarchy_remittance_detail', remittance_id=remittance.id)
    
    if remittance.status != 'pending':
        messages.error(request, 'Only pending remittances can be paid.')
        return redirect('contributions:hierarchy_remittance_detail', remittance_id=remittance.id)
    
    if request.method == 'POST':
        amount_sent = request.POST.get('amount_sent')
        payment_method = request.POST.get('payment_method')
        payment_reference = request.POST.get('payment_reference')
        payment_date = request.POST.get('payment_date')
        
        remittance.amount_sent = amount_sent
        remittance.payment_method = payment_method
        remittance.payment_reference = payment_reference
        remittance.payment_date = payment_date
        remittance.status = 'sent'
        remittance.updated_by = request.user
        remittance.save()
        
        messages.success(request, 'Remittance has been paid successfully.')
        return redirect('contributions:hierarchy_remittance_detail', remittance_id=remittance.id)
    
    context = {
        'remittance': remittance,
    }
    
    return render(request, 'contributions/hierarchy_remittance_pay.html', context)
