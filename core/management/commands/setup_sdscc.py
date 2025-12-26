"""
Management command to set up initial SDSCC data with Ghanaian sample data
Headquarters: Asamankese, Eastern Region, Ghana
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User
from core.models import Area, District, Branch, FiscalYear, SiteSettings
from contributions.models import ContributionType, Contribution
from attendance.models import ServiceType
from groups.models import GroupCategory, Group
from expenditure.models import ExpenditureCategory
from decimal import Decimal
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Set up initial SDSCC data with Ghanaian sample data (HQ: Asamankese)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--superuser',
            action='store_true',
            help='Create superuser only',
        )
        parser.add_argument(
            '--full',
            action='store_true',
            help='Create full sample data including members and contributions',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Setting up SDSCC Ghana system (HQ: Asamankese)...\n')

        # Create site settings
        settings, created = SiteSettings.objects.get_or_create(pk=1)
        settings.site_name = 'SDSCC Ghana'
        settings.tagline = 'Seventh Day Sabbath Church of Christ - Ghana'
        settings.commission_percentage = Decimal('10.00')
        settings.email = 'info@sdsccghana.org'
        settings.phone = '+233 24 000 0000'
        settings.address = 'Mission Headquarters, Asamankese, Eastern Region, Ghana'
        settings.save()
        self.stdout.write(self.style.SUCCESS('✓ Site settings configured'))

        # Create fiscal year
        from django.utils import timezone
        current_year = timezone.now().year
        fiscal_year, created = FiscalYear.objects.get_or_create(
            year=current_year,
            defaults={
                'start_date': date(current_year, 1, 1),
                'end_date': date(current_year, 12, 31),
                'is_current': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Fiscal year {current_year} created'))

        # Create superuser (Mission Admin)
        if not User.objects.filter(member_id='ADMIN001').exists():
            admin = User.objects.create_superuser(
                member_id='ADMIN001',
                password='12345',
                email='admin@sdsccghana.org',
                first_name='Mission',
                last_name='Administrator',
                role='mission_admin',
                phone='+233240000001',
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Mission Admin created: {admin.member_id}'))

        if options['superuser']:
            return

        # ============================================
        # CREATE GHANAIAN CHURCH HIERARCHY
        # ============================================
        self.stdout.write('\n📍 Creating church hierarchy...')

        # AREAS (Regions)
        areas_data = [
            {'code': 'ER', 'name': 'Eastern Region Area'},
            {'code': 'GAR', 'name': 'Greater Accra Area'},
            {'code': 'AR', 'name': 'Ashanti Region Area'},
            {'code': 'WR', 'name': 'Western Region Area'},
            {'code': 'CR', 'name': 'Central Region Area'},
            {'code': 'VR', 'name': 'Volta Region Area'},
        ]

        areas = {}
        for area_data in areas_data:
            area, created = Area.objects.get_or_create(code=area_data['code'], defaults={'name': area_data['name']})
            areas[area_data['code']] = area
            if created:
                self.stdout.write(f"  ✓ Area: {area.name}")

        # DISTRICTS
        districts_data = [
            # Eastern Region
            {'code': 'ASM', 'name': 'Asamankese District', 'area': 'ER'},
            {'code': 'KOF', 'name': 'Koforidua District', 'area': 'ER'},
            {'code': 'NSA', 'name': 'Nkawkaw District', 'area': 'ER'},
            {'code': 'SOM', 'name': 'Somanya District', 'area': 'ER'},
            # Greater Accra
            {'code': 'ACC', 'name': 'Accra Central District', 'area': 'GAR'},
            {'code': 'TEM', 'name': 'Tema District', 'area': 'GAR'},
            {'code': 'ASH', 'name': 'Ashaiman District', 'area': 'GAR'},
            # Ashanti Region
            {'code': 'KUM', 'name': 'Kumasi District', 'area': 'AR'},
            {'code': 'OBU', 'name': 'Obuasi District', 'area': 'AR'},
            # Western Region
            {'code': 'TAK', 'name': 'Takoradi District', 'area': 'WR'},
            # Central Region
            {'code': 'CPT', 'name': 'Cape Coast District', 'area': 'CR'},
            # Volta Region
            {'code': 'HO', 'name': 'Ho District', 'area': 'VR'},
        ]

        districts = {}
        for dist_data in districts_data:
            district, created = District.objects.get_or_create(
                code=dist_data['code'],
                defaults={'name': dist_data['name'], 'area': areas[dist_data['area']]}
            )
            districts[dist_data['code']] = district
            if created:
                self.stdout.write(f"  ✓ District: {district.name}")

        # BRANCHES
        branches_data = [
            # Asamankese District (HQ)
            {'code': 'ASM-HQ', 'name': 'Asamankese Headquarters', 'district': 'ASM', 'target': 15000, 'address': 'Main Street, Asamankese'},
            {'code': 'ASM-01', 'name': 'Asamankese New Town', 'district': 'ASM', 'target': 8000},
            {'code': 'ASM-02', 'name': 'Adeiso Assembly', 'district': 'ASM', 'target': 5000},
            {'code': 'ASM-03', 'name': 'Akwatia Assembly', 'district': 'ASM', 'target': 6000},
            # Koforidua District
            {'code': 'KOF-01', 'name': 'Koforidua Central', 'district': 'KOF', 'target': 10000},
            {'code': 'KOF-02', 'name': 'Koforidua Adweso', 'district': 'KOF', 'target': 6000},
            {'code': 'KOF-03', 'name': 'Nsawam Assembly', 'district': 'KOF', 'target': 5500},
            # Accra Central District
            {'code': 'ACC-01', 'name': 'Accra Central Assembly', 'district': 'ACC', 'target': 12000},
            {'code': 'ACC-02', 'name': 'Kaneshie Assembly', 'district': 'ACC', 'target': 8000},
            {'code': 'ACC-03', 'name': 'Dansoman Assembly', 'district': 'ACC', 'target': 7500},
            {'code': 'ACC-04', 'name': 'Madina Assembly', 'district': 'ACC', 'target': 9000},
            # Tema District
            {'code': 'TEM-01', 'name': 'Tema Community 1', 'district': 'TEM', 'target': 8500},
            {'code': 'TEM-02', 'name': 'Tema Newtown', 'district': 'TEM', 'target': 6500},
            # Kumasi District
            {'code': 'KUM-01', 'name': 'Kumasi Adum', 'district': 'KUM', 'target': 11000},
            {'code': 'KUM-02', 'name': 'Kumasi Bantama', 'district': 'KUM', 'target': 7000},
            {'code': 'KUM-03', 'name': 'Kumasi Asokwa', 'district': 'KUM', 'target': 6000},
            # Takoradi District
            {'code': 'TAK-01', 'name': 'Takoradi Central', 'district': 'TAK', 'target': 8000},
            # Cape Coast District
            {'code': 'CPT-01', 'name': 'Cape Coast Central', 'district': 'CPT', 'target': 7000},
            # Ho District
            {'code': 'HO-01', 'name': 'Ho Central Assembly', 'district': 'HO', 'target': 5500},
        ]

        branches = {}
        for br_data in branches_data:
            branch, created = Branch.objects.get_or_create(
                code=br_data['code'],
                defaults={
                    'name': br_data['name'],
                    'district': districts[br_data['district']],
                    'monthly_tithe_target': Decimal(str(br_data['target'])),
                    'address': br_data.get('address', ''),
                }
            )
            branches[br_data['code']] = branch
            if created:
                self.stdout.write(f"  ✓ Branch: {branch.name}")

        # ============================================
        # CREATE CONTRIBUTION TYPES
        # ============================================
        self.stdout.write('\n💰 Creating contribution types...')

        contribution_types = [
            {'name': 'Tithe', 'code': 'TITHE', 'category': 'tithe', 'is_individual': True, 'is_general': False, 'branch_percentage': 60, 'mission_percentage': 40},
            {'name': 'Sabbath Offering', 'code': 'SAB-OFF', 'category': 'offering', 'is_general': True, 'branch_percentage': 100},
            {'name': 'Thanksgiving Offering', 'code': 'THANKS', 'category': 'thanksgiving', 'is_individual': True, 'branch_percentage': 100},
            {'name': 'Welfare Fund', 'code': 'WELFARE', 'category': 'welfare', 'is_general': True, 'branch_percentage': 100},
            {'name': 'Building Fund', 'code': 'BUILDING', 'category': 'project', 'is_closeable': True, 'branch_percentage': 70, 'mission_percentage': 30},
            {'name': 'Mission Support', 'code': 'MISSION', 'category': 'donation', 'is_general': True, 'branch_percentage': 0, 'mission_percentage': 100},
            {'name': 'Youth Fund', 'code': 'YOUTH', 'category': 'other', 'is_general': True, 'branch_percentage': 100},
            {'name': 'Women\'s Ministry', 'code': 'WOMEN', 'category': 'other', 'is_general': True, 'branch_percentage': 100},
            {'name': 'Men\'s Fellowship', 'code': 'MEN', 'category': 'other', 'is_general': True, 'branch_percentage': 100},
            {'name': 'Funeral Contribution', 'code': 'FUNERAL', 'category': 'funeral', 'is_individual': True, 'is_closeable': True, 'branch_percentage': 100},
        ]

        for ct_data in contribution_types:
            ct, created = ContributionType.objects.get_or_create(code=ct_data['code'], defaults=ct_data)
            if created:
                self.stdout.write(f"  ✓ {ct.name}")

        # ============================================
        # CREATE SERVICE TYPES
        # ============================================
        self.stdout.write('\n⛪ Creating service types...')

        service_types = [
            {'name': 'Sabbath Divine Service', 'code': 'SAB-DIV', 'day': 'sabbath'},
            {'name': 'Sabbath School', 'code': 'SAB-SCH', 'day': 'sabbath'},
            {'name': 'Midweek Bible Study', 'code': 'MID-WEEK', 'day': 'weekday'},
            {'name': 'Friday Prayer Meeting', 'code': 'FRI-PRAYER', 'day': 'weekday'},
            {'name': 'Youth Fellowship', 'code': 'YOUTH-FEL', 'day': 'any'},
            {'name': 'Women\'s Meeting', 'code': 'WOMEN-MTG', 'day': 'any'},
            {'name': 'Men\'s Fellowship', 'code': 'MEN-FEL', 'day': 'any'},
            {'name': 'Revival Service', 'code': 'REVIVAL', 'day': 'any'},
        ]

        for st_data in service_types:
            st, created = ServiceType.objects.get_or_create(code=st_data['code'], defaults=st_data)
            if created:
                self.stdout.write(f"  ✓ {st.name}")

        # ============================================
        # CREATE GROUP CATEGORIES
        # ============================================
        self.stdout.write('\n👥 Creating group categories...')

        group_categories = [
            {'name': 'Ministry', 'category_type': 'ministry'},
            {'name': 'Department', 'category_type': 'department'},
            {'name': 'Fellowship', 'category_type': 'fellowship'},
            {'name': 'Committee', 'category_type': 'committee'},
        ]

        for gc_data in group_categories:
            gc, created = GroupCategory.objects.get_or_create(name=gc_data['name'], defaults=gc_data)
            if created:
                self.stdout.write(f"  ✓ {gc.name}")

        # ============================================
        # CREATE EXPENDITURE CATEGORIES
        # ============================================
        self.stdout.write('\n📋 Creating expenditure categories...')

        expenditure_categories = [
            {'name': 'Utilities', 'code': 'UTIL', 'category_type': 'utilities'},
            {'name': 'Office Supplies', 'code': 'OFFICE', 'category_type': 'operations'},
            {'name': 'Church Maintenance', 'code': 'MAINT', 'category_type': 'maintenance'},
            {'name': 'Welfare Support', 'code': 'WELF', 'category_type': 'welfare'},
            {'name': 'Transportation', 'code': 'TRANS', 'category_type': 'operations'},
            {'name': 'Events & Programs', 'code': 'EVENTS', 'category_type': 'events'},
            {'name': 'Equipment', 'code': 'EQUIP', 'category_type': 'equipment'},
            {'name': 'Staff Salaries', 'code': 'SALARY', 'category_type': 'payroll', 'scope': 'mission'},
        ]

        for ec_data in expenditure_categories:
            ec, created = ExpenditureCategory.objects.get_or_create(code=ec_data['code'], defaults=ec_data)
            if created:
                self.stdout.write(f"  ✓ {ec.name}")

        # ============================================
        # CREATE SAMPLE USERS IF --full
        # ============================================
        if options['full']:
            self.create_sample_users(branches, fiscal_year)

        self.stdout.write(self.style.SUCCESS('\n✅ SDSCC Ghana setup complete!'))
        self.stdout.write(self.style.WARNING('\n📌 Login credentials:'))
        self.stdout.write(f'  Member ID: ADMIN001')
        self.stdout.write(f'  Password:  12345')
        self.stdout.write(f'\n  Headquarters: Asamankese, Eastern Region')
        self.stdout.write(f'  Total Areas: {Area.objects.count()}')
        self.stdout.write(f'  Total Districts: {District.objects.count()}')
        self.stdout.write(f'  Total Branches: {Branch.objects.count()}')

    def create_sample_users(self, branches, fiscal_year):
        """Create sample users with Ghanaian names."""
        self.stdout.write('\n👤 Creating sample users...')

        # Ghanaian names
        first_names_male = ['Kwame', 'Kofi', 'Kwaku', 'Yaw', 'Kwabena', 'Kojo', 'Kwesi', 'Akwasi', 'Nana', 'Osei', 'Mensah', 'Asante', 'Appiah', 'Boateng', 'Owusu']
        first_names_female = ['Ama', 'Akua', 'Abena', 'Yaa', 'Afia', 'Adjoa', 'Akosua', 'Efua', 'Adwoa', 'Afua', 'Esi', 'Araba', 'Ekua', 'Awo', 'Mansa']
        last_names = ['Mensah', 'Asante', 'Boateng', 'Owusu', 'Amoah', 'Appiah', 'Osei', 'Agyemang', 'Darko', 'Frimpong', 'Gyamfi', 'Nyarko', 'Asare', 'Adjei', 'Opoku', 'Antwi', 'Yeboah', 'Amponsah', 'Adomako', 'Bonsu']

        hq_branch = branches.get('ASM-HQ')

        # Create Area Executives
        for area in Area.objects.all()[:3]:
            fname = random.choice(first_names_male)
            lname = random.choice(last_names)
            member_id = f"AE{area.code}{random.randint(100,999)}"
            
            if not User.objects.filter(member_id=member_id).exists():
                user = User.objects.create_user(
                    member_id=member_id,
                    password='12345',
                    first_name=fname,
                    last_name=lname,
                    role='area_executive',
                    managed_area=area,
                    gender='M',
                    phone=f'+23324{random.randint(1000000,9999999)}',
                )
                self.stdout.write(f"  ✓ Area Exec: {user.get_full_name()} ({area.name})")

        # Create District Executives
        for district in District.objects.all()[:6]:
            fname = random.choice(first_names_male)
            lname = random.choice(last_names)
            member_id = f"DE{district.code}{random.randint(100,999)}"
            
            if not User.objects.filter(member_id=member_id).exists():
                user = User.objects.create_user(
                    member_id=member_id,
                    password='12345',
                    first_name=fname,
                    last_name=lname,
                    role='district_executive',
                    managed_district=district,
                    gender='M',
                    phone=f'+23320{random.randint(1000000,9999999)}',
                )
                self.stdout.write(f"  ✓ District Exec: {user.get_full_name()} ({district.name})")

        # Create Branch Executives and Pastors
        for code, branch in list(branches.items())[:10]:
            # Branch Executive
            fname = random.choice(first_names_male)
            lname = random.choice(last_names)
            member_id = f"BE{code.replace('-','')}{random.randint(10,99)}"
            
            if not User.objects.filter(member_id=member_id).exists():
                User.objects.create_user(
                    member_id=member_id,
                    password='12345',
                    first_name=fname,
                    last_name=lname,
                    role='branch_executive',
                    branch=branch,
                    gender='M',
                    phone=f'+23327{random.randint(1000000,9999999)}',
                )

            # Pastor
            fname = random.choice(first_names_male)
            lname = random.choice(last_names)
            member_id = f"PST{code.replace('-','')}{random.randint(10,99)}"
            
            if not User.objects.filter(member_id=member_id).exists():
                User.objects.create_user(
                    member_id=member_id,
                    password='12345',
                    first_name=fname,
                    last_name=lname,
                    role='pastor',
                    pastoral_rank='ordained_pastor',
                    branch=branch,
                    gender='M',
                    phone=f'+23355{random.randint(1000000,9999999)}',
                )

        # Create Auditor
        if not User.objects.filter(member_id='AUD001').exists():
            User.objects.create_user(
                member_id='AUD001',
                password='12345',
                first_name='Daniel',
                last_name='Asare',
                role='auditor',
                branch=hq_branch,
                gender='M',
                phone='+233244000002',
            )
            self.stdout.write("  ✓ Auditor: Daniel Asare")

        # Create sample members for HQ branch
        self.stdout.write('\n  Creating sample members for HQ...')
        for i in range(20):
            gender = random.choice(['M', 'F'])
            fname = random.choice(first_names_male if gender == 'M' else first_names_female)
            lname = random.choice(last_names)
            member_id = f"MEM{random.randint(10000,99999)}"
            
            if not User.objects.filter(member_id=member_id).exists():
                User.objects.create_user(
                    member_id=member_id,
                    password='12345',
                    first_name=fname,
                    last_name=lname,
                    role='member',
                    branch=hq_branch,
                    gender=gender,
                    phone=f'+23324{random.randint(1000000,9999999)}',
                    date_of_birth=date(random.randint(1960, 2000), random.randint(1,12), random.randint(1,28)),
                )

        self.stdout.write(f"  ✓ Created {User.objects.filter(role='member').count()} members")

        # Create sample contributions
        self.create_sample_contributions(branches, fiscal_year)

    def create_sample_contributions(self, branches, fiscal_year):
        """Create sample contribution records."""
        self.stdout.write('\n💵 Creating sample contributions...')

        tithe_type = ContributionType.objects.filter(code='TITHE').first()
        offering_type = ContributionType.objects.filter(code='SAB-OFF').first()
        
        if not tithe_type or not offering_type:
            self.stdout.write(self.style.WARNING('  ⚠ Contribution types not found, skipping'))
            return

        members = User.objects.filter(role='member')
        today = date.today()

        # Create contributions for last 4 weeks
        contributions_created = 0
        for week in range(4):
            contrib_date = today - timedelta(weeks=week)
            # Adjust to Saturday (Sabbath)
            days_until_saturday = (5 - contrib_date.weekday()) % 7
            sabbath_date = contrib_date - timedelta(days=contrib_date.weekday()) + timedelta(days=5)
            if sabbath_date > today:
                sabbath_date -= timedelta(weeks=1)

            for branch_code, branch in list(branches.items())[:8]:
                # General Sabbath offering
                if not Contribution.objects.filter(branch=branch, date=sabbath_date, contribution_type=offering_type).exists():
                    Contribution.objects.create(
                        contribution_type=offering_type,
                        branch=branch,
                        fiscal_year=fiscal_year,
                        date=sabbath_date,
                        amount=Decimal(str(random.randint(500, 3000))),
                        description=f'Sabbath Offering - {sabbath_date}',
                    )
                    contributions_created += 1

        # Create individual tithes
        for member in members[:15]:
            for week in range(2):
                contrib_date = today - timedelta(weeks=week)
                sabbath_date = contrib_date - timedelta(days=contrib_date.weekday()) + timedelta(days=5)
                if sabbath_date > today:
                    sabbath_date -= timedelta(weeks=1)

                if member.branch and not Contribution.objects.filter(member=member, date=sabbath_date, contribution_type=tithe_type).exists():
                    Contribution.objects.create(
                        contribution_type=tithe_type,
                        branch=member.branch,
                        fiscal_year=fiscal_year,
                        member=member,
                        date=sabbath_date,
                        amount=Decimal(str(random.randint(50, 500))),
                        description=f'Tithe - {member.get_full_name()}',
                    )
                    contributions_created += 1

        self.stdout.write(f"  ✓ Created {contributions_created} contribution records")
