"""
Management command to finalize expired draft contributions.
Should be run periodically (e.g., every hour via cron/celery).
Auto-submits drafts that have exceeded their 24-hour edit window.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from contributions.models import Contribution


class Command(BaseCommand):
    help = 'Finalize draft contributions that have exceeded their 24-hour edit window'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be finalized without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()
        
        # Find all draft contributions that have expired
        expired_drafts = Contribution.objects.filter(
            status=Contribution.Status.DRAFT,
            draft_expires_at__lte=now
        )
        
        count = expired_drafts.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No expired drafts to finalize.'))
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Would finalize {count} expired drafts:'))
            for draft in expired_drafts:
                self.stdout.write(f'  - {draft.branch.name}: {draft.contribution_type.name} - {draft.amount} (expired {draft.draft_expires_at})')
            return
        
        # Finalize each expired draft
        finalized = 0
        errors = 0
        
        for draft in expired_drafts:
            try:
                draft.finalize_draft()
                finalized += 1
                self.stdout.write(f'Finalized: {draft.branch.name} - {draft.contribution_type.name} - {draft.amount}')
                
                # Create notification for branch admin
                try:
                    from core.models import Notification
                    # Notify branch executives
                    from accounts.models import User
                    branch_admins = User.objects.filter(
                        branch=draft.branch,
                        is_active=True
                    ).filter(
                        models.Q(role='branch_executive') | 
                        models.Q(role='branch_admin') |
                        models.Q(is_branch_executive=True)
                    )
                    
                    for admin in branch_admins:
                        Notification.objects.create(
                            user=admin,
                            notification_type='system',
                            title='Draft Contribution Auto-Submitted',
                            message=f'Your draft contribution ({draft.contribution_type.name} - {draft.amount}) has been automatically submitted after the 24-hour edit window expired.',
                            is_read=False
                        )
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Could not create notification: {e}'))
                    
            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f'Error finalizing draft {draft.id}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Finalized {finalized} drafts. Errors: {errors}'))
