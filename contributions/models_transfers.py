"""
Financial Transfer Models - For transferring funds between hierarchy levels
"""

import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from core.models import TimeStampedModel


class HierarchyTransfer(TimeStampedModel):
    """
    Tracks transfers of funds between hierarchy levels:
    - Mission → Area
    - Area → District
    - District → Branch
    
    These are NOT contributions or income, but allocations of funds.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Source and destination
    class HierarchyLevel(models.TextChoices):
        MISSION = 'mission', 'Mission'
        AREA = 'area', 'Area'
        DISTRICT = 'district', 'District'
        BRANCH = 'branch', 'Branch'
    
    source_level = models.CharField(max_length=20, choices=HierarchyLevel.choices)
    destination_level = models.CharField(max_length=20, choices=HierarchyLevel.choices)
    
    # Entity references
    source_area = models.ForeignKey(
        'core.Area', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='transfers_sent'
    )
    source_district = models.ForeignKey(
        'core.District', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='transfers_sent'
    )
    source_branch = models.ForeignKey(
        'core.Branch', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='transfers_sent'
    )
    
    destination_area = models.ForeignKey(
        'core.Area', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='transfers_received'
    )
    destination_district = models.ForeignKey(
        'core.District', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='transfers_received'
    )
    destination_branch = models.ForeignKey(
        'core.Branch', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='transfers_received'
    )
    
    # Transfer details
    amount = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    date = models.DateField()
    reference = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    
    # Purpose categorization
    class Purpose(models.TextChoices):
        ALLOCATION = 'allocation', 'Regular Fund Allocation'
        SPECIAL_PROJECT = 'special_project', 'Special Project Funding'
        EMERGENCY = 'emergency', 'Emergency Support'
        OPERATIONS = 'operations', 'Operational Support'
        OTHER = 'other', 'Other'
    
    purpose = models.CharField(max_length=20, choices=Purpose.choices, default=Purpose.ALLOCATION)
    
    # Status
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Approval workflow
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_transfers'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Documentation
    documentation = models.FileField(
        upload_to='hierarchy_transfers/',
        blank=True,
        null=True,
        help_text='Supporting documentation for the transfer'
    )
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Hierarchy Transfer'
        verbose_name_plural = 'Hierarchy Transfers'
    
    def __str__(self):
        source = self._get_entity_name(self.source_level, self.source_area, self.source_district, self.source_branch)
        destination = self._get_entity_name(self.destination_level, self.destination_area, self.destination_district, self.destination_branch)
        return f"{source} → {destination}: {self.amount}"
    
    def _get_entity_name(self, level, area, district, branch):
        """Helper method to get entity name based on level"""
        if level == self.HierarchyLevel.MISSION:
            return "Mission"
        elif level == self.HierarchyLevel.AREA and area:
            return f"Area: {area.name}"
        elif level == self.HierarchyLevel.DISTRICT and district:
            return f"District: {district.name}"
        elif level == self.HierarchyLevel.BRANCH and branch:
            return f"Branch: {branch.name}"
        return level.capitalize()
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate source level and entity consistency
        if self.source_level == self.HierarchyLevel.MISSION:
            if self.source_area or self.source_district or self.source_branch:
                raise ValidationError('No entity should be specified for Mission source')
        elif self.source_level == self.HierarchyLevel.AREA:
            if not self.source_area:
                raise ValidationError('Area must be specified for Area source')
        elif self.source_level == self.HierarchyLevel.DISTRICT:
            if not self.source_district:
                raise ValidationError('District must be specified for District source')
        elif self.source_level == self.HierarchyLevel.BRANCH:
            if not self.source_branch:
                raise ValidationError('Branch must be specified for Branch source')
        
        # Validate destination level and entity consistency
        if self.destination_level == self.HierarchyLevel.MISSION:
            if self.destination_area or self.destination_district or self.destination_branch:
                raise ValidationError('No entity should be specified for Mission destination')
        elif self.destination_level == self.HierarchyLevel.AREA:
            if not self.destination_area:
                raise ValidationError('Area must be specified for Area destination')
        elif self.destination_level == self.HierarchyLevel.DISTRICT:
            if not self.destination_district:
                raise ValidationError('District must be specified for District destination')
        elif self.destination_level == self.HierarchyLevel.BRANCH:
            if not self.destination_branch:
                raise ValidationError('Branch must be specified for Branch destination')
        
        # Validate hierarchy flow (can only go up or down one level)
        valid_flows = [
            (self.HierarchyLevel.MISSION, self.HierarchyLevel.AREA),
            (self.HierarchyLevel.AREA, self.HierarchyLevel.DISTRICT),
            (self.HierarchyLevel.DISTRICT, self.HierarchyLevel.BRANCH),
            (self.HierarchyLevel.AREA, self.HierarchyLevel.MISSION),
            (self.HierarchyLevel.DISTRICT, self.HierarchyLevel.AREA),
            (self.HierarchyLevel.BRANCH, self.HierarchyLevel.DISTRICT)
        ]
        
        if (self.source_level, self.destination_level) not in valid_flows:
            raise ValidationError('Invalid hierarchy flow. Transfers can only occur between adjacent levels.')
        
        # Prevent transfers to self
        if self.source_level == self.destination_level:
            if (self.source_area and self.destination_area and self.source_area == self.destination_area) or \
               (self.source_district and self.destination_district and self.source_district == self.destination_district) or \
               (self.source_branch and self.destination_branch and self.source_branch == self.destination_branch):
                raise ValidationError('Cannot transfer funds to the same entity')
