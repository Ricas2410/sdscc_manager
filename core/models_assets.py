"""
Assets & Inventory Models - Church asset management
"""

import uuid
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class ChurchAsset(TimeStampedModel):
    """Church assets and inventory items."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic Information
    name = models.CharField(max_length=200)
    asset_id = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    
    class Category(models.TextChoices):
        FURNITURE = 'furniture', 'Furniture'
        ELECTRONICS = 'electronics', 'Electronics'
        VEHICLES = 'vehicles', 'Vehicles'
        EQUIPMENT = 'equipment', 'Equipment'
        BUILDING = 'building', 'Building'
        OTHER = 'other', 'Other'
    
    category = models.CharField(max_length=20, choices=Category.choices)
    
    # Location
    branch = models.ForeignKey(
        'core.Branch',
        on_delete=models.CASCADE,
        related_name='church_assets'
    )
    location_detail = models.CharField(max_length=200, blank=True, help_text="Specific location within branch")
    
    # Financial
    value = models.DecimalField(max_digits=12, decimal_places=2, help_text="Current value in GHS")
    purchase_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Original purchase price")
    purchase_date = models.DateField()
    
    class Status(models.TextChoices):
        EXCELLENT = 'excellent', 'Excellent'
        GOOD = 'good', 'Good'
        FAIR = 'fair', 'Fair'
        POOR = 'poor', 'Poor'
        DAMAGED = 'damaged', 'Damaged'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.GOOD)
    
    # Additional Details
    serial_number = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    
    # Media
    image = models.ImageField(upload_to='assets/', blank=True, null=True)
    
    # Maintenance
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    maintenance_notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Church Asset'
        verbose_name_plural = 'Church Assets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['branch', 'status']),
            models.Index(fields=['category']),
            models.Index(fields=['asset_id']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.asset_id})"
    
    @property
    def depreciation_percentage(self):
        """Calculate depreciation percentage."""
        if self.purchase_value and self.purchase_value > 0:
            return ((self.purchase_value - self.value) / self.purchase_value) * 100
        return 0
    
    @property
    def age_years(self):
        """Calculate asset age in years."""
        from django.utils import timezone
        today = timezone.now().date()
        return (today - self.purchase_date).days / 365.25
    
    @property
    def is_maintenance_due(self):
        """Check if maintenance is due."""
        if self.next_maintenance_date:
            from django.utils import timezone
            return timezone.now().date() >= self.next_maintenance_date
        return False


class ChurchAssetMaintenance(TimeStampedModel):
    """Asset maintenance records."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(ChurchAsset, on_delete=models.CASCADE, related_name='maintenance_records')
    
    class MaintenanceType(models.TextChoices):
        ROUTINE = 'routine', 'Routine Maintenance'
        REPAIR = 'repair', 'Repair'
        INSPECTION = 'inspection', 'Inspection'
        UPGRADE = 'upgrade', 'Upgrade'
        CLEANING = 'cleaning', 'Cleaning'
    
    maintenance_type = models.CharField(max_length=20, choices=MaintenanceType.choices)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Maintenance cost in GHS")
    
    performed_by = models.CharField(max_length=200, help_text="Who performed the maintenance")
    performed_date = models.DateField()
    
    next_maintenance_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Asset Maintenance'
        verbose_name_plural = 'Asset Maintenance Records'
        ordering = ['-performed_date']
    
    def __str__(self):
        return f"{self.asset.name} - {self.get_maintenance_type_display()} on {self.performed_date}"


class ChurchAssetTransfer(TimeStampedModel):
    """Asset transfer records between branches."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(ChurchAsset, on_delete=models.CASCADE, related_name='transfer_records')
    
    from_branch = models.ForeignKey(
        'core.Branch',
        on_delete=models.CASCADE,
        related_name='assets_transferred_from'
    )
    to_branch = models.ForeignKey(
        'core.Branch',
        on_delete=models.CASCADE,
        related_name='assets_transferred_to'
    )
    
    transfer_date = models.DateField()
    reason = models.TextField()
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='approved_asset_transfers'
    )
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    class Meta:
        verbose_name = 'Asset Transfer'
        verbose_name_plural = 'Asset Transfers'
        ordering = ['-transfer_date']
    
    def __str__(self):
        return f"{self.asset.name}: {self.from_branch.name} → {self.to_branch.name}"
