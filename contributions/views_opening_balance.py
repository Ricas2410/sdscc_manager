"""
Views for opening balances for Branch and Mission CASH
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.db import transaction
from django.http import HttpResponse
import csv

from .models_opening_balance import OpeningBalance
from .models import ContributionType
from accounts.permissions import mission_admin_required
from core.models import Branch


@login_required
def opening_balance_list(request):
    """View all opening balances."""
    user = request.user
    
    # Filter opening balances based on user role
    if user.is_mission_admin or user.is_auditor:
        opening_balances = OpeningBalance.objects.all().order_by('-date', '-created_at')
    elif user.is_branch_executive and user.branch:
        opening_balances = OpeningBalance.objects.filter(
            branch=user.branch
        ).order_by('-date', '-created_at')
    elif user.is_area_executive and user.managed_area:
        opening_balances = OpeningBalance.objects.filter(
            branch__district__area=user.managed_area
        ).order_by('-date', '-created_at')
    elif user.is_district_executive and user.managed_district:
        opening_balances = OpeningBalance.objects.filter(
            branch__district=user.managed_district
        ).order_by('-date', '-created_at')
    else:
        opening_balances = OpeningBalance.objects.none()
    
    context = {
        'opening_balances': opening_balances,
    }
    
    return render(request, 'contributions/opening_balances.html', context)


@login_required
def opening_balance_detail(request, balance_id):
    """View details of a specific opening balance."""
    balance = get_object_or_404(OpeningBalance, pk=balance_id)
    
    # Check if user has permission to view this opening balance
    user = request.user
    if not (user.is_mission_admin or user.is_auditor):
        if user.is_branch_executive and user.branch != balance.branch:
            messages.error(request, 'You do not have permission to view this opening balance.')
            return redirect('contributions:opening_balances')
    
    context = {
        'balance': balance,
    }
    
    return render(request, 'contributions/opening_balance_detail.html', context)


@login_required
@mission_admin_required
def opening_balance_add(request):
    """Add a new opening balance."""
    if request.method == 'POST':
        # Process form data
        level = request.POST.get('level')
        branch_id = request.POST.get('branch') if level == 'branch' else None
        contribution_type_id = request.POST.get('contribution_type')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        description = request.POST.get('description', 'Opening Balance – Pre-System Funds')
        
        # Create opening balance object
        balance = OpeningBalance(
            level=level,
            amount=amount,
            contribution_type_id=contribution_type_id,
            date=date,
            description=description,
            status='pending',
            created_by=request.user,
            updated_by=request.user
        )
        
        # Set branch if applicable
        if level == 'branch' and branch_id:
            balance.branch = get_object_or_404(Branch, pk=branch_id)
        
        try:
            balance.full_clean()
            balance.save()
            messages.success(request, 'Opening balance created successfully.')
            return redirect('contributions:opening_balance_detail', balance_id=balance.id)
        except Exception as e:
            messages.error(request, f'Error creating opening balance: {str(e)}')
    
    # Get data for form
    branches = Branch.objects.all().order_by('name')
    contribution_types = ContributionType.objects.filter(is_active=True).order_by('name')
    
    context = {
        'branches': branches,
        'contribution_types': contribution_types,
    }
    
    return render(request, 'contributions/opening_balance_add.html', context)


@login_required
@mission_admin_required
def opening_balance_approve(request, balance_id):
    """Approve a pending opening balance."""
    balance = get_object_or_404(OpeningBalance, pk=balance_id)
    
    if balance.status != 'pending':
        messages.error(request, 'Only pending opening balances can be approved.')
        return redirect('contributions:opening_balance_detail', balance_id=balance.id)
    
    from core.ledger_service import LedgerService
    from core.ledger_models import LedgerEntry
    from decimal import Decimal
    
    try:
        with transaction.atomic():
            # Update status
            balance.status = 'approved'
            balance.approved_by = request.user
            balance.approved_at = timezone.now()
            balance.save()
            
            # Create ledger entry for opening balance
            if balance.level == 'branch':
                # Branch opening balance
                LedgerEntry.objects.create(
                    entry_type=LedgerEntry.EntryType.CASH,
                    owner_type=LedgerEntry.OwnerType.BRANCH,
                    owner_branch=balance.branch,
                    amount=balance.amount,
                    source_type=LedgerEntry.SourceType.OPENING_BALANCE,
                    entry_date=balance.date,
                    description=f"Opening Balance – Pre-System Funds: {balance.contribution_type.name}",
                    reference=f"OB-{balance.id[:8].upper()}",
                    status=LedgerEntry.Status.ACTIVE
                )
            else:
                # Mission opening balance
                LedgerEntry.objects.create(
                    entry_type=LedgerEntry.EntryType.CASH,
                    owner_type=LedgerEntry.OwnerType.MISSION,
                    amount=balance.amount,
                    source_type=LedgerEntry.SourceType.OPENING_BALANCE,
                    entry_date=balance.date,
                    description=f"Opening Balance – Pre-System Funds: {balance.contribution_type.name}",
                    reference=f"OB-{balance.id[:8].upper()}",
                    status=LedgerEntry.Status.ACTIVE
                )
            
            messages.success(request, 'Opening balance has been approved and ledger entries created.')
    except Exception as e:
        messages.error(request, f'Error approving opening balance: {str(e)}')
    
    return redirect('contributions:opening_balance_detail', balance_id=balance.id)


@login_required
@mission_admin_required
def opening_balance_reject(request, balance_id):
    """Reject a pending opening balance."""
    balance = get_object_or_404(OpeningBalance, pk=balance_id)
    
    if balance.status != 'pending':
        messages.error(request, 'Only pending opening balances can be rejected.')
        return redirect('contributions:opening_balance_detail', balance_id=balance.id)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason')
        
        balance.status = 'rejected'
        balance.rejection_reason = rejection_reason
        balance.save()
        
        messages.success(request, 'Opening balance has been rejected successfully.')
        return redirect('contributions:opening_balance_detail', balance_id=balance.id)
    
    context = {
        'balance': balance,
    }
    
    return render(request, 'contributions/opening_balance_reject.html', context)


@login_required
@mission_admin_required
def opening_balance_export(request, format='csv'):
    """Export all opening balances to CSV."""
    opening_balances = OpeningBalance.objects.all().order_by('-date', '-created_at')
    
    if format == 'csv':
        # Generate CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="opening_balances.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Level', 'Entity', 'Contribution Type', 'Amount', 'Date', 'Status', 'Description'])
        
        for balance in opening_balances:
            entity = balance.branch.name if balance.branch else 'Mission'
            writer.writerow([
                balance.get_level_display(),
                entity,
                balance.contribution_type.name,
                balance.amount,
                balance.date,
                balance.get_status_display(),
                balance.description
            ])
        
        return response
    
    # Invalid format
    messages.error(request, 'Invalid export format.')
    return redirect('contributions:opening_balances')
