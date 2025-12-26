"""
Management command to create sample data for testing
"""
import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for testing contributions, groups, attendance'

    def handle(self, *args, **options):
        from core.models import Branch, Area, District, FiscalYear
        from contributions.models import Contribution, ContributionType
        from groups.models import Group, GroupMembership
        from attendance.models import AttendanceSession, AttendanceRecord
        from members.models import Member
        
        self.stdout.write('Creating sample data...\n')
        
        # Get or create current fiscal year
        current_year = timezone.now().year
        fiscal_year, _ = FiscalYear.objects.get_or_create(
            year=current_year,
            defaults={
                'start_date': date(current_year, 1, 1),
                'end_date': date(current_year, 12, 31),
                'is_active': True
            }
        )
        self.stdout.write(f'Using fiscal year: {fiscal_year}\n')
        
        # Get existing branches
        branches = list(Branch.objects.all()[:5])
        if not branches:
            self.stdout.write(self.style.ERROR('No branches found! Create branches first.'))
            return
        
        self.stdout.write(f'Found {len(branches)} branches\n')
        
        # ==========================
        # 1. CREATE CONTRIBUTION TYPES
        # ==========================
        self.stdout.write('\n--- Creating Contribution Types ---\n')
        
        # Mission-wide types (already may exist)
        tithe_type, created = ContributionType.objects.get_or_create(
            code='TITHE',
            defaults={
                'name': 'Tithe',
                'category': 'tithe',
                'scope': 'mission',
                'is_individual': False,  # NOT individual - general collection
                'is_general': True,
                'mission_percentage': Decimal('20'),
                'area_percentage': Decimal('10'),
                'district_percentage': Decimal('10'),
                'branch_percentage': Decimal('60'),
                'frequency': 'weekly',
            }
        )
        if created:
            self.stdout.write(f'  Created: {tithe_type.name} (Mission-wide, General)')
        
        offering_type, created = ContributionType.objects.get_or_create(
            code='OFFERING',
            defaults={
                'name': 'Offering',
                'category': 'offering',
                'scope': 'mission',
                'is_individual': False,
                'is_general': True,
                'mission_percentage': Decimal('15'),
                'area_percentage': Decimal('10'),
                'district_percentage': Decimal('10'),
                'branch_percentage': Decimal('65'),
                'frequency': 'weekly',
            }
        )
        if created:
            self.stdout.write(f'  Created: {offering_type.name} (Mission-wide, General)')
        
        thanksgiving_type, created = ContributionType.objects.get_or_create(
            code='THANKSGIVING',
            defaults={
                'name': 'Thanksgiving Offering',
                'category': 'thanksgiving',
                'scope': 'mission',
                'is_individual': False,
                'is_general': True,
                'mission_percentage': Decimal('10'),
                'area_percentage': Decimal('10'),
                'district_percentage': Decimal('10'),
                'branch_percentage': Decimal('70'),
                'frequency': 'weekly',
            }
        )
        if created:
            self.stdout.write(f'  Created: {thanksgiving_type.name} (Mission-wide, General)')
        
        # Branch-specific contribution types
        if len(branches) >= 2:
            branch1, branch2 = branches[0], branches[1]
            
            # Branch 1 specific type
            branch1_project, created = ContributionType.objects.get_or_create(
                code=f'PROJECT_{branch1.code[:10]}',
                defaults={
                    'name': f'{branch1.name} Building Fund',
                    'category': 'project',
                    'scope': 'branch',
                    'branch': branch1,
                    'is_individual': False,
                    'is_general': True,
                    'mission_percentage': Decimal('0'),
                    'area_percentage': Decimal('0'),
                    'district_percentage': Decimal('0'),
                    'branch_percentage': Decimal('100'),
                    'frequency': 'monthly',
                    'target_amount': Decimal('50000'),
                    'is_closeable': True,
                }
            )
            if created:
                self.stdout.write(f'  Created: {branch1_project.name} (Branch-specific: {branch1.name})')
            
            # Branch 2 specific type
            branch2_welfare, created = ContributionType.objects.get_or_create(
                code=f'WELFARE_{branch2.code[:10]}',
                defaults={
                    'name': f'{branch2.name} Welfare Fund',
                    'category': 'welfare',
                    'scope': 'branch',
                    'branch': branch2,
                    'is_individual': False,
                    'is_general': True,
                    'mission_percentage': Decimal('0'),
                    'area_percentage': Decimal('0'),
                    'district_percentage': Decimal('5'),
                    'branch_percentage': Decimal('95'),
                    'frequency': 'weekly',
                }
            )
            if created:
                self.stdout.write(f'  Created: {branch2_welfare.name} (Branch-specific: {branch2.name})')
        
        # ==========================
        # 2. CREATE CONTRIBUTIONS FOR CURRENT MONTH
        # ==========================
        self.stdout.write('\n--- Creating Sample Contributions ---\n')
        
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        # Get all contribution types including branch-specific
        all_types = list(ContributionType.objects.filter(is_active=True))
        
        contributions_created = 0
        for branch in branches:
            # Get contribution types available to this branch
            branch_types = [t for t in all_types if 
                          t.scope == 'mission' or 
                          (t.scope == 'branch' and t.branch == branch)]
            
            for week in range(4):  # 4 weeks of data
                contribution_date = month_start + timedelta(days=week * 7)
                if contribution_date > today:
                    contribution_date = today
                
                for cont_type in branch_types:
                    # Random amounts
                    if cont_type.category == 'tithe':
                        amount = Decimal(random.randint(5000, 25000))
                    elif cont_type.category == 'offering':
                        amount = Decimal(random.randint(2000, 10000))
                    elif cont_type.category == 'project':
                        amount = Decimal(random.randint(1000, 5000))
                    else:
                        amount = Decimal(random.randint(500, 3000))
                    
                    contrib, created = Contribution.objects.get_or_create(
                        branch=branch,
                        contribution_type=cont_type,
                        date=contribution_date,
                        fiscal_year=fiscal_year,
                        defaults={
                            'amount': amount,
                            'member': None,  # General contribution, no specific member
                            'description': f'{cont_type.name} for week {week + 1}',
                            'status': 'verified',
                        }
                    )
                    if created:
                        contributions_created += 1
        
        self.stdout.write(f'  Created {contributions_created} contributions for {len(branches)} branches\n')
        
        # ==========================
        # 3. CREATE GROUPS FOR BRANCHES
        # ==========================
        self.stdout.write('\n--- Creating Sample Groups ---\n')
        
        group_names = [
            ('Youth Fellowship', 'youth'),
            ('Women\'s Ministry', 'women'),
            ('Men\'s Fellowship', 'men'),
            ('Choir', 'choir'),
            ('Prayer Warriors', 'prayer'),
        ]
        
        groups_created = 0
        for i, branch in enumerate(branches[:2]):  # Create groups for first 2 branches
            for name, code_suffix in group_names[:3]:  # 3 groups per branch
                group_code = f'{branch.code[:8]}_{code_suffix}'.upper()[:20]
                group, created = Group.objects.get_or_create(
                    code=group_code,
                    defaults={
                        'name': f'{branch.name} {name}',
                        'branch': branch,
                        'scope': 'branch',
                        'description': f'{name} group for {branch.name}',
                        'is_active': True,
                    }
                )
                if created:
                    groups_created += 1
                    self.stdout.write(f'  Created: {group.name} (Branch: {branch.name})')
                    
                    # Add some members to the group
                    branch_members = User.objects.filter(branch=branch, is_active=True)[:5]
                    for member in branch_members:
                        GroupMembership.objects.get_or_create(
                            group=group,
                            member=member,
                            defaults={
                                'role': random.choice(['member', 'leader', 'member']),
                                'joined_date': today - timedelta(days=random.randint(30, 365)),
                            }
                        )
        
        self.stdout.write(f'  Created {groups_created} groups\n')
        
        # ==========================
        # 4. CREATE ATTENDANCE RECORDS
        # ==========================
        self.stdout.write('\n--- Creating Sample Attendance ---\n')
        
        from attendance.models import ServiceType
        
        # Create service types
        sabbath_service, _ = ServiceType.objects.get_or_create(
            code='SABBATH_MAIN',
            defaults={
                'name': 'Sabbath Main Service',
                'day': 'sabbath',
            }
        )
        midweek_service, _ = ServiceType.objects.get_or_create(
            code='MIDWEEK',
            defaults={
                'name': 'Midweek Service',
                'day': 'weekday',
            }
        )
        
        service_types_list = [sabbath_service, midweek_service]
        
        sessions_created = 0
        for branch in branches[:3]:  # First 3 branches
            for week in range(4):
                session_date = month_start + timedelta(days=week * 7)
                if session_date > today:
                    continue
                
                for service_type in service_types_list:
                    session, created = AttendanceSession.objects.get_or_create(
                        branch=branch,
                        date=session_date,
                        service_type=service_type,
                        defaults={
                            'sermon_topic': f'{service_type.name} - Week {week + 1}',
                            'total_attendance': 0,
                        }
                    )
                    if created:
                        sessions_created += 1
                        
                        # Add attendance records
                        branch_members = User.objects.filter(branch=branch, is_active=True)[:20]
                        for member in branch_members:
                            # Random attendance (80% attendance rate)
                            if random.random() < 0.8:
                                AttendanceRecord.objects.get_or_create(
                                    session=session,
                                    member=member,
                                    defaults={
                                        'status': 'present',
                                        'check_in_time': timezone.now().time(),
                                    }
                                )
        
        self.stdout.write(f'  Created {sessions_created} attendance sessions\n')
        
        # ==========================
        # SUMMARY
        # ==========================
        self.stdout.write(self.style.SUCCESS('\n=== Sample Data Creation Complete ==='))
        self.stdout.write(f'- Fiscal Year: {fiscal_year.year}')
        self.stdout.write(f'- Contribution Types: {ContributionType.objects.count()}')
        self.stdout.write(f'- Contributions: {Contribution.objects.filter(date__month=today.month).count()} this month')
        self.stdout.write(f'- Groups: {Group.objects.count()}')
        self.stdout.write(f'- Attendance Sessions: {AttendanceSession.objects.filter(date__month=today.month).count()} this month')
        
        # Show branch-specific types
        branch_specific = ContributionType.objects.filter(scope='branch')
        if branch_specific:
            self.stdout.write('\nBranch-specific contribution types:')
            for ct in branch_specific:
                self.stdout.write(f'  - {ct.name} -> {ct.branch.name}')
