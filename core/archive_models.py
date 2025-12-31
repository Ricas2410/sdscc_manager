"""
Archive Models - Year-based data archiving for SDSCC
Stores historical data organized by fiscal year
"""

import uuid
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel, FiscalYear

class YearlyArchive(TimeStampedModel):
    """Base model for yearly archived data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='archives')
    archive_date = models.DateTimeField(auto_now_add=True)
    data_summary = models.JSONField(default=dict, help_text="Summary of archived data")
    
    class Meta:
        abstract = True

class FinancialArchive(YearlyArchive):
    """Archived financial data for a fiscal year"""
    mission_total_contributions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    mission_total_expenditures = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    mission_total_tithes = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    mission_total_offerings = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Branch-level summaries
    branch_count = models.IntegerField(default=0)
    total_branch_contributions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_branch_expenditures = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Commission totals
    total_pastor_commissions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    commissions_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    commissions_pending = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Financial Archive"
        verbose_name_plural = "Financial Archives"
        unique_together = ['fiscal_year']
    
    def __str__(self):
        return f"Financial Archive - {self.fiscal_year}"

class MemberArchive(YearlyArchive):
    """Archived member statistics for a fiscal year"""
    total_members = models.IntegerField(default=0)
    new_members = models.IntegerField(default=0)
    transferred_members = models.IntegerField(default=0)
    inactive_members = models.IntegerField(default=0)
    
    # Attendance summary
    total_services = models.IntegerField(default=0)
    average_attendance = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    highest_attendance = models.IntegerField(default=0)
    lowest_attendance = models.IntegerField(default=0)
    
    # Member demographics summary
    members_by_branch = models.JSONField(default=dict, help_text="Member count by branch")
    members_by_area = models.JSONField(default=dict, help_text="Member count by area")
    members_by_district = models.JSONField(default=dict, help_text="Member count by district")
    
    class Meta:
        verbose_name = "Member Archive"
        verbose_name_plural = "Member Archives"
        unique_together = ['fiscal_year']
    
    def __str__(self):
        return f"Member Archive - {self.fiscal_year}"

class BranchArchive(YearlyArchive):
    """Archived branch-specific data for a fiscal year"""
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='yearly_archives')
    
    # Financial data
    total_contributions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_tithes = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_offerings = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_expenditures = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Member data
    member_count = models.IntegerField(default=0)
    new_members = models.IntegerField(default=0)
    average_attendance = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Pastor data
    pastor_name = models.CharField(max_length=200, blank=True)
    pastor_commission_earned = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    pastor_commission_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Performance metrics
    tithe_target_achievement = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    growth_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Branch Archive"
        verbose_name_plural = "Branch Archives"
        unique_together = ['fiscal_year', 'branch']
    
    def __str__(self):
        return f"{self.branch.name} Archive - {self.fiscal_year}"
