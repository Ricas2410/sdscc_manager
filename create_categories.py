# Create Default Expenditure Categories
# Run: python manage.py shell < create_categories.py

from expenditure.models import ExpenditureCategory

print("Creating Expenditure Categories...")

# Mission-level categories
mission_categories = [
    {'name': 'Staff Salaries', 'code': 'SAL', 'scope': 'mission', 'description': 'Monthly staff payroll'},
    {'name': 'Mission Events', 'code': 'MEV', 'scope': 'mission', 'description': 'Mission-wide events and conferences'},
    {'name': 'Administrative Costs', 'code': 'ADM', 'scope': 'mission', 'description': 'Office supplies, utilities, etc.'},
    {'name': 'Training & Development', 'code': 'TRN', 'scope': 'mission', 'description': 'Staff training and development programs'},
    {'name': 'Marketing & Outreach', 'code': 'MKT', 'scope': 'mission', 'description': 'Mission-wide marketing and evangelism'},
    {'name': 'Equipment & Assets', 'code': 'EQP', 'scope': 'mission', 'description': 'Mission-level equipment purchases'},
]

# Branch-level categories
branch_categories = [
    {'name': 'Utilities', 'code': 'UTL', 'scope': 'branch', 'description': 'Electricity, water, internet'},
    {'name': 'Church Maintenance', 'code': 'MNT', 'scope': 'branch', 'description': 'Building repairs and maintenance'},
    {'name': 'Welfare & Benevolence', 'code': 'WEL', 'scope': 'branch', 'description': 'Support for members in need'},
    {'name': 'Transport & Travel', 'code': 'TRV', 'scope': 'branch', 'description': 'Local travel and transportation'},
    {'name': 'Office Supplies', 'code': 'OFF', 'scope': 'branch', 'description': 'Stationery and office materials'},
    {'name': 'Events & Programs', 'code': 'EVT', 'scope': 'branch', 'description': 'Local branch events'},
]

# Create mission categories
for cat in mission_categories:
    obj, created = ExpenditureCategory.objects.get_or_create(
        code=cat['code'],
        defaults={
            'name': cat['name'],
            'scope': cat['scope'],
            'description': cat['description'],
            'is_active': True
        }
    )
    if created:
        print(f"✓ Created mission category: {cat['name']}")
    else:
        print(f"  Already exists: {cat['name']}")

# Create branch categories
for cat in branch_categories:
    obj, created = ExpenditureCategory.objects.get_or_create(
        code=cat['code'],
        defaults={
            'name': cat['name'],
            'scope': cat['scope'],
            'description': cat['description'],
            'is_active': True
        }
    )
    if created:
        print(f"✓ Created branch category: {cat['name']}")
    else:
        print(f"  Already exists: {cat['name']}")

# Summary
mission_count = ExpenditureCategory.objects.filter(scope='mission', is_active=True).count()
branch_count = ExpenditureCategory.objects.filter(scope='branch', is_active=True).count()

print(f"\n✅ Done! Total categories: {mission_count} mission, {branch_count} branch")
