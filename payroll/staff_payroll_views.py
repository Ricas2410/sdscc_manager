"""
Comprehensive Staff & Payroll Management Views
Handles staff management, salary configuration, and payroll processing
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, Count
from django.http import JsonResponse
from django.utils import timezone
from datetime import date
from decimal import Decimal
import calendar

from accounts.models import User
from .models import StaffPayrollProfile, PayrollRun, PaySlip
from core.models import FiscalYear
from expenditure.models import Expenditure, ExpenditureCategory


@login_required
def staff_payroll_management(request):
    """
    Comprehensive Staff & Payroll Management Page
    Shows all staff with salary info, allows adding/editing staff, and managing payroll
    """
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Get all staff (pastors and staff role users)
    staff_profiles = StaffPayrollProfile.objects.select_related('user', 'user__branch').filter(is_active=True)
    
    # Get all users who are pastors or staff but don't have payroll profiles
    users_without_payroll = User.objects.filter(
        Q(role='pastor') | Q(role='staff'),
        is_active=True
    ).exclude(
        id__in=staff_profiles.values_list('user_id', flat=True)
    ).select_related('branch')
    
    # Calculate totals
    total_monthly_salary = staff_profiles.aggregate(total=Sum('base_salary'))['total'] or Decimal('0.00')
    total_staff_count = staff_profiles.count()
    
    # Get recent payroll runs
    recent_payrolls = PayrollRun.objects.all().order_by('-year', '-month')[:5]
    
    context = {
        'staff_profiles': staff_profiles,
        'users_without_payroll': users_without_payroll,
        'total_monthly_salary': total_monthly_salary,
        'total_staff_count': total_staff_count,
        'recent_payrolls': recent_payrolls,
    }
    
    return render(request, 'payroll/staff_payroll_management.html', context)


@login_required
def add_staff_to_payroll(request):
    """Add a user to payroll system."""
    from .models import StaffAllowance, AllowanceType
    from datetime import date
    
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        base_salary = Decimal(request.POST.get('base_salary', '0'))
        housing_allowance = Decimal(request.POST.get('housing_allowance', '0'))
        transport_allowance = Decimal(request.POST.get('transport_allowance', '0'))
        other_allowances = Decimal(request.POST.get('other_allowances', '0'))
        position = request.POST.get('position', '')
        
        try:
            user = User.objects.get(pk=user_id)
            
            # Check if already exists
            if StaffPayrollProfile.objects.filter(user=user).exists():
                messages.warning(request, f'{user.get_full_name()} is already on payroll.')
                return redirect('payroll:staff_management')
            
            # Generate employee ID
            last_profile = StaffPayrollProfile.objects.order_by('-employee_id').first()
            if last_profile and last_profile.employee_id.startswith('EMP'):
                try:
                    last_num = int(last_profile.employee_id[3:])
                    employee_id = f'EMP{last_num + 1:04d}'
                except ValueError:
                    employee_id = f'EMP{StaffPayrollProfile.objects.count() + 1:04d}'
            else:
                employee_id = f'EMP{StaffPayrollProfile.objects.count() + 1:04d}'
            
            # Create payroll profile (without allowance fields)
            profile = StaffPayrollProfile.objects.create(
                user=user,
                employee_id=employee_id,
                base_salary=base_salary,
                position=position or user.get_role_display(),
                hire_date=date.today(),
                is_active=True
            )
            
            # Create allowances as separate records if provided
            today = date.today()
            
            if housing_allowance > 0:
                housing_type, _ = AllowanceType.objects.get_or_create(
                    code='HOUSING',
                    defaults={'name': 'Housing Allowance', 'is_taxable': False}
                )
                StaffAllowance.objects.create(
                    staff=profile,
                    allowance_type=housing_type,
                    amount=housing_allowance,
                    is_recurring=True,
                    start_date=today
                )
            
            if transport_allowance > 0:
                transport_type, _ = AllowanceType.objects.get_or_create(
                    code='TRANSPORT',
                    defaults={'name': 'Transport Allowance', 'is_taxable': False}
                )
                StaffAllowance.objects.create(
                    staff=profile,
                    allowance_type=transport_type,
                    amount=transport_allowance,
                    is_recurring=True,
                    start_date=today
                )
            
            if other_allowances > 0:
                other_type, _ = AllowanceType.objects.get_or_create(
                    code='OTHER',
                    defaults={'name': 'Other Allowances', 'is_taxable': False}
                )
                StaffAllowance.objects.create(
                    staff=profile,
                    allowance_type=other_type,
                    amount=other_allowances,
                    is_recurring=True,
                    start_date=today
                )
            
            messages.success(request, f'{user.get_full_name()} added to payroll successfully.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        except Exception as e:
            messages.error(request, f'Error adding to payroll: {str(e)}')
    
    return redirect('payroll:staff_management')


@login_required
def update_staff_salary(request, profile_id):
    """Update staff salary information."""
    from .models import StaffAllowance, AllowanceType
    from datetime import date
    
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    profile = get_object_or_404(StaffPayrollProfile, pk=profile_id)
    
    if request.method == 'POST':
        profile.base_salary = Decimal(request.POST.get('base_salary', profile.base_salary))
        profile.position = request.POST.get('position', profile.position)
        profile.save()
        
        # Update or create allowances
        housing_allowance = Decimal(request.POST.get('housing_allowance', '0'))
        transport_allowance = Decimal(request.POST.get('transport_allowance', '0'))
        other_allowances = Decimal(request.POST.get('other_allowances', '0'))
        today = date.today()
        
        # Housing allowance
        if housing_allowance > 0:
            housing_type, _ = AllowanceType.objects.get_or_create(
                code='HOUSING',
                defaults={'name': 'Housing Allowance', 'is_taxable': False}
            )
            allowance, created = StaffAllowance.objects.update_or_create(
                staff=profile,
                allowance_type=housing_type,
                defaults={'amount': housing_allowance, 'is_recurring': True, 'start_date': today}
            )
        else:
            StaffAllowance.objects.filter(staff=profile, allowance_type__code='HOUSING').delete()
        
        # Transport allowance
        if transport_allowance > 0:
            transport_type, _ = AllowanceType.objects.get_or_create(
                code='TRANSPORT',
                defaults={'name': 'Transport Allowance', 'is_taxable': False}
            )
            StaffAllowance.objects.update_or_create(
                staff=profile,
                allowance_type=transport_type,
                defaults={'amount': transport_allowance, 'is_recurring': True, 'start_date': today}
            )
        else:
            StaffAllowance.objects.filter(staff=profile, allowance_type__code='TRANSPORT').delete()
        
        # Other allowances
        if other_allowances > 0:
            other_type, _ = AllowanceType.objects.get_or_create(
                code='OTHER',
                defaults={'name': 'Other Allowances', 'is_taxable': False}
            )
            StaffAllowance.objects.update_or_create(
                staff=profile,
                allowance_type=other_type,
                defaults={'amount': other_allowances, 'is_recurring': True, 'start_date': today}
            )
        else:
            StaffAllowance.objects.filter(staff=profile, allowance_type__code='OTHER').delete()
        
        messages.success(request, f'Salary updated for {profile.user.get_full_name()}')
    
    return redirect('payroll:staff_management')


@login_required
def payroll_processing(request):
    """
    Payroll Processing Page
    Generate payroll for a month, mark as paid, view payslips
    """
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'generate':
            month = int(request.POST.get('month'))
            year = int(request.POST.get('year'))
            
            try:
                # Check if payroll already exists
                if PayrollRun.objects.filter(month=month, year=year).exists():
                    messages.warning(request, f'Payroll for {calendar.month_name[month]} {year} already exists.')
                    return redirect('payroll:payroll_processing')
                
                fiscal_year = FiscalYear.get_current()
                
                # Create payroll run
                payroll_run = PayrollRun.objects.create(
                    month=month,
                    year=year,
                    fiscal_year=fiscal_year,
                    status='draft',
                    created_by=request.user
                )
                
                # Generate payslips for all active staff
                from .models import StaffAllowance, StaffDeduction
                
                staff_profiles = StaffPayrollProfile.objects.filter(is_active=True).prefetch_related('allowances', 'deductions')
                payslip_count = 0
                total_net = Decimal('0.00')
                
                for profile in staff_profiles:
                    # Calculate total allowances from StaffAllowance records
                    allowances = profile.allowances.filter(is_recurring=True, end_date__isnull=True) | \
                                profile.allowances.filter(is_recurring=True, end_date__gte=date.today())
                    total_allowances = sum(a.amount for a in allowances)
                    
                    # Calculate total deductions from StaffDeduction records
                    deductions = profile.deductions.filter(is_recurring=True, end_date__isnull=True) | \
                                profile.deductions.filter(is_recurring=True, end_date__gte=date.today())
                    total_deductions = sum(d.amount for d in deductions)
                    
                    # Build allowance breakdown
                    allowances_breakdown = {a.allowance_type.name: float(a.amount) for a in allowances}
                    deductions_breakdown = {d.deduction_type.name: float(d.amount) for d in deductions}
                    
                    # Add SSNIT deduction (5.5%)
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
                        status='pending'
                    )
                    payslip_count += 1
                    total_net += net_pay
                
                # Update payroll run totals
                payroll_run.calculate_totals()
                payroll_run.save()
                
                messages.success(request, f'Generated {payslip_count} payslips for {calendar.month_name[month]} {year}')
            except Exception as e:
                messages.error(request, f'Error generating payroll: {str(e)}')
        
        elif action == 'mark_all_paid':
            payroll_id = request.POST.get('payroll_id')
            payment_date = date.today()
            payment_ref = f'PAY-{date.today().strftime("%Y%m%d")}-BATCH'
            
            try:
                payroll_run = PayrollRun.objects.get(id=payroll_id)
                payslips = PaySlip.objects.filter(payroll_run=payroll_run, status='pending')
                
                # Create expenditure category for payroll if not exists
                category, _ = ExpenditureCategory.objects.get_or_create(
                    name='Staff Salary',
                    defaults={
                        'code': 'SAL',
                        'category_type': 'payroll',
                        'scope': 'mission',
                        'is_active': True
                    }
                )
                
                fiscal_year = FiscalYear.get_current()
                
                for payslip in payslips:
                    # Create expenditure record for audit trail
                    Expenditure.objects.create(
                        branch=payslip.staff.user.branch if payslip.staff.user.branch else None,
                        fiscal_year=fiscal_year,
                        category=category,
                        level='mission',
                        amount=payslip.net_pay,
                        date=payment_date,
                        title=f'Salary - {payslip.staff.user.get_full_name()}',
                        description=f'Salary payment for {calendar.month_name[payslip.payroll_run.month]} {payslip.payroll_run.year}',
                        vendor=payslip.staff.user.get_full_name(),
                        reference_number=payment_ref,
                        status='approved',
                        approved_by=request.user,
                        approved_at=timezone.now(),
                        notes=f'Payment method: Bank transfer. Payslip ID: {payslip.id}'
                    )
                    
                    # Mark payslip as paid
                    payslip.status = 'paid'
                    payslip.payment_date = payment_date
                    payslip.payment_reference = payment_ref
                    payslip.save()
                
                messages.success(request, f'Marked {len(payslips)} payslips as paid.')
            except Exception as e:
                messages.error(request, f'Error processing batch payment: {str(e)}')
        
        elif action == 'mark_paid':
            payslip_id = request.POST.get('payslip_id')
            payment_date = date.today()
            payment_ref = f'PAY-{date.today().strftime("%Y%m%d")}-{payslip_id[:8]}' if payslip_id else f'PAY-{date.today().strftime("%Y%m%d")}'
            
            try:
                if payslip_id:
                    payslips = PaySlip.objects.filter(id=payslip_id, status='pending')
                else:
                    # Fallback to multiple selection
                    payslip_ids = request.POST.getlist('payslip_ids')
                    payslips = PaySlip.objects.filter(id__in=payslip_ids, status='pending')
                
                # Create expenditure category for payroll if not exists
                category, _ = ExpenditureCategory.objects.get_or_create(
                    name='Staff Salary',
                    defaults={
                        'code': 'SAL',
                        'category_type': 'payroll',
                        'scope': 'mission',
                        'is_active': True
                    }
                )
                
                fiscal_year = FiscalYear.get_current()
                
                for payslip in payslips:
                    # Create expenditure record for audit trail
                    Expenditure.objects.create(
                        branch=payslip.staff.user.branch if payslip.staff.user.branch else None,
                        fiscal_year=fiscal_year,
                        category=category,
                        level='mission',
                        amount=payslip.net_pay,
                        date=payment_date,
                        title=f'Salary - {payslip.staff.user.get_full_name()}',
                        description=f'Salary payment for {calendar.month_name[payslip.payroll_run.month]} {payslip.payroll_run.year}',
                        vendor=payslip.staff.user.get_full_name(),
                        reference_number=payment_ref,
                        status='approved',
                        approved_by=request.user,
                        approved_at=timezone.now(),
                        notes=f'Payment method: Bank transfer. Payslip ID: {payslip.id}'
                    )
                    
                    # Mark payslip as paid
                    payslip.status = 'paid'
                    payslip.payment_date = payment_date
                    payslip.payment_reference = payment_ref
                    payslip.save()
                
                messages.success(request, f'Marked {len(payslips)} payslips as paid.')
            except Exception as e:
                messages.error(request, f'Error processing payment: {str(e)}')
        
        return redirect('payroll:payroll_processing')
    
    # Get payroll runs
    month = int(request.GET.get('month', date.today().month))
    year = int(request.GET.get('year', date.today().year))
    
    payroll_run = PayrollRun.objects.filter(month=month, year=year).prefetch_related('payslips__staff__user').first()
    
    # Calculate paid count if payroll exists
    paid_count = 0
    if payroll_run:
        paid_count = payroll_run.payslips.filter(status='paid').count()
    
    # Month/year options
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    years = list(range(date.today().year - 2, date.today().year + 2))
    
    context = {
        'payroll_run': payroll_run,
        'paid_count': paid_count,
        'month': month,
        'year': year,
        'month_name': calendar.month_name[month],
        'months': months,
        'years': years,
    }
    
    return render(request, 'payroll/payroll_processing.html', context)


@login_required
def my_payroll(request):
    """
    Pastor/Staff view of their own payroll
    Shows their salary, payslips, and payment history
    """
    if not (request.user.is_pastor or request.user.is_staff):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    try:
        staff_profile = StaffPayrollProfile.objects.get(user=request.user, is_active=True)
    except StaffPayrollProfile.DoesNotExist:
        staff_profile = None
    
    # Get payslips
    payslips = PaySlip.objects.filter(
        staff__user=request.user
    ).select_related('payroll_run').order_by('-payroll_run__year', '-payroll_run__month')
    
    # Calculate totals
    total_paid = payslips.filter(status='paid').aggregate(total=Sum('net_pay'))['total'] or Decimal('0.00')
    total_pending = payslips.filter(status='pending').aggregate(total=Sum('net_pay'))['total'] or Decimal('0.00')
    
    # Get available years for filter
    available_years = list(set(payslip.payroll_run.year for payslip in payslips))
    available_years.sort(reverse=True)
    
    # Add month names to payslips
    import calendar
    for payslip in payslips:
        payslip.payroll_run.month_name = calendar.month_name[payslip.payroll_run.month]
    
    context = {
        'staff_profile': staff_profile,
        'payslips': payslips,
        'total_paid': total_paid,
        'total_pending': total_pending,
        'available_years': available_years,
    }
    
    return render(request, 'payroll/my_payroll.html', context)


@login_required
def payslip_detail(request, payslip_id):
    """View detailed payslip."""
    if not (request.user.is_pastor or request.user.is_staff or request.user.is_mission_admin):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Admin can view any payslip, staff can only view their own
    if request.user.is_mission_admin:
        payslip = get_object_or_404(
            PaySlip.objects.select_related('staff', 'staff__user', 'payroll_run'),
            id=payslip_id
        )
    else:
        payslip = get_object_or_404(
            PaySlip.objects.select_related('staff', 'staff__user', 'payroll_run'),
            id=payslip_id,
            staff__user=request.user
        )
    
    # Add month name
    import calendar
    payslip.payroll_run.month_name = calendar.month_name[payslip.payroll_run.month]
    
    # Get site settings for church branding
    from core.models import SiteSettings
    site_settings = SiteSettings.objects.first()
    
    return render(request, 'payroll/payslip_detail.html', {
        'payslip': payslip,
        'site_settings': site_settings
    })


@login_required
def payment_history(request):
    """Payment history page showing monthly salary breakdown with filtering."""
    from decimal import Decimal
    from calendar import month_name
    
    # Get filter parameters
    year = request.GET.get('year', str(timezone.now().year))
    month = request.GET.get('month', '')
    staff_id = request.GET.get('staff')
    
    # Check permissions
    is_admin = request.user.is_mission_admin
    is_auditor = request.user.is_auditor and SiteSettings.get_settings().allow_auditor_payroll_access
    is_own_record = False
    
    if not (is_admin or is_auditor):
        # Regular staff can only view their own records
        try:
            profile = StaffPayrollProfile.objects.get(user=request.user, is_active=True)
            is_own_record = True
            staff_id = str(profile.id)
        except StaffPayrollProfile.DoesNotExist:
            messages.error(request, 'You do not have a payroll profile.')
            return redirect('core:dashboard')
    
    # Base queryset
    payslips = PaySlip.objects.select_related(
        'staff_profile__user',
        'staff_profile__position',
        'payroll_run'
    ).order_by('-payroll_run__year', '-payroll_run__month', 'staff_profile__user__last_name')
    
    # Apply filters
    if year:
        payslips = payslips.filter(payroll_run__year=year)
    
    if month:
        payslips = payslips.filter(payroll_run__month=month)
    
    if staff_id:
        payslips = payslips.filter(staff_profile_id=staff_id)
    
    # Calculate summary statistics
    total_gross_pay = payslips.aggregate(total=Sum('gross_pay'))['total'] or Decimal('0.00')
    total_deductions = payslips.aggregate(total=Sum('total_deductions'))['total'] or Decimal('0.00')
    total_net_pay = payslips.aggregate(total=Sum('net_pay'))['total'] or Decimal('0.00')
    total_payslips = payslips.count()
    
    # Get monthly breakdown
    monthly_breakdown = payslips.values(
        'payroll_run__year',
        'payroll_run__month'
    ).annotate(
        total_gross=Sum('gross_pay'),
        total_deductions=Sum('total_deductions'),
        total_net=Sum('net_pay'),
        payslip_count=Count('id')
    ).order_by('-payroll_run__year', '-payroll_run__month')
    
    # Get staff list (for filter)
    if is_admin or is_auditor:
        staff_profiles = StaffPayrollProfile.objects.filter(is_active=True).select_related('user')
    else:
        staff_profiles = StaffPayrollProfile.objects.filter(user=request.user, is_active=True)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(payslips, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'payslips': page_obj,
        'staff_profiles': staff_profiles,
        'selected_year': year,
        'selected_month': month,
        'selected_staff': staff_id,
        'years': range(timezone.now().year - 3, timezone.now().year + 1),
        'months': [(i, month_name[i]) for i in range(1, 13)],
        
        # Summary
        'total_gross_pay': total_gross_pay,
        'total_deductions': total_deductions,
        'total_net_pay': total_net_pay,
        'total_payslips': total_payslips,
        
        # Monthly breakdown
        'monthly_breakdown': monthly_breakdown,
        
        # Permissions
        'is_admin': is_admin,
        'is_auditor': is_auditor,
        'is_own_record': is_own_record,
    }
    
    return render(request, 'payroll/payment_history.html', context)


@login_required
def export_payment_history(request):
    """Export payment history to Excel."""
    from decimal import Decimal
    from calendar import month_name
    
    # Get filter parameters
    year = request.GET.get('year', str(timezone.now().year))
    month = request.GET.get('month', '')
    staff_id = request.GET.get('staff')
    
    # Check permissions
    is_admin = request.user.is_mission_admin
    is_auditor = request.user.is_auditor and SiteSettings.get_settings().allow_auditor_payroll_access
    
    if not (is_admin or is_auditor):
        # Regular staff can only export their own records
        try:
            profile = StaffPayrollProfile.objects.get(user=request.user, is_active=True)
            staff_id = str(profile.id)
        except StaffPayrollProfile.DoesNotExist:
            messages.error(request, 'You do not have a payroll profile.')
            return redirect('payroll:payment_history')
    
    # Base queryset
    payslips = PaySlip.objects.select_related(
        'staff_profile__user',
        'staff_profile__position',
        'payroll_run'
    ).order_by('-payroll_run__year', '-payroll_run__month', 'staff_profile__user__last_name')
    
    # Apply filters
    if year:
        payslips = payslips.filter(payroll_run__year=year)
    if month:
        payslips = payslips.filter(payroll_run__month=month)
    if staff_id:
        payslips = payslips.filter(staff_profile_id=staff_id)
    
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill
        from openpyxl.utils import get_column_letter
    except ImportError:
        messages.error(request, 'Excel export requires openpyxl package.')
        return redirect('payroll:payment_history')
    
    # Create workbook
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    
    # Payment History Sheet
    ws = wb.create_sheet("Payment History", 0)
    
    # Headers styling
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    
    # Headers
    headers = ["Year", "Month", "Staff ID", "Staff Name", "Position", 
               "Basic Salary", "Allowances", "Gross Pay", "SSNIT", "Other Deductions", 
               "Total Deductions", "Net Pay", "Payment Status"]
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
    
    # Data rows
    for row, payslip in enumerate(payslips, 2):
        data = [
            payslip.payroll_run.year,
            month_name[payslip.payroll_run.month],
            payslip.staff_profile.user.username,
            payslip.staff_profile.user.get_full_name(),
            payslip.staff_profile.position.name if payslip.staff_profile.position else "N/A",
            payslip.basic_salary,
            payslip.total_allowances,
            payslip.gross_pay,
            payslip.ssnit_deduction,
            payslip.total_deductions - payslip.ssnit_deduction,
            payslip.total_deductions,
            payslip.net_pay,
            payslip.get_payment_status_display()
        ]
        
        for col, value in enumerate(data, 1):
            cell = ws.cell(row=row, column=col, value=value)
            if col >= 6 and col <= 12:  # Amount columns
                cell.number_format = '#,##0.00'
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Create response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"payment_history_{year}_{month or 'all'}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    wb.save(response)
    return response


@login_required
def export_payroll(request):
    """Export payroll to Excel."""
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    month = int(request.GET.get('month', date.today().month))
    year = int(request.GET.get('year', date.today().year))
    
    payroll_run = PayrollRun.objects.filter(month=month, year=year).prefetch_related('payslips__staff__user').first()
    
    if not payroll_run:
        messages.error(request, 'No payroll found for the selected period.')
        return redirect('payroll:payroll_processing')
    
    # Create Excel file
    import pandas as pd
    from django.http import HttpResponse
    
    # Get site settings for church branding
    from core.models import SiteSettings
    site_settings = SiteSettings.objects.first()
    church_name = site_settings.site_name if site_settings and site_settings.site_name != 'SDSCC' else (site_settings.tagline if site_settings else 'Seventh Day Sabbath Church of Christ')
    
    data = []
    for payslip in payroll_run.payslips.all():
        data.append({
            'Employee ID': payslip.staff.employee_id or '',
            'Employee Name': payslip.staff.user.get_full_name(),
            'Position': payslip.staff.position or '',
            'Email': payslip.staff.user.email,
            'Phone': payslip.staff.user.phone or '',
            'Base Salary': payslip.base_salary,
            'Total Allowances': payslip.total_allowances,
            'Gross Pay': payslip.gross_pay,
            'Total Deductions': payslip.total_deductions,
            'Net Pay': payslip.net_pay,
            'Status': payslip.get_status_display(),
            'Payment Date': payslip.payment_date or '',
            'Payment Reference': payslip.payment_reference or '',
        })
    
    df = pd.DataFrame(data)
    
    # Create response
    import calendar
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{church_name.replace(" ", "_")}_Payroll_{calendar.month_name[month]}_{year}.xlsx"'
    
    # Save to response
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Payroll')
        
        # Add summary sheet
        summary_data = {
            'Metric': ['Church Name', 'Pay Period', 'Total Employees', 'Total Gross Pay', 'Total Deductions', 'Total Net Pay', 'Paid Employees', 'Pending Employees'],
            'Value': [
                church_name,
                f'{calendar.month_name[month]} {year}',
                payroll_run.payslips.count(),
                payroll_run.total_gross,
                payroll_run.total_deductions,
                payroll_run.total_net_pay,
                payroll_run.payslips.filter(status='paid').count(),
                payroll_run.payslips.filter(status='pending').count(),
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, index=False, sheet_name='Summary')
    
    return response


@login_required
def download_payslip(request, payslip_id):
    """Download payslip as PDF."""
    if not (request.user.is_pastor or request.user.is_staff):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    payslip = get_object_or_404(
        PaySlip.objects.select_related('staff', 'staff__user', 'payroll_run'),
        id=payslip_id,
        staff__user=request.user
    )
    
    # For now, return a simple text response
    # In production, you would generate a PDF here
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="payslip_{payslip.staff.employee_id}_{payslip.payroll_run.month}_{payslip.payroll_run.year}.txt"'
    
    import calendar
    
    # Get site settings for church branding
    from core.models import SiteSettings
    site_settings = SiteSettings.objects.first()
    church_name = site_settings.site_name if site_settings and site_settings.site_name != 'SDSCC' else (site_settings.tagline if site_settings else 'Seventh Day Sabbath Church of Christ')
    
    content = f"""
{church_name}
OFFICIAL PAYSLIP - {payslip.payroll_run.month_name} {payslip.payroll_run.year}
{'='*60}

{site_settings.address if site_settings and site_settings.address else ''}

Employee Details:
- Name: {payslip.staff.user.get_full_name()}
- ID: {payslip.staff.employee_id}
- Position: {payslip.staff.position}

Earnings:
- Base Salary: GH₵{payslip.base_salary:,.2f}
- Total Allowances: GH₵{payslip.total_allowances:,.2f}
- Gross Pay: GH₵{payslip.gross_pay:,.2f}

Deductions:
- Total Deductions: GH₵{payslip.total_deductions:,.2f}

Net Pay: GH₵{payslip.net_pay:,.2f}

Payment Status: {payslip.get_status_display()}
Payment Date: {payslip.payment_date or 'Pending'}
Payment Reference: {payslip.payment_reference or 'Pending'}
"""
    
    response.write(content)
    return response
