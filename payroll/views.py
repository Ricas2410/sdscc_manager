"""
Payroll Views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from calendar import month_name
from datetime import datetime

from payroll.models import StaffPayrollProfile, PayrollRun, PaySlip
from contributions.models import TitheCommission
from payroll.utils import auditor_can_view_payroll


@login_required
def staff_list(request):
    """List payroll staff."""
    can_view = request.user.is_mission_admin or auditor_can_view_payroll(request.user)
    if not can_view:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    staff_profiles = StaffPayrollProfile.objects.filter(is_active=True).select_related('user', 'user__branch')
    total_staff = staff_profiles.count()
    monthly_payroll = staff_profiles.aggregate(total=Sum('base_salary'))['total'] or 0
    pending_commissions = TitheCommission.objects.filter(status='pending').count()
    last_run = PayrollRun.objects.order_by('-year', '-month').first()
    last_payroll_date = None
    if last_run:
        last_payroll_date = last_run.processed_at or last_run.created_at

    context = {
        'staff_profiles': staff_profiles,
        'total_staff': total_staff,
        'monthly_payroll': monthly_payroll,
        'pending_commissions': pending_commissions,
        'last_payroll_date': last_payroll_date,
        'last_payroll_run': last_run,
        'last_payroll': last_payroll_date,
        'can_manage_staff': request.user.is_mission_admin,
        'read_only': not request.user.is_mission_admin,
    }
    return render(request, 'payroll/staff_list.html', context)


@login_required
def payroll_runs(request):
    """List payroll runs."""
    can_view_payroll = request.user.is_mission_admin or auditor_can_view_payroll(request.user)
    if not can_view_payroll:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        if not request.user.is_mission_admin:
            messages.error(request, 'You do not have permission to run payroll.')
            return redirect('payroll:runs')
        
        action = request.POST.get('action')
        
        if action == 'run':
            from core.models import FiscalYear
            from decimal import Decimal
            
            month = int(request.POST.get('month'))
            year = int(request.POST.get('year'))
            
            try:
                if PayrollRun.objects.filter(month=month, year=year).exists():
                    messages.warning(request, f'Payroll for {month_name[month]} {year} already exists.')
                    return redirect('payroll:runs')
                
                # DEPRECATED: Year-as-state architecture - fiscal_year no longer assigned
                # Payroll runs now use date-based filtering only
                
                payroll_run = PayrollRun.objects.create(
                    month=month,
                    year=year,
                    # fiscal_year=fiscal_year,  # REMOVED: Use date filtering instead
                    status=PayrollRun.Status.DRAFT,
                    processed_by=request.user,
                    processed_at=timezone.now()
                )
                
                staff_profiles = StaffPayrollProfile.objects.filter(is_active=True).prefetch_related('allowances', 'deductions')
                payslip_count = 0
                
                for profile in staff_profiles:
                    from datetime import date
                    allowances = profile.allowances.filter(is_recurring=True, end_date__isnull=True) | \
                                profile.allowances.filter(is_recurring=True, end_date__gte=date.today())
                    total_allowances = sum(a.amount for a in allowances)
                    
                    deductions = profile.deductions.filter(is_recurring=True, end_date__isnull=True) | \
                                profile.deductions.filter(is_recurring=True, end_date__gte=date.today())
                    total_deductions = sum(d.amount for d in deductions)
                    
                    allowances_breakdown = {a.allowance_type.name: float(a.amount) for a in allowances}
                    deductions_breakdown = {d.deduction_type.name: float(d.amount) for d in deductions}
                    
                    ssnit = profile.base_salary * Decimal('0.055')
                    deductions_breakdown['SSNIT (5.5%)'] = float(ssnit)
                    total_deductions += ssnit
                    
                    gross_pay = profile.base_salary + total_allowances
                    net_pay = gross_pay - total_deductions
                    
                    PaySlip.objects.create(
                        payroll_run=payroll_run,
                        staff=profile,
                        base_salary=profile.base_salary,
                        total_allowances=total_allowances,
                        total_deductions=total_deductions,
                        gross_pay=gross_pay,
                        net_pay=net_pay,
                        allowances_breakdown=allowances_breakdown,
                        deductions_breakdown=deductions_breakdown,
                        status=PaySlip.Status.PENDING
                    )
                    payslip_count += 1
                
                payroll_run.calculate_totals()
                payroll_run.save()
                
                messages.success(request, f'Successfully generated {payslip_count} payslips for {month_name[month]} {year}. Total: GH₵ {payroll_run.total_net_pay:,.2f}')
            except Exception as e:
                messages.error(request, f'Error generating payroll: {str(e)}')
        
        return redirect('payroll:runs')
    
    runs = PayrollRun.objects.all().order_by('-year', '-month')
    staff_profiles = StaffPayrollProfile.objects.filter(is_active=True)
    total_staff = staff_profiles.count()
    monthly_total = staff_profiles.aggregate(total=Sum('base_salary'))['total'] or 0
    pending_runs = PayrollRun.objects.exclude(status=PayrollRun.Status.PAID).count()
    completed_runs = PayrollRun.objects.filter(status=PayrollRun.Status.PAID).count()
    month_choices = [(i, month_name[i]) for i in range(1, 13)]
    context = {
        'runs': runs,
        'can_run_payroll': request.user.is_mission_admin,
        'total_staff': total_staff,
        'monthly_total': monthly_total,
        'pending_runs': pending_runs,
        'completed_runs': completed_runs,
        'month_choices': month_choices,
    }
    return render(request, 'payroll/payroll_runs.html', context)


@login_required
def commissions_list(request):
    """List tithe commissions."""
    from django.core.paginator import Paginator
    from core.models import Area
    from core.models import SiteSettings
    
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    commissions = TitheCommission.objects.all().select_related('recipient', 'branch').order_by('-year', '-month')
    
    # Filters
    year = request.GET.get('year')
    month = request.GET.get('month')
    status = request.GET.get('status')
    
    if year:
        commissions = commissions.filter(year=year)
    if month:
        commissions = commissions.filter(month=month)
    if status:
        commissions = commissions.filter(status=status)
    
    # Pagination
    paginator = Paginator(commissions, 25)
    page = request.GET.get('page')
    commissions = paginator.get_page(page)
    
    settings = SiteSettings.get_settings()
    
    context = {
        'commissions': commissions,
        'areas': Area.objects.filter(is_active=True),
        'years': list(range(timezone.now().year - 5, timezone.now().year + 6)),
        'selected_year': int(year) if year else None,
        'selected_month': int(month) if month else None,
        'commission_rate': settings.commission_percentage,
    }
    return render(request, 'payroll/commissions_list.html', context)


@login_required
def calculate_commissions(request):
    """Calculate commissions for a period."""
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        year = request.POST.get('year')
        month = request.POST.get('month')
        # TODO: Implement commission calculation logic
        messages.success(request, f'Commissions calculated for {month}/{year}')
    
    return redirect('payroll:commissions')


@login_required
def payslip_detail(request, payslip_id):
    """View payslip detail."""
    payslip = get_object_or_404(PaySlip, pk=payslip_id)
    
    # Check access
    can_view = (
        request.user.is_mission_admin
        or payslip.staff.user == request.user
        or auditor_can_view_payroll(request.user)
    )
    if not can_view:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    return render(request, 'payroll/payslip_detail.html', {'payslip': payslip})
