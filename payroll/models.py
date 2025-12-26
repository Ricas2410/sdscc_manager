"""
Payroll Models - Mission staff payroll management
"""

import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class StaffPayrollProfile(TimeStampedModel):
    """Payroll profile for mission staff."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payroll_profile'
    )
    
    # Employment Details
    employee_id = models.CharField(max_length=20, unique=True)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True)
    
    class EmploymentType(models.TextChoices):
        FULL_TIME = 'full_time', 'Full Time'
        PART_TIME = 'part_time', 'Part Time'
        CONTRACT = 'contract', 'Contract'
    
    employment_type = models.CharField(max_length=20, choices=EmploymentType.choices, default=EmploymentType.FULL_TIME)
    
    hire_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Salary Details
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class PaymentCycle(models.TextChoices):
        WEEKLY = 'weekly', 'Weekly'
        BI_WEEKLY = 'bi_weekly', 'Bi-Weekly'
        MONTHLY = 'monthly', 'Monthly'
    
    payment_cycle = models.CharField(max_length=20, choices=PaymentCycle.choices, default=PaymentCycle.MONTHLY)
    
    # Bank Details
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)
    
    # Tax info
    tax_id = models.CharField(max_length=50, blank=True)
    
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Staff Payroll Profile'
        verbose_name_plural = 'Staff Payroll Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position}"
    
    @property
    def total_allowances(self):
        """Calculate total active allowances."""
        from django.utils import timezone
        today = timezone.now().date()
        return sum(
            a.amount for a in self.allowances.filter(
                is_recurring=True
            ).filter(
                models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)
            )
        )
    
    @property
    def gross_salary(self):
        """Calculate gross salary (base + allowances)."""
        return self.base_salary + self.total_allowances
    
    @property
    def housing_allowance(self):
        """Get housing allowance amount."""
        allowance = self.allowances.filter(allowance_type__code='HOUSING').first()
        return allowance.amount if allowance else Decimal('0.00')
    
    @property
    def transport_allowance(self):
        """Get transport allowance amount."""
        allowance = self.allowances.filter(allowance_type__code='TRANSPORT').first()
        return allowance.amount if allowance else Decimal('0.00')
    
    @property
    def other_allowances(self):
        """Get other allowances amount."""
        allowance = self.allowances.filter(allowance_type__code='OTHER').first()
        return allowance.amount if allowance else Decimal('0.00')


class AllowanceType(models.Model):
    """Types of allowances."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_taxable = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DeductionType(models.Model):
    """Types of deductions."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class StaffAllowance(TimeStampedModel):
    """Allowances assigned to staff."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    staff = models.ForeignKey(StaffPayrollProfile, on_delete=models.CASCADE, related_name='allowances')
    allowance_type = models.ForeignKey(AllowanceType, on_delete=models.PROTECT, related_name='staff_allowances')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_recurring = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['staff__user__first_name']
    
    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.allowance_type.name}"


class StaffDeduction(TimeStampedModel):
    """Deductions assigned to staff."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    staff = models.ForeignKey(StaffPayrollProfile, on_delete=models.CASCADE, related_name='deductions')
    deduction_type = models.ForeignKey(DeductionType, on_delete=models.PROTECT, related_name='staff_deductions')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_recurring = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['staff__user__first_name']
    
    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.deduction_type.name}"


class PayrollRun(TimeStampedModel):
    """A payroll processing run for a specific period."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    fiscal_year = models.ForeignKey('core.FiscalYear', on_delete=models.PROTECT, related_name='payroll_runs')
    
    month = models.IntegerField()
    year = models.IntegerField()
    
    # Totals
    total_base_salary = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_allowances = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_net_pay = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    # Status
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PROCESSING = 'processing', 'Processing'
        APPROVED = 'approved', 'Approved'
        PAID = 'paid', 'Paid'
        CANCELLED = 'cancelled', 'Cancelled'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_payrolls'
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_payrolls'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['month', 'year']
        verbose_name = 'Payroll Run'
        verbose_name_plural = 'Payroll Runs'
    
    def __str__(self):
        return f"Payroll - {self.month}/{self.year}"
    
    def calculate_totals(self):
        """Calculate totals from all payslips."""
        payslips = self.payslips.all()
        self.total_base_salary = sum(p.base_salary for p in payslips)
        self.total_allowances = sum(p.total_allowances for p in payslips)
        self.total_deductions = sum(p.total_deductions for p in payslips)
        self.total_net_pay = sum(p.net_pay for p in payslips)
        self.save()


class PaySlip(TimeStampedModel):
    """Individual payslip for a staff member."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name='payslips')
    staff = models.ForeignKey(StaffPayrollProfile, on_delete=models.PROTECT, related_name='payslips')
    
    # Amounts
    base_salary = models.DecimalField(max_digits=12, decimal_places=2)
    total_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gross_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Breakdown (JSON fields for detailed breakdown)
    allowances_breakdown = models.JSONField(default=dict, blank=True)
    deductions_breakdown = models.JSONField(default=dict, blank=True)
    
    # Payment
    payment_date = models.DateField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        PAID = 'paid', 'Paid'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-payroll_run__year', '-payroll_run__month']
        unique_together = ['payroll_run', 'staff']
        verbose_name = 'Pay Slip'
        verbose_name_plural = 'Pay Slips'
    
    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.payroll_run}"
    
    @property
    def is_paid(self):
        """Check if payslip is paid."""
        return self.status == self.Status.PAID
    
    def calculate_pay(self):
        """Calculate pay amounts."""
        self.gross_pay = self.base_salary + self.total_allowances
        self.net_pay = self.gross_pay - self.total_deductions


class StaffLoan(TimeStampedModel):
    """Track staff loans and advances."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    staff = models.ForeignKey(StaffPayrollProfile, on_delete=models.CASCADE, related_name='loans')
    
    class LoanType(models.TextChoices):
        SALARY_ADVANCE = 'advance', 'Salary Advance'
        PERSONAL_LOAN = 'personal', 'Personal Loan'
        EMERGENCY = 'emergency', 'Emergency Loan'
    
    loan_type = models.CharField(max_length=20, choices=LoanType.choices)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    loan_date = models.DateField()
    repayment_start_date = models.DateField()
    monthly_deduction = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        PAID = 'paid', 'Fully Paid'
        CANCELLED = 'cancelled', 'Cancelled'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_loans'
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-loan_date']
        verbose_name = 'Staff Loan'
        verbose_name_plural = 'Staff Loans'
    
    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.get_loan_type_display()} - {self.amount}"
    
    @property
    def outstanding_amount(self):
        return max(Decimal('0'), self.amount - self.amount_paid)
