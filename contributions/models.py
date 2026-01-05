"""
Contributions Models - Financial contributions management
Handles general and individual contributions with allocation splits
"""

import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from core.models import TimeStampedModel


class ContributionType(TimeStampedModel):
    """Defines types of contributions with allocation rules."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    class Category(models.TextChoices):
        TITHE = 'tithe', 'Tithe'
        OFFERING = 'offering', 'Offering'
        DONATION = 'donation', 'Donation'
        PLEDGE = 'pledge', 'Pledge'
        THANKSGIVING = 'thanksgiving', 'Thanksgiving'
        FUNERAL = 'funeral', 'Funeral Contribution'
        WELFARE = 'welfare', 'Welfare'
        PROJECT = 'project', 'Special Project'
        CHARITY = 'charity', 'Charity'
        OTHER = 'other', 'Other'
    
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OFFERING)
    
    # Scope - who can see/use this type
    class Scope(models.TextChoices):
        MISSION = 'mission', 'Mission (National)'
        AREA = 'area', 'Area'
        DISTRICT = 'district', 'District'
        BRANCH = 'branch', 'Branch'
    
    scope = models.CharField(max_length=20, choices=Scope.choices, default=Scope.MISSION, 
                           help_text='Defines the hierarchical level this contribution type belongs to')
    
    # For branch/district/area specific types
    branch = models.ForeignKey(
        'core.Branch', on_delete=models.CASCADE, null=True, blank=True, related_name='contribution_types'
    )
    district = models.ForeignKey(
        'core.District', on_delete=models.CASCADE, null=True, blank=True, related_name='contribution_types'
    )
    area = models.ForeignKey(
        'core.Area', on_delete=models.CASCADE, null=True, blank=True, related_name='contribution_types'
    )
    
    # Type flags
    is_individual = models.BooleanField(default=False, help_text='Track per member')
    is_general = models.BooleanField(default=True, help_text='General collection')
    
    # Allocation percentages (must sum to 100)
    mission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    area_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    district_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    branch_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    
    # Frequency
    class Frequency(models.TextChoices):
        ONE_TIME = 'one_time', 'One Time'
        DAILY = 'daily', 'Daily'
        WEEKLY = 'weekly', 'Weekly'
        MONTHLY = 'monthly', 'Monthly'
        YEARLY = 'yearly', 'Yearly'
    
    frequency = models.CharField(max_length=20, choices=Frequency.choices, default=Frequency.WEEKLY)
    
    # Closeable types (for pledges, projects)
    is_closeable = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='closed_contribution_types'
    )
    close_reason = models.TextField(blank=True)
    
    # Target amount (for projects/pledges)
    target_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Contribution Type'
        verbose_name_plural = 'Contribution Types'
    
    def __str__(self):
        status = ' [CLOSED]' if self.is_closed else ''
        return f"{self.name}{status}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Validate allocation percentages
        total = self.mission_percentage + self.area_percentage + self.district_percentage + self.branch_percentage
        if total != 100:
            raise ValidationError('Allocation percentages must sum to 100%')
        
        # Validate scope-specific fields
        if self.scope == self.Scope.BRANCH and not self.branch:
            raise ValidationError('Branch-scoped contribution types must have a branch assigned')
        elif self.scope == self.Scope.DISTRICT and not self.district:
            raise ValidationError('District-scoped contribution types must have a district assigned')
        elif self.scope == self.Scope.AREA and not self.area:
            raise ValidationError('Area-scoped contribution types must have an area assigned')
            
        # Ensure proper hierarchy alignment
        if self.branch and self.scope != self.Scope.BRANCH:
            raise ValidationError('Branch can only be set for branch-scoped contribution types')
        if self.district and self.scope != self.Scope.DISTRICT:
            raise ValidationError('District can only be set for district-scoped contribution types')
        if self.area and self.scope != self.Scope.AREA:
            raise ValidationError('Area can only be set for area-scoped contribution types')
    
    def calculate_allocations(self, amount):
        """Calculate allocation amounts from total contribution."""
        # Ensure amount is a Decimal
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))

        # Convert percentage to Decimal if it's a string
        mission_pct = Decimal(str(self.mission_percentage)) / Decimal('100')
        area_pct = Decimal(str(self.area_percentage)) / Decimal('100')
        district_pct = Decimal(str(self.district_percentage)) / Decimal('100')
        branch_pct = Decimal(str(self.branch_percentage)) / Decimal('100')

        return {
            'mission': amount * mission_pct,
            'area': amount * area_pct,
            'district': amount * district_pct,
            'branch': amount * branch_pct,
        }


class Contribution(TimeStampedModel):
    """Individual contribution entry."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    contribution_type = models.ForeignKey(ContributionType, on_delete=models.PROTECT, related_name='contributions')
    branch = models.ForeignKey('core.Branch', on_delete=models.PROTECT, related_name='contributions')
    fiscal_year = models.ForeignKey('core.FiscalYear', on_delete=models.PROTECT, related_name='contributions', null=True, blank=True)
    
    # For individual contributions
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='contributions'
    )
    
    # Contribution details
    date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    description = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True)
    receipt = models.FileField(upload_to='contribution_receipts/', blank=True, null=True)
    
    # Calculated allocations
    mission_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    area_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    district_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    branch_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    # Status
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'  # Editable within 24 hours, no ledger entries
        PENDING = 'pending', 'Pending'
        VERIFIED = 'verified', 'Verified'  # Final, ledger entries created
        REJECTED = 'rejected', 'Rejected'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.VERIFIED)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_contributions'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Draft mode fields - 24-hour edit window
    is_draft = models.BooleanField(default=False, help_text='Draft contributions can be edited within 24 hours')
    draft_expires_at = models.DateTimeField(null=True, blank=True, help_text='When draft auto-submits')
    submitted_at = models.DateTimeField(null=True, blank=True, help_text='When draft was finalized')
    
    # Late entry tracking
    is_late_entry = models.BooleanField(default=False)
    late_entry_reason = models.TextField(blank=True)
    
    # Funeral specific
    deceased = models.ForeignKey(
        'members.DeceasedMember', on_delete=models.SET_NULL, null=True, blank=True, related_name='contributions'
    )
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Contribution'
        verbose_name_plural = 'Contributions'
    
    def __str__(self):
        member_info = f" - {self.member.get_full_name()}" if self.member else ""
        return f"{self.contribution_type.name}{member_info} - {self.amount}"
    
    def save(self, *args, **kwargs):
        # Calculate allocations before saving
        if self.contribution_type:
            allocations = self.contribution_type.calculate_allocations(self.amount)
            self.mission_amount = allocations['mission']
            self.area_amount = allocations['area']
            self.district_amount = allocations['district']
            self.branch_amount = allocations['branch']
        super().save(*args, **kwargs)
    
    @property
    def is_editable(self):
        """Check if contribution can be edited (only drafts within 24-hour window)."""
        from django.utils import timezone
        if self.status != self.Status.DRAFT:
            return False
        if self.draft_expires_at and timezone.now() > self.draft_expires_at:
            return False
        return True
    
    @property
    def time_remaining(self):
        """Get time remaining for draft edit window."""
        from django.utils import timezone
        if not self.draft_expires_at:
            return None
        remaining = self.draft_expires_at - timezone.now()
        if remaining.total_seconds() <= 0:
            return None
        return remaining
    
    def finalize_draft(self, user=None):
        """
        Finalize a draft contribution - makes it immutable and creates ledger entries.
        Called when user submits or when 24-hour window expires.
        """
        from django.utils import timezone
        if self.status != self.Status.DRAFT:
            return False
        
        self.status = self.Status.VERIFIED
        self.is_draft = False
        self.submitted_at = timezone.now()
        if user:
            self.verified_by = user
            self.verified_at = timezone.now()
        self.save()
        
        # Ledger entries will be created by signal handler
        return True


