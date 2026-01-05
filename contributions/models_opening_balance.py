"""
Opening Balance Models - For tracking pre-system funds
"""

import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from core.models import TimeStampedModel


class OpeningBalance(TimeStampedModel):
    """
    One-time opening balance for Branch and Mission CASH only.
    These represent pre-system funds that exist before system adoption.
    
    Opening balances:
    - Are CASH only (no PAYABLE/RECEIVABLE)
    - Are one-time per contribution type
    - Require Mission Admin approval
    - Are clearly labeled as pre-system funds
    - Are included in balance visibility
    - Are excluded from income, tithe, and commission calculations
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Level - Branch or Mission only
    class Level(models.TextChoices):
        BRANCH = 'branch', 'Branch'
        MISSION = 'mission', 'Mission'
    
    level = models.CharField(max_length=20, choices=Level.choices)
    
    # Branch reference (null for Mission level)
    branch = models.ForeignKey(
        'core.Branch', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='opening_balances'
    )
    
    # Financial details
    amount = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    contribution_type = models.ForeignKey(
        'contributions.ContributionType', 
        on_delete=models.PROTECT, 
        related_name='opening_balances'
    )
    date = models.DateField(help_text='Date the opening balance was recorded')
    description = models.TextField(
        default='Opening Balance – Pre-System Funds',
        help_text='Description of the opening balance'
    )
    
    # Approval workflow
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Approval'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_opening_balances'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Supporting documentation
    documentation = models.FileField(
        upload_to='opening_balance_docs/',
        blank=True,
        null=True,
        help_text='Supporting documentation for the opening balance'
    )
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Opening Balance'
        verbose_name_plural = 'Opening Balances'
        # Ensure only one opening balance per contribution type per branch/mission
        unique_together = [
            ('branch', 'contribution_type'),  # For branch level
        ]
        constraints = [
            # For mission level (where branch is null)
            models.UniqueConstraint(
                fields=['contribution_type'],
                condition=models.Q(branch__isnull=True),
                name='unique_mission_contribution_type'
            )
        ]
    
    def __str__(self):
        entity = self.branch.name if self.branch else 'Mission'
        return f"{entity} - {self.contribution_type.name} - {self.amount}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate level and branch consistency
        if self.level == self.Level.BRANCH and not self.branch:
            raise ValidationError('Branch must be specified for branch-level opening balances')
        elif self.level == self.Level.MISSION and self.branch:
            raise ValidationError('Branch should not be specified for mission-level opening balances')
    
    def save(self, *args, **kwargs):
        # Set level based on branch
        if self.branch:
            self.level = self.Level.BRANCH
        else:
            self.level = self.Level.MISSION
        
        super().save(*args, **kwargs)
