"""
Tithe Tracking & Commission Management Views
Handles tithe performance tracking, commission calculations, and reporting
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, Count, Avg
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date, datetime
from decimal import Decimal
import calendar

from core.models import Branch, Area, District, FiscalYear
from .models import Contribution, ContributionType, TitheCommission
from expenditure.models import Expenditure, ExpenditureCategory
from accounts.models import User


@login_required
def tithe_performance(request):
    """
    Tithe Performance Tracking Dashboard
    Shows branches meeting/not meeting targets, commission calculations
    """
    if not (request.user.is_mission_admin or request.user.is_branch_executive):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Get current month/year or from filters
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    area_id = request.GET.get('area')
    district_id = request.GET.get('district')
    
    # Get tithe contribution type
    try:
        tithe_type = ContributionType.objects.get(category='tithe', is_active=True)
    except ContributionType.DoesNotExist:
        messages.warning(request, 'Tithe contribution type not configured.')
        tithe_type = None
    
    # Get all branches
    branches = Branch.objects.select_related('district__area', 'pastor').filter(is_active=True)
    
    # Filter by hierarchy
    if request.user.is_branch_executive and request.user.branch:
        branches = branches.filter(id=request.user.branch_id)
    elif area_id:
        branches = branches.filter(district__area_id=area_id)
    elif district_id:
        branches = branches.filter(district_id=district_id)
    
    # Calculate tithe performance for each branch
    branch_performance = []
    total_target = Decimal('0.00')
    total_collected = Decimal('0.00')
    branches_met_target = 0
    total_commission = Decimal('0.00')
    
    for branch in branches:
        # Get tithe collected for the month
        tithe_collected = Decimal('0.00')
        if tithe_type:
            contributions = Contribution.objects.filter(
                branch=branch,
                contribution_type=tithe_type,
                date__month=month,
                date__year=year
            ).aggregate(total=Sum('amount'))
            tithe_collected = contributions['total'] or Decimal('0.00')
        
        # Calculate performance
        target = branch.monthly_tithe_target
        percentage = (tithe_collected / target * 100) if target > 0 else 0
        met_target = tithe_collected >= target
        variance = tithe_collected - target
        
        # Get or calculate commission
        commission_amount = Decimal('0.00')
        commission_status = 'N/A'
        commission_obj = None
        
        if branch.pastor:
            try:
                commission_obj = TitheCommission.objects.get(
                    branch=branch,
                    month=month,
                    year=year
                )
                commission_amount = commission_obj.commission_amount
                commission_status = commission_obj.get_status_display()
            except TitheCommission.DoesNotExist:
                # Calculate potential commission (10% of tithe if target met)
                if met_target:
                    commission_amount = tithe_collected * Decimal('0.10')
                    commission_status = 'Not Created'
        
        branch_performance.append({
            'branch': branch,
            'target': target,
            'collected': tithe_collected,
            'percentage': round(percentage, 2),
            'met_target': met_target,
            'variance': variance,
            'pastor': branch.pastor,
            'commission_amount': commission_amount,
            'commission_status': commission_status,
            'commission_obj': commission_obj,
        })
        
        total_target += target
        total_collected += tithe_collected
        if met_target:
            branches_met_target += 1
        total_commission += commission_amount
    
    # Sort by performance
    sort_by = request.GET.get('sort', 'percentage')
    if sort_by == 'percentage':
        branch_performance.sort(key=lambda x: x['percentage'], reverse=True)
    elif sort_by == 'collected':
        branch_performance.sort(key=lambda x: x['collected'], reverse=True)
    elif sort_by == 'variance':
        branch_performance.sort(key=lambda x: x['variance'], reverse=True)
    
    # Overall statistics
    overall_percentage = (total_collected / total_target * 100) if total_target > 0 else 0
    
    # Generate year list
    current_year = date.today().year
    years = list(range(current_year - 2, current_year + 2))
    
    # Generate month list
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    
    context = {
        'branch_performance': branch_performance,
        'month': month,
        'year': year,
        'month_name': calendar.month_name[month],
        'total_target': total_target,
        'total_collected': total_collected,
        'overall_percentage': round(overall_percentage, 2),
        'branches_met_target': branches_met_target,
        'total_branches': len(branch_performance),
        'total_commission': total_commission,
        'areas': Area.objects.filter(is_active=True),
        'districts': District.objects.filter(is_active=True).select_related('area'),
        'selected_area': area_id,
        'selected_district': district_id,
        'tithe_type': tithe_type,
        'years': years,
        'months': months,
    }
    
    return render(request, 'contributions/tithe_performance.html', context)


@login_required
def commission_management(request):
    """
    Commission Management Dashboard
    Create, approve, and track commission payments
    """
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'generate_commissions':
            # Generate commissions for a specific month/year
            month = int(request.POST.get('month'))
            year = int(request.POST.get('year'))
            commission_percentage = Decimal(request.POST.get('commission_percentage', '10.00'))
            
            created_count = 0
            skipped_no_pastor = 0
            try:
                fiscal_year = FiscalYear.get_current()
                tithe_type = ContributionType.objects.get(category='tithe', is_active=True)
                
                # Get ALL active branches, not just those with pastors
                branches = Branch.objects.filter(is_active=True)
                
                for branch in branches:
                    # Check if commission already exists
                    if TitheCommission.objects.filter(branch=branch, month=month, year=year).exists():
                        continue
                    
                    # Determine the recipient - pastor, branch head, or branch admin
                    recipient = branch.pastor
                    if not recipient:
                        # Try to find branch head or admin
                        from accounts.models import User
                        recipient = User.objects.filter(
                            branch=branch, 
                            role__in=['branch_head', 'branch_admin', 'branch_executive'],
                            is_active=True
                        ).first()
                    
                    if not recipient:
                        skipped_no_pastor += 1
                        continue
                    
                    # Calculate tithe collected
                    tithe_collected = Contribution.objects.filter(
                        branch=branch,
                        contribution_type=tithe_type,
                        date__month=month,
                        date__year=year
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                    
                    # Create commission record
                    commission = TitheCommission.objects.create(
                        recipient=recipient,
                        branch=branch,
                        fiscal_year=fiscal_year,
                        month=month,
                        year=year,
                        target_amount=branch.monthly_tithe_target,
                        tithe_collected=tithe_collected,
                        commission_percentage=commission_percentage,
                        created_by=request.user
                    )
                    commission.calculate_commission()
                    commission.save()
                    created_count += 1
                
                msg = f'Generated {created_count} commission records for {calendar.month_name[month]} {year}'
                if skipped_no_pastor:
                    msg += f' ({skipped_no_pastor} branches skipped - no pastor/branch head assigned)'
                messages.success(request, msg)
            except Exception as e:
                messages.error(request, f'Error generating commissions: {str(e)}')
        
        elif action == 'approve_commission':
            commission_id = request.POST.get('commission_id')
            try:
                commission = TitheCommission.objects.get(pk=commission_id)
                commission.status = 'approved'
                commission.approved_by = request.user
                commission.approved_at = timezone.now()
                commission.save()
                messages.success(request, f'Commission approved for {commission.recipient.get_full_name()}')
            except TitheCommission.DoesNotExist:
                messages.error(request, 'Commission not found')
        
        elif action == 'pay_commission':
            commission_id = request.POST.get('commission_id')
            payment_ref = request.POST.get('payment_reference', '')
            
            try:
                commission = TitheCommission.objects.get(pk=commission_id)
                
                # Create expenditure record for audit trail
                category, _ = ExpenditureCategory.objects.get_or_create(
                    name='Pastor Commission',
                    defaults={
                        'code': 'COMM',
                        'category_type': 'payroll',
                        'scope': 'mission',
                        'is_active': True
                    }
                )
                
                Expenditure.objects.create(
                    branch=commission.branch,
                    fiscal_year=commission.fiscal_year,
                    category=category,
                    level='mission',
                    amount=commission.commission_amount,
                    date=date.today(),
                    title=f'Pastor Commission - {commission.recipient.get_full_name()}',
                    description=f'Pastor Commission for {calendar.month_name[commission.month]} {commission.year}',
                    vendor=commission.recipient.get_full_name(),
                    reference_number=payment_ref,
                    status='approved',
                    approved_by=request.user,
                    approved_at=timezone.now(),
                    notes=f'Payment method: Bank transfer. Commission ID: {commission.id}'
                )
                
                # Mark commission as paid
                commission.status = 'paid'
                commission.paid_at = timezone.now()
                commission.notes = f'Payment Reference: {payment_ref}'
                commission.save()
                
                messages.success(request, f'Commission paid to {commission.recipient.get_full_name()} - GH₵{commission.commission_amount}')
            except TitheCommission.DoesNotExist:
                messages.error(request, 'Commission not found')
            except Exception as e:
                messages.error(request, f'Error processing payment: {str(e)}')
        
        return redirect('contributions:commission_management')
    
    # Get commissions
    month = int(request.GET.get('month', date.today().month))
    year = int(request.GET.get('year', date.today().year))
    status_filter = request.GET.get('status', '')
    
    commissions = TitheCommission.objects.select_related(
        'recipient', 'branch', 'branch__district', 'approved_by'
    ).filter(month=month, year=year)
    
    if status_filter:
        commissions = commissions.filter(status=status_filter)
    
    commissions = commissions.order_by('-commission_amount')
    
    # Calculate totals
    stats = commissions.aggregate(
        total_qualified=Count('id', filter=Q(is_qualified=True)),
        total_amount=Sum('commission_amount'),
        total_paid=Sum('commission_amount', filter=Q(status='paid')),
        total_pending=Sum('commission_amount', filter=Q(status='pending')),
    )
    
    # Generate year list
    current_year = date.today().year
    years = list(range(current_year - 2, current_year + 2))
    
    # Generate month list
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    
    context = {
        'commissions': commissions,
        'month': month,
        'year': year,
        'month_name': calendar.month_name[month],
        'stats': stats,
        'status_filter': status_filter,
        'years': years,
        'months': months,
    }
    
    return render(request, 'contributions/commission_management.html', context)


@login_required
def commission_report_print(request):
    """
    Printable Commission Report
    Shows executives, branches, and commissions
    """
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    month = int(request.GET.get('month', date.today().month))
    year = int(request.GET.get('year', date.today().year))
    
    # Get all commissions for the period
    commissions = TitheCommission.objects.select_related(
        'recipient', 'branch__district__area'
    ).filter(month=month, year=year).order_by(
        'branch__district__area__name', 'branch__district__name', 'branch__name'
    )
    
    # Group by area
    areas_data = {}
    for commission in commissions:
        area_name = commission.branch.district.area.name
        if area_name not in areas_data:
            areas_data[area_name] = {
                'districts': {},
                'total_commission': Decimal('0.00'),
                'total_tithe': Decimal('0.00'),
            }
        
        district_name = commission.branch.district.name
        if district_name not in areas_data[area_name]['districts']:
            areas_data[area_name]['districts'][district_name] = {
                'branches': [],
                'total_commission': Decimal('0.00'),
                'total_tithe': Decimal('0.00'),
            }
        
        areas_data[area_name]['districts'][district_name]['branches'].append(commission)
        areas_data[area_name]['districts'][district_name]['total_commission'] += commission.commission_amount
        areas_data[area_name]['districts'][district_name]['total_tithe'] += commission.tithe_collected
        areas_data[area_name]['total_commission'] += commission.commission_amount
        areas_data[area_name]['total_tithe'] += commission.tithe_collected
    
    # Overall totals
    grand_total = commissions.aggregate(
        total_commission=Sum('commission_amount'),
        total_tithe=Sum('tithe_collected'),
        total_target=Sum('target_amount'),
    )
    
    context = {
        'month': month,
        'year': year,
        'month_name': calendar.month_name[month],
        'areas_data': areas_data,
        'grand_total': grand_total,
        'generated_at': timezone.now(),
        'generated_by': request.user,
    }
    
    return render(request, 'contributions/commission_report_print.html', context)
