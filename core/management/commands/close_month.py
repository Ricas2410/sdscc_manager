"""
Management commands for month/year closing and archiving
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from core.models import FiscalYear, MonthlyClose, Branch
from contributions.models import Contribution
from attendance.models import AttendanceRecord
from announcements.models import Announcement
from django.db import transaction


class Command(BaseCommand):
    help = 'Close a month and prepare for the next month'

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, required=True, help='Year to close')
        parser.add_argument('--month', type=int, required=True, help='Month to close (1-12)')
        parser.add_argument('--force', action='store_true', help='Force close even if not all data is present')

    def handle(self, *args, **options):
        year = options['year']
        month = options['month']
        force = options['force']

        if not (1 <= month <= 12):
            self.stdout.write(self.style.ERROR('Month must be between 1 and 12'))
            return

        # Check if month is already closed
        if MonthlyClose.objects.filter(year=year, month=month, is_closed=True).exists():
            self.stdout.write(self.style.ERROR(f'Month {month}/{year} is already closed'))
            return

        # Get current fiscal year
        fiscal_year = FiscalYear.get_current()
        
        # Verify all branches have closed the month
        branches = Branch.objects.filter(is_active=True)
        unclosed_branches = []
        
        for branch in branches:
            close_record = MonthlyClose.objects.filter(
                fiscal_year=fiscal_year,
                branch=branch,
                month=month,
                year=year,
                is_closed=True
            ).first()
            
            if not close_record and not force:
                unclosed_branches.append(branch.name)

        if unclosed_branches and not force:
            self.stdout.write(self.style.WARNING(
                f'The following branches have not closed month {month}/{year}: {", ".join(unclosed_branches)}'
            ))
            self.stdout.write('Use --force to close anyway')
            return

        with transaction.atomic():
            # Close the month for all branches
            for branch in branches:
                MonthlyClose.objects.update_or_create(
                    fiscal_year=fiscal_year,
                    branch=branch,
                    month=month,
                    year=year,
                    defaults={
                        'is_closed': True,
                        'closed_at': timezone.now(),
                        'closed_by': None  # Can be set to a system user
                    }
                )

        self.stdout.write(self.style.SUCCESS(f'Successfully closed month {month}/{year}'))
