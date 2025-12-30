"""
Expenditure Models - Branch and Mission level expense management
"""

import uuid
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class ExpenditureCategory(models.Model):
    """Categories for organizing expenditures."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    class CategoryType(models.TextChoices):
        OPERATIONS = 'operations', 'Operations / Projects'
        WELFARE = 'welfare', 'Welfare / Social Support'
        UTILITIES = 'utilities', 'Utilities'
        PAYROLL = 'payroll', 'Payroll'
        MAINTENANCE = 'maintenance', 'Maintenance'
        EVENTS = 'events', 'Events'
        EQUIPMENT = 'equipment', 'Equipment'
        OTHER = 'other', 'Other'
    
    category_type = models.CharField(max_length=20, choices=CategoryType.choices, default=CategoryType.OPERATIONS)
    
    # Scope
    class Scope(models.TextChoices):
        BRANCH = 'branch', 'Branch Level'
        MISSION = 'mission', 'Mission Level'
        ALL = 'all', 'All Levels'
    
    scope = models.CharField(max_length=20, choices=Scope.choices, default=Scope.ALL)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Expenditure Category'
        verbose_name_plural = 'Expenditure Categories'
    
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class Expenditure(TimeStampedModel):
    """Track all expenditures at branch and mission levels."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    category = models.ForeignKey(ExpenditureCategory, on_delete=models.PROTECT, related_name='expenditures')
    fiscal_year = models.ForeignKey('core.FiscalYear', on_delete=models.PROTECT, related_name='expenditures')
    
    # Level - Branch or Mission
    class Level(models.TextChoices):
        BRANCH = 'branch', 'Branch'
        DISTRICT = 'district', 'District'
        AREA = 'area', 'Area'
        MISSION = 'mission', 'Mission'
    
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BRANCH)
    
    # Hierarchy references
    branch = models.ForeignKey(
        'core.Branch', on_delete=models.PROTECT, null=True, blank=True, related_name='expenditures'
    )
    district = models.ForeignKey(
        'core.District', on_delete=models.PROTECT, null=True, blank=True, related_name='expenditures'
    )
    area = models.ForeignKey(
        'core.Area', on_delete=models.PROTECT, null=True, blank=True, related_name='expenditures'
    )
    
    # Expenditure details
    date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Vendor / Recipient info
    vendor = models.CharField(max_length=200, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True, help_text='Payment ID or transaction reference')
    
    # Receipt / Documentation
    receipt = models.FileField(upload_to='expenditure_receipts/', blank=True, null=True)
    receipt_number = models.CharField(max_length=100, blank=True)
    
    # Status
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Approval'
        APPROVED = 'approved', 'Approved'
        PAID = 'paid', 'Paid'
        REJECTED = 'rejected', 'Rejected'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPROVED)
    
    # Approval workflow
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_expenditures'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Late entry tracking
    is_late_entry = models.BooleanField(default=False)
    late_entry_reason = models.TextField(blank=True)
    
    # Include in reports
    include_in_reports = models.BooleanField(default=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Expenditure'
        verbose_name_plural = 'Expenditures'
    
    def __str__(self):
        return f"{self.title} - {self.amount} ({self.date})"
    
    @property
    def location_name(self):
        if self.branch:
            return self.branch.name
        elif self.district:
            return self.district.name
        elif self.area:
            return self.area.name
        return "Mission"


class UtilityBill(TimeStampedModel):
    """Track recurring utility bills for branches."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    branch = models.ForeignKey('core.Branch', on_delete=models.PROTECT, related_name='utility_bills')
    fiscal_year = models.ForeignKey('core.FiscalYear', on_delete=models.PROTECT, related_name='utility_bills')
    
    class UtilityType(models.TextChoices):
        ELECTRICITY = 'electricity', 'Electricity'
        WATER = 'water', 'Water'
        INTERNET = 'internet', 'Internet'
        GAS = 'gas', 'Gas'
        RENT = 'rent', 'Rent'
        FUEL = 'fuel', 'Generator Fuel'
        PHONE = 'phone', 'Phone/Airtime'
        OTHER = 'other', 'Other'
    
    utility_type = models.CharField(max_length=20, choices=UtilityType.choices)
    
    # Bill details
    month = models.IntegerField()
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Provider info
    provider = models.CharField(max_length=200, blank=True)
    account_number = models.CharField(max_length=100, blank=True)
    meter_number = models.CharField(max_length=100, blank=True)
    
    # Payment
    payment_date = models.DateField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    receipt = models.FileField(upload_to='utility_receipts/', blank=True, null=True)
    
    is_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['branch', 'utility_type', 'month', 'year']
        verbose_name = 'Utility Bill'
        verbose_name_plural = 'Utility Bills'
    
    def __str__(self):
        return f"{self.branch.name} - {self.get_utility_type_display()} - {self.month}/{self.year}"


class WelfarePayment(TimeStampedModel):
    """Track welfare/social support payments to members."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    branch = models.ForeignKey('core.Branch', on_delete=models.PROTECT, related_name='welfare_payments')
    fiscal_year = models.ForeignKey('core.FiscalYear', on_delete=models.PROTECT, related_name='welfare_payments')
    
    # Recipient
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='welfare_received'
    )
    recipient_name = models.CharField(max_length=200)  # For non-members
    
    class WelfareType(models.TextChoices):
        SCHOOL_FEES = 'school_fees', 'School Fees Support'
        MEDICAL = 'medical', 'Medical/Hospital Support'
        TRAVEL = 'travel', 'Travel Support'
        EMERGENCY = 'emergency', 'Emergency Assistance'
        BEREAVEMENT = 'bereavement', 'Bereavement Support'
        RENT = 'rent', 'Rent Assistance'
        FOOD = 'food', 'Food Support'
        OTHER = 'other', 'Other'
    
    welfare_type = models.CharField(max_length=20, choices=WelfareType.choices)
    
    # Payment details
    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    
    # Approval
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_welfare'
    )
    
    receipt = models.FileField(upload_to='welfare_receipts/', blank=True, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Welfare Payment'
        verbose_name_plural = 'Welfare Payments'
    
    def __str__(self):
        return f"{self.recipient_name} - {self.get_welfare_type_display()} - {self.amount}"


class Asset(TimeStampedModel):
    """Track church assets and inventory."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class AssetLevel(models.TextChoices):
        BRANCH = 'branch', 'Branch'
        MISSION = 'mission', 'Mission'
    
    level = models.CharField(max_length=20, choices=AssetLevel.choices, default=AssetLevel.BRANCH)
    branch = models.ForeignKey(
        'core.Branch', on_delete=models.PROTECT, null=True, blank=True, related_name='assets'
    )
    
    # Asset details
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    class AssetCategory(models.TextChoices):
        FURNITURE = 'furniture', 'Furniture'
        ELECTRONICS = 'electronics', 'Electronics'
        INSTRUMENTS = 'instruments', 'Musical Instruments'
        VEHICLE = 'vehicle', 'Vehicle'
        BUILDING = 'building', 'Building/Property'
        EQUIPMENT = 'equipment', 'Equipment'
        OTHER = 'other', 'Other'
    
    category = models.CharField(max_length=20, choices=AssetCategory.choices)
    
    # Purchase info
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    vendor = models.CharField(max_length=200, blank=True)
    
    # Current status
    quantity = models.IntegerField(default=1)
    current_value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active / In Use'
        DAMAGED = 'damaged', 'Damaged'
        DISPOSED = 'disposed', 'Disposed'
        LOST = 'lost', 'Lost'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    # Linked to expenditure
    related_expenditure = models.ForeignKey(
        Expenditure, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets'
    )
    
    serial_number = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Asset'
        verbose_name_plural = 'Assets'
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
