"""
Monthly Reports Models - Branch monthly financial and attendance reports
"""

import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from core.models import TimeStampedModel, FiscalYear


class MonthlyReport(TimeStampedModel):
    """Monthly report for each branch including contributions, attendance, and expenditures."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Branch and Period
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='monthly_reports')
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.PROTECT, related_name='monthly_reports')
    month = models.IntegerField()
    year = models.IntegerField()
    
    # Attendance Summary
    total_services = models.IntegerField(default=0, help_text="Number of services held in the month")
    average_attendance = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Average attendance per service")
    total_attendance = models.IntegerField(default=0, help_text="Total attendance for all services")
    visitors_count = models.IntegerField(default=0, help_text="Number of visitors")
    new_members = models.IntegerField(default=0, help_text="New members added")
    
    # Financial Summary - Contributions
    total_contributions = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total contributions for the month"
    )
    tithe_amount = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total tithe collected"
    )
    offering_amount = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total offering collected"
    )
    special_contributions = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Special contributions (building, projects, etc.)"
    )
    
    # Financial Summary - Expenditures
    total_expenditure = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total expenditure for the month"
    )
    utility_expenses = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Utility bills (electricity, water, etc.)"
    )
    maintenance_expenses = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Building maintenance and repairs"
    )
    other_expenses = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Other operational expenses"
    )
    
    # Mission Remittance
    mission_remittance_due = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Amount due to mission (tithe portion)"
    )
    mission_remittance_paid = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Amount paid to mission"
    )
    mission_remittance_balance = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Balance remaining to be paid"
    )
    
    # Branch Balance
    branch_balance = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Remaining funds in branch account"
    )
    
    # Status
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SUBMITTED = 'submitted', 'Submitted for Review'
        APPROVED = 'approved', 'Approved by Mission'
        PAID = 'paid', 'Mission Remittance Paid'
        ARCHIVED = 'archived', 'Archived'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    # Approval Workflow
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_reports'
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_reports'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Payment Details
    payment_date = models.DateField(null=True, blank=True, help_text="Date mission remittance was paid")
    payment_reference = models.CharField(max_length=100, blank=True, help_text="Payment reference number")
    payment_method = models.CharField(max_length=50, blank=True, help_text="Payment method (bank, mobile money, etc.)")
    
    # Notes and Attachments
    notes = models.TextField(blank=True, help_text="Additional notes or comments")
    attachment = models.FileField(
        upload_to='monthly_reports/',
        blank=True,
        null=True,
        help_text="Supporting documents (PDF, Excel, etc.)"
    )
    
    class Meta:
        unique_together = ['branch', 'month', 'year']
        ordering = ['-year', '-month', 'branch__name']
        verbose_name = 'Monthly Report'
        verbose_name_plural = 'Monthly Reports'
    
    def __str__(self):
        return f"{self.branch.name} - {self.month}/{self.year}"
    
    def save(self, *args, **kwargs):
        from django.utils import timezone
        
        # Calculate mission remittance (typically 10% of tithe)
        if self.mission_remittance_due == 0 and self.tithe_amount > 0:
            self.mission_remittance_due = self.tithe_amount * Decimal('0.10')
        
        # Calculate balance
        self.branch_balance = (
            self.total_contributions - 
            self.total_expenditure - 
            self.mission_remittance_paid
        )
        
        # Calculate remaining remittance balance
        self.mission_remittance_balance = (
            self.mission_remittance_due - self.mission_remittance_paid
        )
        
        super().save(*args, **kwargs)
    
    @property
    def month_name(self):
        """Get month name."""
        import calendar
        return calendar.month_name[self.month]
    
    @property
    def is_overdue(self):
        """Check if payment is overdue."""
        if self.status in [self.Status.PAID, self.Status.ARCHIVED]:
            return False
        from django.utils import timezone
        today = timezone.now().date()
        # Payment is due by 10th of next month
        if self.month == 12:
            due_date = today.replace(year=self.year + 1, month=1, day=10)
        else:
            due_date = today.replace(year=self.year, month=self.month + 1, day=10)
        return today > due_date and self.mission_remittance_balance > 0
    
    def mark_submitted(self, user):
        """Mark report as submitted."""
        from django.utils import timezone
        self.status = self.Status.SUBMITTED
        self.submitted_by = user
        self.submitted_at = timezone.now()
        self.save()
    
    def mark_approved(self, user):
        """Mark report as approved."""
        from django.utils import timezone
        self.status = self.Status.APPROVED
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()
    
    def mark_paid(self, payment_date=None, reference=None, method=None):
        """Mark report as paid."""
        from django.utils import timezone
        self.status = self.Status.PAID
        self.payment_date = payment_date or timezone.now().date()
        self.payment_reference = reference or ''
        self.payment_method = method or ''
        self.mission_remittance_paid = self.mission_remittance_due
        self.mission_remittance_balance = Decimal('0.00')
        self.save()


class MonthlyReportItem(models.Model):
    """Detailed breakdown items for monthly reports."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(MonthlyReport, on_delete=models.CASCADE, related_name='detail_items')
    
    class Category(models.TextChoices):
        CONTRIBUTION = 'contribution', 'Contribution'
        EXPENDITURE = 'expenditure', 'Expenditure'
    
    category = models.CharField(max_length=20, choices=Category.choices)
    item_type = models.CharField(max_length=100, help_text="e.g., Tithe, Offering, Electricity, Water")
    description = models.CharField(max_length=200, help_text="Description of the item")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    quantity = models.IntegerField(default=1, help_text="Number of occurrences (e.g., weeks, units)")
    
    class Meta:
        ordering = ['category', 'item_type']
        verbose_name = 'Report Item'
        verbose_name_plural = 'Report Items'
    
    def __str__(self):
        return f"{self.report} - {self.item_type}"
