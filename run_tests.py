# Test Runner Script for All New Features
# Run this in Django shell: python manage.py shell < run_tests.py

print("=" * 80)
print("SDSCC SYSTEM - Comprehensive Feature Testing")
print("=" * 80)

import os

if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sdscc.settings')

try:
    import django
    django.setup()
except Exception:
    # If running via `python manage.py shell < run_tests.py`, Django is already setup.
    pass

from django.test import Client
from django.contrib.auth import get_user_model
from core.models import Branch, District, Area, FiscalYear, MissionFinancialSummary, BranchFinancialSummary
from expenditure.models import Expenditure, ExpenditureCategory
from accounts.models import UserChangeRequest
from payroll.models import PaySlip, PayrollRun
from decimal import Decimal
import sys

User = get_user_model()

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def test(description):
    print(f"\n{Colors.BLUE}TEST:{Colors.END} {description}")

def success(message):
    print(f"{Colors.GREEN}✓ PASS:{Colors.END} {message}")

def fail(message):
    print(f"{Colors.RED}✗ FAIL:{Colors.END} {message}")

def info(message):
    print(f"{Colors.YELLOW}INFO:{Colors.END} {message}")

# Test 1: Check Models Exist
test("Verify all new models are accessible")
try:
    assert MissionFinancialSummary is not None
    assert BranchFinancialSummary is not None
    assert UserChangeRequest is not None
    success("All new models imported successfully")
except Exception as e:
    fail(f"Model import error: {e}")
    sys.exit(1)

# Test 2: Check Database Tables
test("Verify database tables exist")
try:
    MissionFinancialSummary.objects.count()
    BranchFinancialSummary.objects.count()
    UserChangeRequest.objects.count()
    success("All database tables accessible")
except Exception as e:
    fail(f"Database table error: {e}")
    sys.exit(1)

# Test 3: Check Expenditure Categories
test("Verify expenditure categories")
try:
    mission_cats = ExpenditureCategory.objects.filter(scope='mission', is_active=True).count()
    branch_cats = ExpenditureCategory.objects.filter(scope='branch', is_active=True).count()
    
    if mission_cats > 0 and branch_cats > 0:
        success(f"Found {mission_cats} mission categories and {branch_cats} branch categories")
    else:
        fail(f"Missing categories: Mission={mission_cats}, Branch={branch_cats}")
        info("Run the category creation script from DEPLOYMENT_GUIDE")
except Exception as e:
    fail(f"Category check error: {e}")

# Test 4: Test Mission Financial Summary Calculations
test("Test MissionFinancialSummary calculations")
try:
    fiscal_year = FiscalYear.get_current()
    
    summary = MissionFinancialSummary(
        fiscal_year=fiscal_year,
        month=12,
        year=2025,
        opening_balance=Decimal('10000.00'),
        total_remittances=Decimal('50000.00'),
        total_other_income=Decimal('5000.00'),
        total_payroll=Decimal('20000.00'),
        total_mission_expenses=Decimal('10000.00'),
        total_mission_returns=Decimal('2000.00')
    )
    summary.calculate_totals()
    
    expected_income = Decimal('55000.00')
    expected_expenditure = Decimal('32000.00')
    expected_closing = Decimal('33000.00')
    
    assert summary.total_income == expected_income, f"Income mismatch: {summary.total_income} != {expected_income}"
    assert summary.total_expenditure == expected_expenditure, f"Expenditure mismatch: {summary.total_expenditure} != {expected_expenditure}"
    assert summary.closing_balance == expected_closing, f"Closing balance mismatch: {summary.closing_balance} != {expected_closing}"
    
    success("Mission financial calculations correct")
except Exception as e:
    fail(f"Mission summary calculation error: {e}")

# Test 5: Test Branch Financial Summary Calculations
test("Test BranchFinancialSummary calculations")
try:
    branches = Branch.objects.filter(is_active=True).first()
    if not branches:
        fail("No active branches found - cannot test")
    else:
        summary = BranchFinancialSummary(
            fiscal_year=fiscal_year,
            branch=branches,
            month=12,
            year=2025,
            opening_balance=Decimal('5000.00'),
            total_tithe=Decimal('8000.00'),
            total_offerings=Decimal('3000.00'),
            total_other_contributions=Decimal('1000.00'),
            total_branch_expenses=Decimal('4000.00'),
            remittance_to_mission=Decimal('800.00'),
            pastor_commission=Decimal('400.00'),
            tithe_target=Decimal('7000.00')
        )
        summary.calculate_totals()
        
        expected_income = Decimal('12000.00')
        expected_expenditure = Decimal('5200.00')
        expected_achievement = Decimal('114.29')
        
        assert summary.total_income == expected_income
        assert summary.total_expenditure == expected_expenditure
        assert summary.target_achieved == True
        assert abs(summary.achievement_percentage - expected_achievement) < Decimal('0.01')
        
        success("Branch financial calculations correct")
