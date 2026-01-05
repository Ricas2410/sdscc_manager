"""
Enhanced Remittance Models - For clear separation of remittance obligations
"""

import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from core.models import TimeStampedModel


class HierarchyRemittance(TimeStampedModel):
    """
    Tracks remittances from branches to Area or District.
    Separate from the existing Branch → Mission remittances.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Source branch
    branch = models.ForeignKey('core.Branch', on_delete=models.PROTECT, related_name='hierarchy_remittances')
    
    # Destination level
    class DestinationLevel(models.TextChoices):
        AREA = 'area', 'Area'
        DISTRICT = 'district', 'District'
    
    destination_level = models.CharField(max_length=20, choices=DestinationLevel.choices)
    
    # Destination entity
    area = models.ForeignKey(
        'core.Area', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='remittances'
    )
    district = models.ForeignKey(
        'core.District', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='remittances'
    )
    
    # Time period
    month = models.IntegerField()
    year = models.IntegerField()
    
    # Amounts
    amount_due = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount_sent = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    # Payment details
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=100, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    payment_proof = models.FileField(upload_to='hierarchy_remittance_proofs/', blank=True, null=True)
    
    # Status
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENT = 'sent', 'Sent'
        VERIFIED = 'verified', 'Verified (Paid)'
        OVERDUE = 'overdue', 'Overdue'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Verification
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_hierarchy_remittances'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-year', '-month']
        unique_together = [
            ('branch', 'destination_level', 'area', 'month', 'year'),
            ('branch', 'destination_level', 'district', 'month', 'year'),
        ]
        verbose_name = 'Hierarchy Remittance'
        verbose_name_plural = 'Hierarchy Remittances'
    
    def __str__(self):
        destination = self.area.name if self.area else self.district.name
        return f"{self.branch.name} → {self.get_destination_level_display()} ({destination}) - {self.month}/{self.year} - {self.get_status_display()}"
    
    @property
    def outstanding_amount(self):
        return max(0, self.amount_due - self.amount_sent)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate destination level and entity consistency
        if self.destination_level == self.DestinationLevel.AREA and not self.area:
            raise ValidationError('Area must be specified for Area remittances')
        elif self.destination_level == self.DestinationLevel.DISTRICT and not self.district:
            raise ValidationError('District must be specified for District remittances')
        
        # Ensure only one entity is specified
        if self.area and self.district:
            raise ValidationError('Cannot specify both Area and District')
        
        # Ensure branch belongs to the specified hierarchy
        if self.destination_level == self.DestinationLevel.AREA and self.area:
            if self.branch.district.area != self.area:
                raise ValidationError('Branch must belong to the specified Area')
        elif self.destination_level == self.DestinationLevel.DISTRICT and self.district:
            if self.branch.district != self.district:
                raise ValidationError('Branch must belong to the specified District')
