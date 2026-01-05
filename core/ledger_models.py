"""
Ledger Models - Single Source of Financial Truth
Implements custody vs ownership accounting for church financial management.

LEDGER-CENTRIC DESIGN:
- Each LedgerEntry represents a financial position
- CASH = physically held funds
- RECEIVABLE = owed but not yet received
- PAYABLE = owed to another level
- All financial reports derive from ledger entries
"""

import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.db.models import Sum, Q
from django.utils import timezone
from core.models import TimeStampedModel


class LedgerEntry(TimeStampedModel):
    """
    Single source of financial truth.
    
    Every financial transaction creates ledger entries that track:
    - WHO owns the money (owner)
    - WHERE the money physically is (custody)
    - WHAT type of entry (CASH, RECEIVABLE, PAYABLE)
    - WHERE it came from (source)
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class EntryType(models.TextChoices):
        CASH = 'cash', 'Cash (Physically Held)'
        RECEIVABLE = 'receivable', 'Receivable (Owed to Owner)'
        PAYABLE = 'payable', 'Payable (Owed by Owner)'
    
    entry_type = models.CharField(max_length=20, choices=EntryType.choices)
    
    class OwnerType(models.TextChoices):
        MISSION = 'mission', 'Mission (National)'
        AREA = 'area', 'Area'
        DISTRICT = 'district', 'District'
        BRANCH = 'branch', 'Branch'
        MEMBER = 'member', 'Member'
    
    owner_type = models.CharField(max_length=20, choices=OwnerType.choices)
    
    # Owner references
    owner_branch = models.ForeignKey(
        'core.Branch', on_delete=models.PROTECT, null=True, blank=True,
        related_name='ledger_entries_owned'
    )
    owner_area = models.ForeignKey(
        'core.Area', on_delete=models.PROTECT, null=True, blank=True,
        related_name='ledger_entries_owned'
    )
    owner_district = models.ForeignKey(
        'core.District', on_delete=models.PROTECT, null=True, blank=True,
        related_name='ledger_entries_owned'
    )
    owner_member = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        related_name='ledger_entries_owned'
    )
    
    # Counterparty for RECEIVABLE/PAYABLE
    counterparty_type = models.CharField(max_length=20, choices=OwnerType.choices, blank=True)
    counterparty_branch = models.ForeignKey(
        'core.Branch', on_delete=models.PROTECT, null=True, blank=True,
        related_name='ledger_entries_counterparty'
    )
    counterparty_area = models.ForeignKey(
        'core.Area', on_delete=models.PROTECT, null=True, blank=True,
        related_name='ledger_entries_counterparty'
    )
    counterparty_district = models.ForeignKey(
        'core.District', on_delete=models.PROTECT, null=True, blank=True,
        related_name='ledger_entries_counterparty'
    )
    
    # Amount - positive for increases, negative for decreases
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    balance_after = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    class SourceType(models.TextChoices):
        CONTRIBUTION = 'contribution', 'Contribution'
        EXPENDITURE = 'expenditure', 'Expenditure'
        REMITTANCE = 'remittance', 'Remittance'
        COMMISSION = 'commission', 'Commission'
        EXTERNAL_INCOME = 'external_income', 'External Income'
        ADJUSTMENT = 'adjustment', 'Manual Adjustment'
        OPENING_BALANCE = 'opening_balance', 'Opening Balance'
    
    source_type = models.CharField(max_length=20, choices=SourceType.choices)
    
    # Source references
    contribution = models.ForeignKey(
        'contributions.Contribution', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ledger_entries'
    )
    expenditure = models.ForeignKey(
        'expenditure.Expenditure', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ledger_entries'
    )
    remittance = models.ForeignKey(
        'contributions.Remittance', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ledger_entries'
    )
    commission = models.ForeignKey(
        'contributions.TitheCommission', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ledger_entries'
    )
    
    entry_date = models.DateField()
    description = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True)
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        REVERSED = 'reversed', 'Reversed'
        CLEARED = 'cleared', 'Cleared'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    reversed_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reverses'
    )
    
    is_locked = models.BooleanField(default=False)
    locked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-entry_date', '-created_at']
        verbose_name = 'Ledger Entry'
        verbose_name_plural = 'Ledger Entries'
        indexes = [
            models.Index(fields=['owner_type', 'entry_type', 'entry_date']),
            models.Index(fields=['owner_branch', 'entry_type']),
            models.Index(fields=['entry_date', 'source_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.get_entry_type_display()} - {self.get_owner_display()} - {self.amount}"
    
    def get_owner_display(self):
        if self.owner_type == self.OwnerType.MISSION:
            return "Mission"
        elif self.owner_type == self.OwnerType.BRANCH and self.owner_branch:
            return self.owner_branch.name
        elif self.owner_type == self.OwnerType.AREA and self.owner_area:
            return self.owner_area.name
        elif self.owner_type == self.OwnerType.DISTRICT and self.owner_district:
            return self.owner_district.name
        elif self.owner_type == self.OwnerType.MEMBER and self.owner_member:
            return self.owner_member.get_full_name()
        return "Unknown"
    
    def get_counterparty_display(self):
        if self.counterparty_type == self.OwnerType.MISSION:
            return "Mission"
        elif self.counterparty_type == self.OwnerType.BRANCH and self.counterparty_branch:
            return self.counterparty_branch.name
        return ""