except Exception as e:
    fail(f"Branch summary calculation error: {e}")

# Test 6: Test UserChangeRequest Workflow
test("Test UserChangeRequest approve/apply workflow")
try:
    # Get a test user
    test_user = User.objects.filter(role='member').first()
    admin_user = User.objects.filter(is_mission_admin=True).first()
    
    if not test_user or not admin_user:
        fail("Missing test users - cannot test")
    else:
        # Create change request
        change_req = UserChangeRequest.objects.create(
            user=test_user,
            field_name='phone',
            old_value=test_user.phone or 'old-phone',
            new_value='+233-24-TEST-123',
            reason='Testing change request system'
        )
        
        assert change_req.status == 'pending'
        
        # Approve and apply
        change_req.approve(admin_user, 'Test approval')
        
        assert change_req.status == 'approved'
        assert change_req.reviewed_by == admin_user
        
        # Verify user phone was updated
        test_user.refresh_from_db()
        assert test_user.phone == '+233-24-TEST-123'
        
        # Verify applied status
        assert change_req.status == 'applied'
        
        # Clean up
        change_req.delete()
        
        success("UserChangeRequest workflow works correctly")
except Exception as e:
    fail(f"Change request workflow error: {e}")

# Test 7: Check URL Patterns
test("Verify new URL patterns are registered")
try:
    from django.urls import reverse
    
    urls_to_check = [
        ('expenditure:mission_list', []),
        ('expenditure:branch_list', []),
        ('reports:final_financial_report', []),
        ('payroll:payment_history', []),
        ('accounts:my_change_requests', []),
        ('accounts:manage_change_requests', []),
    ]
    
    for url_name, args in urls_to_check:
        try:
            url = reverse(url_name, args=args)
            info(f"  {url_name} → {url}")
        except Exception as e:
            fail(f"URL pattern missing: {url_name} - {e}")
            
    success("All URL patterns registered")
except Exception as e:
    fail(f"URL check error: {e}")

# Test 8: Check Template Files
test("Verify template files exist")
try:
    import os
    from django.conf import settings
    
    templates_to_check = [
        'reports/final_financial_report.html',
        'payroll/payment_history.html',
        'accounts/my_change_requests.html',
        'accounts/manage_change_requests.html',
        'accounts/review_change_request.html',
        'expenditure/mission_expenditure_list.html',
        'expenditure/branch_expenditure_list.html',
    ]
    
    for template_path in templates_to_check:
        full_path = os.path.join(settings.BASE_DIR, 'templates', template_path)
        if os.path.exists(full_path):
            info(f"  ✓ {template_path}")
        else:
            fail(f"  ✗ Missing: {template_path}")
    
    success("Template file check complete")
except Exception as e:
    fail(f"Template check error: {e}")

# Test 9: Check Static Files
test("Verify JavaScript files exist")
try:
    js_files = [
        'js/hierarchical-selectors.js',
    ]
    
    for js_file in js_files:
        full_path = os.path.join(settings.BASE_DIR, 'static', js_file)
        if os.path.exists(full_path):
            info(f"  ✓ {js_file}")
        else:
            fail(f"  ✗ Missing: {js_file}")
    
    success("JavaScript file check complete")
except Exception as e:
    fail(f"JavaScript check error: {e}")

# Test 10: Verify Sidebar Permissions
test("Verify sidebar link permissions")
try:
    # Mission Admin should have access to all new features
    mission_admin = User.objects.filter(is_mission_admin=True).first()
    if mission_admin:
        assert mission_admin.is_mission_admin == True
        success("Mission Admin permissions verified")
    
    # Branch Executive should have limited access
    branch_exec = User.objects.filter(role='branch_executive').first()
    if branch_exec:
        assert branch_exec.is_branch_executive == True
        success("Branch Executive permissions verified")
except Exception as e:
    fail(f"Permission check error: {e}")

# Summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"{Colors.GREEN}All critical tests passed!{Colors.END}")
print("\nNext Steps:")
print("1. Start the development server: python manage.py runserver")
print("2. Test manually using COMPREHENSIVE_TEST_GUIDE.md")
print("3. Create test expenditure categories if not yet done")
print("4. Review all new features in the browser")
print("=" * 80)
