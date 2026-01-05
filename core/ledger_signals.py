"""
Ledger Signals - Automatically create ledger entries from financial transactions.
This integrates the ledger system with existing contribution/remittance/expenditure flows.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction


@receiver(post_save, sender='contributions.Contribution')
def create_contribution_ledger_entries(sender, instance, created, **kwargs):
    """
    Create ledger entries when a contribution is saved.
    Only creates entries for verified contributions (NOT drafts).
    Draft contributions do NOT create ledger entries until finalized.
    """
    # Only create ledger entries for verified contributions
    # Draft contributions are editable and should NOT have ledger entries
    if instance.status != 'verified':
        return
    
    # Check if ledger entries already exist for this contribution
    from core.ledger_models import LedgerEntry
    existing = LedgerEntry.objects.filter(contribution=instance).exists()
    if existing:
        return
    
    try:
        from core.ledger_service import LedgerService
        LedgerService.create_contribution_entries(instance)
    except Exception as e:
        # Log error but don't break the contribution save
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create ledger entries for contribution {instance.id}: {e}")


@receiver(post_save, sender='contributions.Remittance')
def create_remittance_ledger_entries(sender, instance, created, **kwargs):
    """
    Create ledger entries when a remittance is verified.
    Converts Mission RECEIVABLE to CASH.
    """
    # Only process when status changes to verified
    if instance.status != 'verified':
        return
    
    # Check if ledger entries already exist for this remittance
    from core.ledger_models import LedgerEntry
    existing = LedgerEntry.objects.filter(remittance=instance).exists()
    if existing:
        return
    
    # Only create entries if there's an amount sent
    if instance.amount_sent <= 0:
        return
    
    try:
        from core.ledger_service import LedgerService
        LedgerService.create_remittance_entries(instance, instance.amount_sent)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create ledger entries for remittance {instance.id}: {e}")


@receiver(post_save, sender='expenditure.Expenditure')
def create_expenditure_ledger_entries(sender, instance, created, **kwargs):
    """
    Create ledger entries when an expenditure is approved/paid.
    Expenditures reduce CASH only.
    """
    if not created:
        return
    
    # Only create ledger entries for approved or paid expenditures
    if instance.status not in ['approved', 'paid']:
        return
    
    try:
        from core.ledger_service import LedgerService
        LedgerService.create_expenditure_entries(instance)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create ledger entries for expenditure {instance.id}: {e}")


@receiver(post_save, sender='contributions.TitheCommission')
def create_commission_ledger_entries(sender, instance, created, **kwargs):
    """
    Create ledger entries when a commission is paid.
    """
    # Only process when status changes to paid
    if instance.status != 'paid':
        return
    
    # Check if ledger entries already exist
    from core.ledger_models import LedgerEntry
    existing = LedgerEntry.objects.filter(commission=instance).exists()
    if existing:
        return
    
    try:
        from core.ledger_service import LedgerService
        LedgerService.create_commission_entries(instance)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create ledger entries for commission {instance.id}: {e}")


@receiver(post_save, sender='contributions.MissionDonation')
def create_mission_donation_ledger_entries(sender, instance, created, **kwargs):
    """
    Create ledger entries when a mission donation is verified.
    Mission donations go directly to Mission CASH (not through branch).
    """
    # Only process verified donations
    if instance.status != 'verified':
        return
    
    # Check if ledger entries already exist
    from core.ledger_models import LedgerEntry
    existing = LedgerEntry.objects.filter(
        source_type=LedgerEntry.SourceType.CONTRIBUTION,
        description__contains=f'Mission Donation #{instance.id}'
    ).exists()
    if existing:
        return
    
    try:
        from core.ledger_service import LedgerService
        # Create Mission CASH entry directly (no branch involvement)
        LedgerService.create_entry(
            entry_type=LedgerEntry.EntryType.CASH,
            owner_type=LedgerEntry.OwnerType.MISSION,
            source_type=LedgerEntry.SourceType.CONTRIBUTION,
            amount=instance.amount,
            entry_date=instance.date,
            description=f'Mission Donation #{instance.id} - {instance.get_donation_type_display()}',
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create ledger entries for mission donation {instance.id}: {e}")
