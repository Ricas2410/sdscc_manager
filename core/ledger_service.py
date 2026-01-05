"""
Ledger Service - Business logic for ledger operations.
Handles creation of ledger entries from financial transactions.
"""

from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, Q
from django.utils import timezone


class LedgerService:
    """
    Service class for ledger operations.
    Handles creation of ledger entries from financial transactions.
    """
    
    @classmethod
    def create_contribution_entries(cls, contribution):
        """
        Create ledger entries when a contribution is recorded.
        
        Example: 100 GHS tithe at Branch A, split 60% branch / 40% mission
        Creates:
        1. Branch CASH +100 (full amount received)
        2. Mission RECEIVABLE +40 (owed by branch)
        3. Branch PAYABLE +40 (owed to mission)
        """
        from core.ledger_models import LedgerEntry
        
        entries = []
        
        with transaction.atomic():
            # 1. Branch receives full cash
            branch_cash = LedgerEntry.objects.create(
                entry_type=LedgerEntry.EntryType.CASH,
                owner_type=LedgerEntry.OwnerType.BRANCH,
                owner_branch=contribution.branch,
                amount=contribution.amount,
                source_type=LedgerEntry.SourceType.CONTRIBUTION,
                contribution=contribution,
                entry_date=contribution.date,
                description=f"Contribution received: {contribution.contribution_type.name}",
                reference=contribution.reference or str(contribution.id)[:8]
            )
            entries.append(branch_cash)
            
            # 2. If mission has allocation, create RECEIVABLE for mission
            if contribution.mission_amount > 0:
                mission_receivable = LedgerEntry.objects.create(
                    entry_type=LedgerEntry.EntryType.RECEIVABLE,
                    owner_type=LedgerEntry.OwnerType.MISSION,
                    counterparty_type=LedgerEntry.OwnerType.BRANCH,
                    counterparty_branch=contribution.branch,
                    amount=contribution.mission_amount,
                    source_type=LedgerEntry.SourceType.CONTRIBUTION,
                    contribution=contribution,
                    entry_date=contribution.date,
                    description=f"Mission allocation from {contribution.branch.name}: {contribution.contribution_type.name}",
                    reference=contribution.reference or str(contribution.id)[:8]
                )
                entries.append(mission_receivable)
                
                # 3. Branch PAYABLE to mission
                branch_payable = LedgerEntry.objects.create(
                    entry_type=LedgerEntry.EntryType.PAYABLE,
                    owner_type=LedgerEntry.OwnerType.BRANCH,
                    owner_branch=contribution.branch,
                    counterparty_type=LedgerEntry.OwnerType.MISSION,
                    amount=contribution.mission_amount,
                    source_type=LedgerEntry.SourceType.CONTRIBUTION,
                    contribution=contribution,
                    entry_date=contribution.date,
                    description=f"Payable to Mission: {contribution.contribution_type.name}",
                    reference=contribution.reference or str(contribution.id)[:8]
                )
                entries.append(branch_payable)
            
            # 4. Area allocation (if any)
            if contribution.area_amount > 0:
                area_receivable = LedgerEntry.objects.create(
                    entry_type=LedgerEntry.EntryType.RECEIVABLE,
                    owner_type=LedgerEntry.OwnerType.AREA,
                    owner_area=contribution.branch.district.area,
                    counterparty_type=LedgerEntry.OwnerType.BRANCH,
                    counterparty_branch=contribution.branch,
                    amount=contribution.area_amount,
                    source_type=LedgerEntry.SourceType.CONTRIBUTION,
                    contribution=contribution,
                    entry_date=contribution.date,
                    description=f"Area allocation from {contribution.branch.name}",
                    reference=contribution.reference or str(contribution.id)[:8]
                )
                entries.append(area_receivable)
            
            # 5. District allocation (if any)
            if contribution.district_amount > 0:
                district_receivable = LedgerEntry.objects.create(
                    entry_type=LedgerEntry.EntryType.RECEIVABLE,
                    owner_type=LedgerEntry.OwnerType.DISTRICT,
                    owner_district=contribution.branch.district,
                    counterparty_type=LedgerEntry.OwnerType.BRANCH,
                    counterparty_branch=contribution.branch,
                    amount=contribution.district_amount,
                    source_type=LedgerEntry.SourceType.CONTRIBUTION,
                    contribution=contribution,
                    entry_date=contribution.date,
                    description=f"District allocation from {contribution.branch.name}",
                    reference=contribution.reference or str(contribution.id)[:8]
                )
                entries.append(district_receivable)
        
        return entries
    
    @classmethod
    def create_remittance_entries(cls, remittance, amount_remitted):
        """
        Create ledger entries when a branch remits money to mission.
        
        This converts:
        - Mission RECEIVABLE → Mission CASH
        - Branch PAYABLE → cleared
        - Branch CASH → reduced
        """
        from core.ledger_models import LedgerEntry
        
        entries = []
        payment_date = remittance.payment_date or timezone.now().date()
        ref = remittance.payment_reference or str(remittance.id)[:8]
        
        with transaction.atomic():
            # 1. Reduce Branch CASH
            branch_cash_out = LedgerEntry.objects.create(
                entry_type=LedgerEntry.EntryType.CASH,
                owner_type=LedgerEntry.OwnerType.BRANCH,
                owner_branch=remittance.branch,
                amount=-amount_remitted,
                source_type=LedgerEntry.SourceType.REMITTANCE,
                remittance=remittance,
                entry_date=payment_date,
                description=f"Remittance to Mission for {remittance.month}/{remittance.year}",
                reference=ref
            )
            entries.append(branch_cash_out)
            
            # 2. Reduce Branch PAYABLE
            branch_payable_clear = LedgerEntry.objects.create(
                entry_type=LedgerEntry.EntryType.PAYABLE,
                owner_type=LedgerEntry.OwnerType.BRANCH,
                owner_branch=remittance.branch,
                counterparty_type=LedgerEntry.OwnerType.MISSION,
                amount=-amount_remitted,
                source_type=LedgerEntry.SourceType.REMITTANCE,
                remittance=remittance,
                entry_date=payment_date,
                description=f"Payable cleared: Remittance for {remittance.month}/{remittance.year}",
                reference=ref
            )
            entries.append(branch_payable_clear)
            
            # 3. Reduce Mission RECEIVABLE
            mission_receivable_clear = LedgerEntry.objects.create(
                entry_type=LedgerEntry.EntryType.RECEIVABLE,
                owner_type=LedgerEntry.OwnerType.MISSION,
                counterparty_type=LedgerEntry.OwnerType.BRANCH,
                counterparty_branch=remittance.branch,
                amount=-amount_remitted,
                source_type=LedgerEntry.SourceType.REMITTANCE,
                remittance=remittance,
                entry_date=payment_date,
                description=f"Receivable cleared: Remittance from {remittance.branch.name}",
                reference=ref
            )
            entries.append(mission_receivable_clear)
            
            # 4. Increase Mission CASH
            mission_cash_in = LedgerEntry.objects.create(
                entry_type=LedgerEntry.EntryType.CASH,
                owner_type=LedgerEntry.OwnerType.MISSION,
                amount=amount_remitted,
                source_type=LedgerEntry.SourceType.REMITTANCE,
                remittance=remittance,
                entry_date=payment_date,
                description=f"Remittance received from {remittance.branch.name}",
                reference=ref
            )
            entries.append(mission_cash_in)
        
        return entries
    
    @classmethod
    def create_expenditure_entries(cls, expenditure):
        """
        Create ledger entries when an expenditure is recorded.
        Expenditures ONLY reduce CASH - never RECEIVABLE.
        """
        from core.ledger_models import LedgerEntry
        
        entries = []
        ref = expenditure.reference_number or str(expenditure.id)[:8]
        
        with transaction.atomic():
            if expenditure.level == 'mission':
                entry = LedgerEntry.objects.create(
                    entry_type=LedgerEntry.EntryType.CASH,
                    owner_type=LedgerEntry.OwnerType.MISSION,
                    amount=-expenditure.amount,
                    source_type=LedgerEntry.SourceType.EXPENDITURE,
                    expenditure=expenditure,
                    entry_date=expenditure.date,
                    description=f"Expenditure: {expenditure.title}",
                    reference=ref
                )
                entries.append(entry)
            elif expenditure.branch:
                entry = LedgerEntry.objects.create(
                    entry_type=LedgerEntry.EntryType.CASH,
                    owner_type=LedgerEntry.OwnerType.BRANCH,
                    owner_branch=expenditure.branch,
                    amount=-expenditure.amount,
                    source_type=LedgerEntry.SourceType.EXPENDITURE,
                    expenditure=expenditure,
                    entry_date=expenditure.date,
                    description=f"Expenditure: {expenditure.title}",
                    reference=ref
                )
                entries.append(entry)
        
        return entries
    
    @classmethod
    def create_commission_entries(cls, commission):
        """
        Create ledger entries when a commission is paid.
        Commission is a Mission expenditure paid to pastor.
        """
        from core.ledger_models import LedgerEntry
        
        entries = []
        
        with transaction.atomic():
            mission_cash_out = LedgerEntry.objects.create(
                entry_type=LedgerEntry.EntryType.CASH,
                owner_type=LedgerEntry.OwnerType.MISSION,
                amount=-commission.commission_amount,
                source_type=LedgerEntry.SourceType.COMMISSION,
                commission=commission,
                entry_date=commission.paid_at.date() if commission.paid_at else timezone.now().date(),
                description=f"Commission paid to {commission.recipient.get_full_name()}",
                reference=str(commission.id)[:8]
            )
            entries.append(mission_cash_out)
        
        return entries
    
    @classmethod
    def get_balance(cls, owner_type, entry_type, owner_branch=None, owner_area=None,
                   owner_district=None, owner_member=None, as_of_date=None):
        """
        Get the current balance for a specific owner and entry type.
        """
        from core.ledger_models import LedgerEntry
        
        queryset = LedgerEntry.objects.filter(
            owner_type=owner_type,
            entry_type=entry_type,
            status=LedgerEntry.Status.ACTIVE
        )
        
        if owner_type == LedgerEntry.OwnerType.BRANCH and owner_branch:
            queryset = queryset.filter(owner_branch=owner_branch)
        elif owner_type == LedgerEntry.OwnerType.AREA and owner_area:
            queryset = queryset.filter(owner_area=owner_area)
        elif owner_type == LedgerEntry.OwnerType.DISTRICT and owner_district:
            queryset = queryset.filter(owner_district=owner_district)
        elif owner_type == LedgerEntry.OwnerType.MEMBER and owner_member:
            queryset = queryset.filter(owner_member=owner_member)
        
        if as_of_date:
            queryset = queryset.filter(entry_date__lte=as_of_date)
        
        total = queryset.aggregate(total=Sum('amount'))['total']
        return total or Decimal('0')
    
    @classmethod
    def get_mission_cash_balance(cls, as_of_date=None):
        """Get Mission's spendable cash balance."""
        from core.ledger_models import LedgerEntry
        return cls.get_balance(
            LedgerEntry.OwnerType.MISSION,
            LedgerEntry.EntryType.CASH,
            as_of_date=as_of_date
        )
    
    @classmethod
    def get_mission_receivables(cls, as_of_date=None):
        """Get Mission's total receivables (money owed by branches)."""
        from core.ledger_models import LedgerEntry
        return cls.get_balance(
            LedgerEntry.OwnerType.MISSION,
            LedgerEntry.EntryType.RECEIVABLE,
            as_of_date=as_of_date
        )
    
    @classmethod
    def get_branch_cash_balance(cls, branch, as_of_date=None):
        """Get a branch's cash balance (money physically held)."""
        from core.ledger_models import LedgerEntry
        return cls.get_balance(
            LedgerEntry.OwnerType.BRANCH,
            LedgerEntry.EntryType.CASH,
            owner_branch=branch,
            as_of_date=as_of_date
        )
    
    @classmethod
    def get_branch_payables(cls, branch, as_of_date=None):
        """Get a branch's payables (money owed to mission)."""
        from core.ledger_models import LedgerEntry
        return cls.get_balance(
            LedgerEntry.OwnerType.BRANCH,
            LedgerEntry.EntryType.PAYABLE,
            owner_branch=branch,
            as_of_date=as_of_date
        )
    
    @classmethod
    def get_branch_spendable_cash(cls, branch, as_of_date=None):
        """
        Get a branch's spendable cash (cash minus payables).
        This is what the branch can actually spend.
        """
        cash = cls.get_branch_cash_balance(branch, as_of_date)
        payables = cls.get_branch_payables(branch, as_of_date)
        return cash - payables
    
    @classmethod
    def can_mission_spend(cls, amount):
        """
        Check if Mission can spend a given amount.
        Mission can ONLY spend CASH, not RECEIVABLE.
        """
        cash = cls.get_mission_cash_balance()
        return cash >= amount
    
    @classmethod
    def can_branch_spend(cls, branch, amount):
        """
        Check if a branch can spend a given amount.
        Branch can spend from their retained portion only.
        """
        spendable = cls.get_branch_spendable_cash(branch)
        return spendable >= amount
    
    @classmethod
    def get_receivables_by_branch(cls, as_of_date=None):
        """
        Get Mission's receivables grouped by branch.
        Returns dict: {branch: amount_owed}
        """
        from core.ledger_models import LedgerEntry
        from core.models import Branch
        
        queryset = LedgerEntry.objects.filter(
            owner_type=LedgerEntry.OwnerType.MISSION,
            entry_type=LedgerEntry.EntryType.RECEIVABLE,
            status=LedgerEntry.Status.ACTIVE
        )
        
        if as_of_date:
            queryset = queryset.filter(entry_date__lte=as_of_date)
        
        result = queryset.values('counterparty_branch').annotate(
            total=Sum('amount')
        ).filter(total__gt=0)
        
        branch_receivables = {}
        for item in result:
            if item['counterparty_branch']:
                try:
                    branch = Branch.objects.get(pk=item['counterparty_branch'])
                    branch_receivables[branch] = item['total']
                except Branch.DoesNotExist:
                    pass
        
        return branch_receivables
    
    @classmethod
    def get_monthly_summary(cls, owner_type, month, year, owner_branch=None):
        """
        Get monthly ledger summary for reporting.
        """
        from core.ledger_models import LedgerEntry
        from datetime import date
        from calendar import monthrange
        
        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)
        
        queryset = LedgerEntry.objects.filter(
            owner_type=owner_type,
            entry_date__gte=start_date,
            entry_date__lte=end_date,
            status=LedgerEntry.Status.ACTIVE
        )
        
        if owner_branch:
            queryset = queryset.filter(owner_branch=owner_branch)
        
        summary = {
            'cash_in': Decimal('0'),
            'cash_out': Decimal('0'),
            'receivables_added': Decimal('0'),
            'receivables_cleared': Decimal('0'),
            'payables_added': Decimal('0'),
            'payables_cleared': Decimal('0'),
        }
        
        for entry in queryset:
            if entry.entry_type == LedgerEntry.EntryType.CASH:
                if entry.amount > 0:
                    summary['cash_in'] += entry.amount
                else:
                    summary['cash_out'] += abs(entry.amount)
            elif entry.entry_type == LedgerEntry.EntryType.RECEIVABLE:
                if entry.amount > 0:
                    summary['receivables_added'] += entry.amount
                else:
                    summary['receivables_cleared'] += abs(entry.amount)
            elif entry.entry_type == LedgerEntry.EntryType.PAYABLE:
                if entry.amount > 0:
                    summary['payables_added'] += entry.amount
                else:
                    summary['payables_cleared'] += abs(entry.amount)
        
        summary['net_cash'] = summary['cash_in'] - summary['cash_out']
        summary['net_receivables'] = summary['receivables_added'] - summary['receivables_cleared']
        summary['net_payables'] = summary['payables_added'] - summary['payables_cleared']
        
        return summary
    
    @classmethod
    def lock_entries_for_month(cls, month, year, branch=None):
        """
        Lock all ledger entries for a given month (monthly closing).
        """
        from core.ledger_models import LedgerEntry
        from datetime import date
        from calendar import monthrange
        
        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)
        
        queryset = LedgerEntry.objects.filter(
            entry_date__gte=start_date,
            entry_date__lte=end_date,
            is_locked=False
        )
        
        if branch:
            queryset = queryset.filter(
                Q(owner_branch=branch) | Q(counterparty_branch=branch)
            )
        
        count = queryset.update(is_locked=True, locked_at=timezone.now())
        return count