class MissionDonation(TimeStampedModel):
    """
    Direct donations from members to Mission.
    These are NOT part of branch weekly contributions and do NOT affect branch PAYABLES.
    Recorded as Mission CASH directly.
    
    Visibility Rules:
    - Donor (Member): Sees only their own donations
    - Mission Admin / National Finance: See all donations
    - Branch/Area/District admins: NO visibility (donor privacy)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='mission_donations'
    )
    
    # Donation details
    date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
    class DonationType(models.TextChoices):
        GENERAL = 'general', 'General Donation'
        PROJECT = 'project', 'Special Project'
        BUILDING = 'building', 'Building Fund'
        MISSIONS = 'missions', 'Missions & Outreach'
        EDUCATION = 'education', 'Education Fund'
        WELFARE = 'welfare', 'Welfare Fund'
        OTHER = 'other', 'Other'
    
    donation_type = models.CharField(max_length=20, choices=DonationType.choices, default=DonationType.GENERAL)
    description = models.TextField(blank=True)
    
    # Payment details
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    receipt = models.FileField(upload_to='mission_donation_receipts/', blank=True, null=True)
    
    # Status
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Verification'
        VERIFIED = 'verified', 'Verified'
        REJECTED = 'rejected', 'Rejected'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_mission_donations'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Privacy - donor can choose to be anonymous in reports
    is_anonymous = models.BooleanField(default=False, help_text='Hide donor name in public reports')
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Mission Donation'
        verbose_name_plural = 'Mission Donations'
    
    def __str__(self):
        donor_name = 'Anonymous' if self.is_anonymous else self.donor.get_full_name()
        return f"{donor_name} - {self.amount} ({self.date})"


class WeeklyContributionSummary(TimeStampedModel):
    """Weekly summary of general contributions for a branch."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    branch = models.ForeignKey('core.Branch', on_delete=models.PROTECT, related_name='weekly_summaries')
    fiscal_year = models.ForeignKey('core.FiscalYear', on_delete=models.PROTECT, related_name='weekly_summaries', null=True, blank=True)
    
    week_start = models.DateField()
    week_end = models.DateField()
    week_number = models.IntegerField()
    year = models.IntegerField()
    
    # Totals
    total_tithe = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_offering = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_other = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    # Status
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_weekly_summaries'
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-year', '-week_number']
        unique_together = ['branch', 'year', 'week_number']
        verbose_name = 'Weekly Contribution Summary'
        verbose_name_plural = 'Weekly Contribution Summaries'
    
    def __str__(self):
        return f"{self.branch.name} - Week {self.week_number}/{self.year}"


