"""
Monthly Closing System - Comprehensive month-end processing
Handles financial calculations, locking, and report generation
"""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from datetime import date, timedelta
from django.db.models import Sum, Q

from core.models import MonthlyClose, FiscalYear, Branch
from contributions.models import Contribution, Remittance, ContributionType
from expenditure.models import Expenditure
from payroll.models import PayrollRun


class MonthlyClosingService:
    """Service for handling monthly closing operations."""
    
    def __init__(self, branch, month, year):
        self.branch = branch
        self.month = month
        self.year = year
        # DEPRECATED: Year-as-state architecture - fiscal_year no longer assigned
        # Monthly closing now uses date filtering only
        
    def can_close_month(self):
        """Check if month can be closed."""
        # Check if already closed
        existing = MonthlyClose.objects.filter(
            branch=self.branch,
            month=self.month,
            year=self.year,
            is_closed=True
        ).first()
        
        if existing:
            return False, "Month already closed"
        
        # Check if it's a past or current month
        today = date.today()
        if self.year > today.year or (self.year == today.year and self.month > today.month):
            return False, "Cannot close future months"
        
        return True, "OK"
    
    @transaction.atomic
    def close_month(self, closed_by):
        """Close the month and calculate all financial summaries."""
        can_close, message = self.can_close_month()
        if not can_close:
            raise ValueError(message)
        
        # Get date range for the month
        start_date = date(self.year, self.month, 1)
        if self.month == 12:
            end_date = date(self.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(self.year, self.month + 1, 1) - timedelta(days=1)
        
        # Calculate contributions
        contributions = Contribution.objects.filter(
            branch=self.branch,
            date__gte=start_date,
            date__lte=end_date,
            status='verified'
        )
        
        # Get verified remittances - DEPRECATED: Use month/year filtering instead of date
        verified_remittances = Remittance.objects.filter(
            branch=self.branch,
            month=self.month,
            year=self.year,
            status='verified'
        )
        
        total_contributions = contributions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Calculate tithe specifically
        tithe_type = ContributionType.objects.filter(category='tithe', is_active=True).first()
        total_tithe = Decimal('0')
        if tithe_type:
            total_tithe = contributions.filter(contribution_type=tithe_type).aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
        
        # Calculate mission allocation (sum of all mission_amount fields)
        mission_allocation = contributions.aggregate(
            total=Sum('mission_amount')
        )['total'] or Decimal('0')
        
        # Calculate branch retained (sum of all branch_amount fields)
        branch_retained = contributions.aggregate(
            total=Sum('branch_amount')
        )['total'] or Decimal('0')
        
        # Calculate expenditures
        # DEPRECATED: Year-as-state architecture - Use date filtering only
        expenditures = Expenditure.objects.filter(
            branch=self.branch,
            date__gte=start_date,
            date__lte=end_date,
            status__in=['approved', 'paid']
        )
        
        total_expenditure = expenditures.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Get or create monthly close record
        # DEPRECATED: Year-as-state architecture - Create/get fiscal year for compatibility
        fiscal_year, _ = FiscalYear.objects.get_or_create(
            year=self.year,
            defaults={
                'start_date': date(self.year, 1, 1),
                'end_date': date(self.year, 12, 31),
                'is_current': False,  # DEPRECATED: Not used
                'is_closed': False
            }
        )
        
        monthly_close, created = MonthlyClose.objects.get_or_create(
            branch=self.branch,
            month=self.month,
            year=self.year,
            defaults={
                'fiscal_year': fiscal_year,  # DEPRECATED: For compatibility only
                'total_tithe': total_tithe,
                'total_contributions': total_contributions,
                'total_expenditure': total_expenditure,
                'mission_allocation': mission_allocation,
                'branch_retained': branch_retained,
                'is_closed': True,
                'closed_at': timezone.now(),
                'closed_by': closed_by
            }
        )
        
        if not created:
            # Update existing record
            monthly_close.total_tithe = total_tithe
            monthly_close.total_contributions = total_contributions
            monthly_close.total_expenditure = total_expenditure
            monthly_close.mission_allocation = mission_allocation
            monthly_close.branch_retained = branch_retained
            monthly_close.is_closed = True
            monthly_close.closed_at = timezone.now()
            monthly_close.closed_by = closed_by
            monthly_close.save()
        
        # Create or update remittance record for mission allocation
        # DEPRECATED: Year-as-state architecture - Use fiscal year for compatibility
        if mission_allocation > 0:
            remittance, _ = Remittance.objects.get_or_create(
                branch=self.branch,
                month=self.month,
                year=self.year,
                defaults={
                    'fiscal_year': fiscal_year,  # DEPRECATED: For compatibility only
                    'amount_due': mission_allocation,
                    'amount_sent': Decimal('0'),
                    'status': 'pending'
                }
            )
            
            if remittance.amount_due != mission_allocation:
                remittance.amount_due = mission_allocation
                remittance.save()
        
        # Lock ledger entries for this month
        try:
            from core.ledger_service import LedgerService
            LedgerService.lock_entries_for_month(self.month, self.year, self.branch)
        except Exception as e:
            # Log but don't fail the close
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to lock ledger entries: {e}")
        
        return monthly_close
    
    def reopen_month(self, reopened_by):
        """Reopen a closed month (admin only)."""
        monthly_close = MonthlyClose.objects.filter(
            branch=self.branch,
            month=self.month,
            year=self.year,
            is_closed=True
        ).first()
        
        if not monthly_close:
            raise ValueError("Month is not closed")
        
        monthly_close.is_closed = False
        monthly_close.updated_by = reopened_by
        monthly_close.save()
        
        return monthly_close
    
    def is_month_closed(self):
        """Check if month is closed."""
        return MonthlyClose.objects.filter(
            branch=self.branch,
            month=self.month,
            year=self.year,
            is_closed=True
        ).exists()
    
    @classmethod
    def is_date_in_closed_month(cls, branch, date_obj):
        """Check if a date falls in a closed month."""
        return MonthlyClose.objects.filter(
            branch=branch,
            month=date_obj.month,
            year=date_obj.year,
            is_closed=True
        ).exists()
    
    @classmethod
    def can_edit_contribution(cls, contribution, user):
        """Check if a contribution can be edited."""
        # Mission admin can always edit
        if user.is_mission_admin:
            return True, "OK"
        
        # Check if month is closed
        if cls.is_date_in_closed_month(contribution.branch, contribution.date):
            return False, "Month is closed. Contact mission admin to reopen."
        
        # Check 24-hour edit window
        from django.utils import timezone
        time_since_creation = timezone.now() - contribution.created_at
        if time_since_creation.total_seconds() > 86400:  # 24 hours
            return False, "Edit window expired (24 hours). Contact mission admin for changes."
        
        return True, "OK"
    
    @classmethod
    def can_edit_expenditure(cls, expenditure, user):
        """Check if an expenditure can be edited."""
        # Mission admin can always edit
        if user.is_mission_admin:
            return True, "OK"
        
        # Check if month is closed
        if cls.is_date_in_closed_month(expenditure.branch, expenditure.date):
            return False, "Month is closed. Contact mission admin to reopen."
        
        # Check 24-hour edit window
        from django.utils import timezone
        time_since_creation = timezone.now() - expenditure.created_at
        if time_since_creation.total_seconds() > 86400:  # 24 hours
            return False, "Edit window expired (24 hours). Contact mission admin for changes."
        
        return True, "OK"
    
    def get_monthly_summary(self):
        """Get monthly financial summary."""
        start_date = date(self.year, self.month, 1)
        if self.month == 12:
            end_date = date(self.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(self.year, self.month + 1, 1) - timedelta(days=1)
        
        # Get contributions
        # DEPRECATED: Year-as-state architecture - Use date filtering only
        contributions = Contribution.objects.filter(
            branch=self.branch,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Group by contribution type
        contributions_by_type = {}
        for contrib in contributions:
            type_name = contrib.contribution_type.name
            if type_name not in contributions_by_type:
                contributions_by_type[type_name] = {
                    'total': Decimal('0'),
                    'mission': Decimal('0'),
                    'branch': Decimal('0'),
                    'count': 0
                }
            contributions_by_type[type_name]['total'] += contrib.amount
            contributions_by_type[type_name]['mission'] += contrib.mission_amount
            contributions_by_type[type_name]['branch'] += contrib.branch_amount
            contributions_by_type[type_name]['count'] += 1
        
        # Get expenditures
        # DEPRECATED: Year-as-state architecture - Use date filtering only
        expenditures = Expenditure.objects.filter(
            branch=self.branch,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Group by category
        expenditures_by_category = {}
        for exp in expenditures:
            cat_name = exp.category.name
            if cat_name not in expenditures_by_category:
                expenditures_by_category[cat_name] = {
                    'total': Decimal('0'),
                    'count': 0
                }
            expenditures_by_category[cat_name]['total'] += exp.amount
            expenditures_by_category[cat_name]['count'] += 1
        
        # Get totals
        total_contributions = contributions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_mission = contributions.aggregate(total=Sum('mission_amount'))['total'] or Decimal('0')
        total_branch = contributions.aggregate(total=Sum('branch_amount'))['total'] or Decimal('0')
        total_expenditure = expenditures.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Get remittance status
        remittance = Remittance.objects.filter(
            branch=self.branch,
            month=self.month,
            year=self.year
        ).first()
        
        return {
            'branch': self.branch,
            'month': self.month,
            'year': self.year,
            'start_date': start_date,
            'end_date': end_date,
            'contributions_by_type': contributions_by_type,
            'expenditures_by_category': expenditures_by_category,
            'total_contributions': total_contributions,
            'total_mission': total_mission,
            'total_branch': total_branch,
            'total_expenditure': total_expenditure,
            'net_balance': total_branch - total_expenditure,
            'remittance': remittance,
            'is_closed': self.is_month_closed()
        }
