"""
Area and District Financial Reports - Read-only reports derived from ledger data
"""

import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel, Area, District


class AreaFinancialReport(TimeStampedModel):
    """
    Read-only financial report for Area level finances.
    Derived from ledger data, respects closed months.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Area and time period
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='financial_reports')
    month = models.IntegerField()
    year = models.IntegerField()
    
    # Financial summary
    opening_balance = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0, 
        help_text='Opening balance at start of month'
    )
    
    # Income
    contributions_received = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0, 
        help_text='Area-scoped contributions received'
    )
    remittances_received = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0, 
        help_text='Remittances received from branches'
    )
    transfers_received = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0, 
        help_text='Transfers received from Mission or other levels'
    )
    total_income = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0, 
        help_text='Total income for the month'
    )
    
    # Expenditure
    expenditures = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0, 
        help_text='Area expenditures'
    )
    transfers_sent = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0, 
        help_text='Transfers sent to other levels'
    )
    total_expenditure = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0, 
        help_text='Total expenditure for the month'
    )
    
    # Balance
    closing_balance = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0, 
        help_text='Closing balance at end of month'
    )
    
    # Status
    is_generated = models.BooleanField(default=False)
    generated_at = models.DateTimeField(null=True, blank=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_area_reports'
    )
    
    # Report data
    report_data = models.JSONField(default=dict, help_text='Detailed report data')
    
    class Meta:
        ordering = ['-year', '-month', 'area__name']
        unique_together = ['area', 'month', 'year']
        verbose_name = 'Area Financial Report'
        verbose_name_plural = 'Area Financial Reports'
    
    def __str__(self):
        from calendar import month_name
        return f"{self.area.name} - {month_name[self.month]} {self.year}"
    
    def calculate_totals(self):
        """Calculate total income, expenditure, and closing balance."""
        self.total_income = (
            self.contributions_received + 
            self.remittances_received + 
            self.transfers_received
        )
        self.total_expenditure = self.expenditures + self.transfers_sent
        self.closing_balance = self.opening_balance + self.total_income - self.total_expenditure
        self.save()


class DistrictFinancialReport(TimeStampedModel):
    """
    Read-only financial report for District level finances.
    Derived from ledger data, respects closed months.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # District and time period
    district = models.ForeignKey(District, on_delete=models.PROTECT, related_name='financial_reports')
    month = models.IntegerField()
    year = models.IntegerField()
    
    # Financial summary
    opening_balance = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0, 
        help_text='Opening balance at start of month'
    )
    
    # Income
    contributions_received = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0, 
        help_text='District-scoped contributions received'
    )
    remittances_received = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0, 
        help_text='Remittances received from branches'
    )
    transfers_received = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0, 
        help_text='Transfers received from Area or other levels'
    )
    total_income = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0, 
        help_text='Total income for the month'
    )
    
    # Expenditure
    expenditures = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0, 
        help_text='District expenditures'
    )
    transfers_sent = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0, 
        help_text='Transfers sent to other levels'
    )
    total_expenditure = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0, 
        help_text='Total expenditure for the month'
    )
    
    # Balance
    closing_balance = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0, 
        help_text='Closing balance at end of month'
    )
    
    # Status
    is_generated = models.BooleanField(default=False)
    generated_at = models.DateTimeField(null=True, blank=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_district_reports'
    )
    
    # Report data
    report_data = models.JSONField(default=dict, help_text='Detailed report data')
    
    class Meta:
        ordering = ['-year', '-month', 'district__name']
        unique_together = ['district', 'month', 'year']
        verbose_name = 'District Financial Report'
        verbose_name_plural = 'District Financial Reports'
    
    def __str__(self):
        from calendar import month_name
        return f"{self.district.name} - {month_name[self.month]} {self.year}"
    
    def calculate_totals(self):
        """Calculate total income, expenditure, and closing balance."""
        self.total_income = (
            self.contributions_received + 
            self.remittances_received + 
            self.transfers_received
        )
        self.total_expenditure = self.expenditures + self.transfers_sent
        self.closing_balance = self.opening_balance + self.total_income - self.total_expenditure
        self.save()