class Remittance(TimeStampedModel):
    """Track remittances from branches to mission."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    branch = models.ForeignKey('core.Branch', on_delete=models.PROTECT, related_name='remittances')
    fiscal_year = models.ForeignKey('core.FiscalYear', on_delete=models.PROTECT, related_name='remittances', null=True, blank=True)
    
    month = models.IntegerField()
    year = models.IntegerField()
    
    # Amounts
    amount_due = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount_sent = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    # Payment details
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=100, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    payment_proof = models.FileField(upload_to='remittance_proofs/', blank=True, null=True)
    
    # Status
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENT = 'sent', 'Sent'
        VERIFIED = 'verified', 'Verified (Paid)'
        OVERDUE = 'overdue', 'Overdue'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Verification
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_remittances'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['branch', 'month', 'year']
        verbose_name = 'Remittance'
        verbose_name_plural = 'Remittances'
    
    def __str__(self):
        return f"{self.branch.name} - {self.month}/{self.year} - {self.get_status_display()}"
    
    @property
    def outstanding_amount(self):
        return max(0, self.amount_due - self.amount_sent)


class MissionReturnsPeriod(TimeStampedModel):
    """Monthly period for mission returns tracking."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    month = models.IntegerField()
    year = models.IntegerField()
    
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    
    opened_at = models.DateTimeField(auto_now_add=True)
    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='opened_return_periods'
    )
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='closed_return_periods'
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['month', 'year']
        verbose_name = 'Mission Returns Period'
        verbose_name_plural = 'Mission Returns Periods'
    
    def __str__(self):
        import calendar
        return f"{calendar.month_name[self.month]} {self.year}"


class TitheCommission(TimeStampedModel):
    """Commission payments for pastors based on tithe target achievement."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='commissions'
    )
    branch = models.ForeignKey('core.Branch', on_delete=models.PROTECT, related_name='commissions')
    fiscal_year = models.ForeignKey('core.FiscalYear', on_delete=models.PROTECT, related_name='commissions', null=True, blank=True)
    
    month = models.IntegerField()
    year = models.IntegerField()
    
    # Target & Achievement
    target_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tithe_collected = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    percentage_achieved = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_qualified = models.BooleanField(default=False)
    
    # Commission
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Payment
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        PAID = 'paid', 'Paid'
        DECLINED = 'declined', 'Declined'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_commissions'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['recipient', 'branch', 'month', 'year']
        verbose_name = 'Tithe Commission'
        verbose_name_plural = 'Tithe Commissions'
    
    def __str__(self):
        return f"{self.recipient.get_full_name()} - {self.month}/{self.year} - {self.commission_amount}"
    
    def calculate_commission(self):
        """Calculate commission based on tithe collected and target."""
        if self.tithe_collected >= self.target_amount:
            self.is_qualified = True
            self.percentage_achieved = Decimal('100.00')
            self.commission_amount = self.tithe_collected * (self.commission_percentage / 100)
        else:
            self.is_qualified = False
            self.percentage_achieved = (self.tithe_collected / self.target_amount * 100) if self.target_amount > 0 else 0
            self.commission_amount = Decimal('0.00')
