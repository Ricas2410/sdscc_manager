"""
Accounts Views - Authentication and user management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models
from django.http import JsonResponse

from .models import User, UserProfile, LoginHistory, UserChangeRequest


def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        member_id = request.POST.get('member_id', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember')
        
        user = authenticate(request, username=member_id, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Log the login
                LoginHistory.objects.create(
                    user=user,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    success=True
                )
                
                # Update last login IP
                user.last_login_ip = get_client_ip(request)
                user.save(update_fields=['last_login_ip'])
                
                # Set session expiry based on remember me
                if not remember:
                    request.session.set_expiry(0)  # Browser close
                
                messages.success(request, f'Welcome back, {user.get_short_name()}!')
                
                # Check if PIN/Password change is required
                # Set session variable for modal to display on dashboard
                if not user.pin_changed or user.pin == '12345':
                    request.session['show_pin_change_modal'] = True
                    request.session['pin_change_required'] = True
                
                # Redirect to next URL or dashboard (always go to dashboard now)
                next_url = request.GET.get('next', 'core:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Your account has been deactivated.')
        else:
            # Log failed attempt
            try:
                user = User.objects.get(member_id=member_id)
                LoginHistory.objects.create(
                    user=user,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    success=False
                )
            except User.DoesNotExist:
                pass
            
            messages.error(request, 'Invalid Member ID or password.')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    """User logout view."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def force_pin_change_view(request):
    """Force user to change PIN on first login."""
    if request.user.pin_changed and request.user.pin != '12345':
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        new_pin = request.POST.get('new_pin', '').strip()
        confirm_pin = request.POST.get('confirm_pin', '').strip()
        
        if len(new_pin) < 4 or len(new_pin) > 5 or not new_pin.isdigit():
            messages.error(request, 'PIN must be 4 or 5 digits.')
        elif new_pin != confirm_pin:
            messages.error(request, 'PINs do not match.')
        elif new_pin == '12345':
            messages.error(request, 'You cannot use the default PIN.')
        else:
            request.user.pin = new_pin
            request.user.pin_changed = True
            request.user.set_password(new_pin)  # Sync password with PIN for easy login
            request.user.save(update_fields=['pin', 'pin_changed', 'password'])
            
            # Re-login to keep session active after password change
            login(request, request.user)
            
            messages.success(request, 'PIN updated successfully. You can now access your dashboard.')
            return redirect('core:dashboard')
    
    return render(request, 'accounts/force_pin_change.html')


@login_required
def profile_view(request):
    """User profile view."""
    user = request.user
    
    # Get or create profile
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        # Update user fields
        user.phone = request.POST.get('phone', user.phone)
        user.email = request.POST.get('email', user.email)
        
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        
        # Update profile fields
        profile.address = request.POST.get('address', profile.address)
        profile.city = request.POST.get('city', profile.city)
        profile.region = request.POST.get('region', profile.region)
        profile.marital_status = request.POST.get('marital_status', profile.marital_status)
        profile.profession = request.POST.get('profession', profile.profession)
        profile.emergency_contact_name = request.POST.get('emergency_contact_name', profile.emergency_contact_name)
        profile.emergency_contact_phone = request.POST.get('emergency_contact_phone', profile.emergency_contact_phone)
        profile.emergency_contact_relationship = request.POST.get('emergency_contact_relationship', profile.emergency_contact_relationship)
        
        profile.save()
        
        messages.success(request, 'Profile updated successfully.')
        return redirect('accounts:profile')
    
    context = {
        'profile': profile,
        'login_history': LoginHistory.objects.filter(user=user).order_by('-timestamp')[:10],
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit_view(request):
    """Edit user profile - Only admins can edit their profiles, members view only."""
    user = request.user
    
    # Allow all users to edit their own profile
    # if not user.is_any_admin:
    #     # Redirect regular members to view-only profile page
    #     messages.info(request, 'Your profile information is managed by the church administration. If you need to update any details, please contact your branch administrator.')
    #     return redirect('accounts:profile')
    
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        # Update user fields
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone = request.POST.get('phone', user.phone)
        user.email = request.POST.get('email', user.email)
        user.date_of_birth = request.POST.get('date_of_birth') or user.date_of_birth
        user.gender = request.POST.get('gender', user.gender)
        
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        
        # Update profile fields
        profile.address = request.POST.get('address', profile.address)
        profile.city = request.POST.get('city', profile.city)
        profile.region = request.POST.get('region', profile.region)
        profile.marital_status = request.POST.get('marital_status', profile.marital_status)
        profile.profession = request.POST.get('profession', profile.profession)
        profile.emergency_contact_name = request.POST.get('emergency_contact_name', profile.emergency_contact_name)
        profile.emergency_contact_phone = request.POST.get('emergency_contact_phone', profile.emergency_contact_phone)
        profile.emergency_contact_relationship = request.POST.get('emergency_contact_relationship', profile.emergency_contact_relationship)
        
        profile.save()
        
        messages.success(request, 'Profile updated successfully.')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/profile_edit.html', {'profile': profile, 'can_edit': True})


@login_required
def change_pin_view(request):
    """Change user PIN."""
    if request.method == 'POST':
        current_pin = request.POST.get('current_pin', '')
        new_pin = request.POST.get('new_pin', '')
        confirm_pin = request.POST.get('confirm_pin', '')
        
        user = request.user
        
        # Verify current PIN
        if user.pin != current_pin:
            messages.error(request, 'Current PIN is incorrect.')
            return redirect('accounts:change_pin')
        
        # Validate new PIN
        if len(new_pin) < 5:
            messages.error(request, 'PIN must be at least 5 characters.')
            return redirect('accounts:change_pin')
        
        if new_pin != confirm_pin:
            messages.error(request, 'New PINs do not match.')
            return redirect('accounts:change_pin')
        
        # Update PIN
        user.pin = new_pin
        user.pin_changed = True
        user.save(update_fields=['pin', 'pin_changed'])
        
        messages.success(request, 'PIN changed successfully.')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/change_pin.html')


@login_required
def change_password_view(request):
    """Change user password."""
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        user = request.user
        
        # Verify current password
        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('accounts:change_password')
        
        # Validate new password
        if len(new_password) < 5:
            messages.error(request, 'Password must be at least 5 characters.')
            return redirect('accounts:change_password')
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('accounts:change_password')
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Re-authenticate
        login(request, user)
        
        messages.success(request, 'Password changed successfully.')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/change_password.html')


def password_reset_view(request):
    """Password reset request."""
    if request.method == 'POST':
        member_id = request.POST.get('member_id', '').strip()
        
        try:
            user = User.objects.get(member_id=member_id)
            # In production, send email/SMS with reset link
            # For now, just show a message
            messages.info(request, 'Please contact your branch administrator to reset your password.')
        except User.DoesNotExist:
            messages.error(request, 'Member ID not found.')
        
        return redirect('accounts:password_reset')
    
    return render(request, 'accounts/password_reset.html')


# Admin views

@login_required
def users_list(request):
    """List all users (admin only)."""
    from django.core.paginator import Paginator
    from django.db.models import Prefetch
    from core.models import Branch
    from payroll.models import StaffPayrollProfile
    
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    users = User.objects.select_related('branch').prefetch_related(
        'payroll_profile'
    ).order_by('first_name', 'last_name')
    
    # Search
    q = request.GET.get('q')
    if q:
        users = users.filter(
            models.Q(first_name__icontains=q) |
            models.Q(last_name__icontains=q) |
            models.Q(member_id__icontains=q) |
            models.Q(phone__icontains=q) |
            models.Q(email__icontains=q)
        )
    
    # Filters
    role = request.GET.get('role')
    if role:
        users = users.filter(role=role)
    
    branch_id = request.GET.get('branch')
    if branch_id:
        users = users.filter(branch_id=branch_id)
    
    # Pagination
    paginator = Paginator(users, 25)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    context = {
        'users': users,
        'roles': User.Role.choices,
        'branches': Branch.objects.filter(is_active=True).select_related('district'),
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'pastor_count': User.objects.filter(role='pastor').count(),
        'admin_count': User.objects.filter(role__in=['mission_admin', 'branch_executive', 'district_executive', 'area_executive']).count(),
    }
    
    return render(request, 'accounts/users_list.html', context)


@login_required
def user_detail(request, user_id):
    """View user details with contributions and attendance history."""
    from django.db.models import Sum, Count
    from contributions.models import Contribution
    from attendance.models import AttendanceRecord
    from payroll.models import StaffPayrollProfile
    from core.models import FiscalYear
    from datetime import date, timedelta
    
    if not (request.user.is_mission_admin or request.user.is_branch_executive):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    user = get_object_or_404(User.objects.select_related('branch', 'branch__district', 'branch__district__area'), pk=user_id)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    # Get current fiscal year
    fiscal_year = FiscalYear.get_current()
    
    # Contributions summary
    contributions = Contribution.objects.filter(member=user)
    total_contributions = contributions.aggregate(total=Sum('amount'))['total'] or 0
    this_year_contributions = contributions.filter(fiscal_year=fiscal_year).aggregate(total=Sum('amount'))['total'] or 0
    contributions_by_type = contributions.filter(fiscal_year=fiscal_year).values('contribution_type__name').annotate(
        total=Sum('amount'), count=Count('id')
    ).order_by('-total')
    recent_contributions = contributions.select_related('contribution_type', 'branch').order_by('-date')[:10]
    
    # Attendance summary
    attendance_records = AttendanceRecord.objects.filter(member=user)
    total_attendance = attendance_records.count()
    this_year_attendance = attendance_records.filter(session__date__year=date.today().year).count()
    
    # Last 30 days attendance
    thirty_days_ago = date.today() - timedelta(days=30)
    recent_attendance_count = attendance_records.filter(session__date__gte=thirty_days_ago).count()
    recent_attendance = attendance_records.select_related('session', 'session__service_type', 'session__branch').order_by('-session__date')[:10]
    
    # Payroll info for pastors/staff
    payroll_profile = None
    if user.role in ['pastor', 'staff']:
        payroll_profile = StaffPayrollProfile.objects.filter(user=user, is_active=True).first()
    
    # Active tab from query param
    active_tab = request.GET.get('tab', 'overview')
    
    context = {
        'member': user,
        'profile': profile,
        'active_tab': active_tab,
        # Contributions
        'total_contributions': total_contributions,
        'this_year_contributions': this_year_contributions,
        'contributions_by_type': contributions_by_type,
        'recent_contributions': recent_contributions,
        'contribution_count': contributions.count(),
        # Attendance
        'total_attendance': total_attendance,
        'this_year_attendance': this_year_attendance,
        'recent_attendance_count': recent_attendance_count,
        'recent_attendance': recent_attendance,
        # Payroll
        'payroll_profile': payroll_profile,
        'fiscal_year': fiscal_year,
    }
    
    return render(request, 'accounts/user_detail.html', context)


@login_required
def add_user(request):
    """Add a new user with auto-generated member ID."""
    from core.models import Branch
    from groups.models import Group, GroupMembership
    from payroll.models import StaffPayrollProfile
    from decimal import Decimal
    
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        # Handle form submission
        member_id = request.POST.get('user_id', '').strip().upper()
        pin = request.POST.get('pin', '')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        other_names = request.POST.get('other_names', '')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender', '')
        date_of_birth = request.POST.get('date_of_birth') or None
        role = request.POST.get('role')
        branch_id = request.POST.get('branch')
        group_ids = request.POST.getlist('groups')

        # Pastoral fields
        pastoral_rank = request.POST.get('pastoral_rank', 'none')
        ordination_date = request.POST.get('ordination_date') or None
        ordination_place = request.POST.get('ordination_place', '')
        ordaining_minister = request.POST.get('ordaining_minister', '')

        # Address fields
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        region = request.POST.get('region', '')
        marital_status = request.POST.get('marital_status', '')

        # Professional fields
        profession = request.POST.get('profession', '')
        employer = request.POST.get('employer', '')

        # Church journey fields
        baptism_date = request.POST.get('baptism_date') or None
        baptism_by = request.POST.get('baptism_by', '')
        membership_date = request.POST.get('membership_date') or None
        previous_church = request.POST.get('previous_church', '')

        # Emergency contact
        emergency_name = request.POST.get('emergency_contact_name', '')
        emergency_phone = request.POST.get('emergency_contact_phone', '')
        emergency_relationship = request.POST.get('emergency_contact_relationship', '')

        # Skills and talents
        skills = request.POST.get('skills', '')
        talents = request.POST.get('talents', '')

        # Pastoral notes
        pastoral_notes = request.POST.get('pastoral_notes', '')
        counseling_status = request.POST.get('counseling_status', '')

        # Pastor-specific fields
        is_commission_eligible = request.POST.get('is_commission_eligible') == 'on'
        base_salary = request.POST.get('base_salary', '0') or '0'
        
        # Auto-generate member_id if not provided or empty
        if not member_id:
            # Get the highest existing member ID and increment
            try:
                last_user = User.objects.all().order_by('-member_id').first()
                if last_user and last_user.member_id.isdigit():
                    next_id = int(last_user.member_id) + 1
                    member_id = str(next_id).zfill(3)  # Pad with zeros to 3 digits (001, 002, etc.)
                else:
                    # Start from 001 if no numeric users exist
                    member_id = '001'
            except:
                member_id = '001'
        
        # Validate member_id
        if User.objects.filter(member_id=member_id).exists():
            # Return error with ALL form data to repopulate
            context = {
                'edit_user': None,
                'profile': None,
                'roles': User.Role.choices,
                'branches': Branch.objects.filter(is_active=True),
                'groups': Group.objects.filter(is_active=True).select_related('category'),
                'error': f'Member ID "{member_id}" already exists.',
                'form_data': {
                    'user_id': member_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'other_names': other_names,
                    'email': email,
                    'phone': phone,
                    'gender': gender,
                    'date_of_birth': date_of_birth,
                    'role': role,
                    'branch': branch_id,
                    'pastoral_rank': pastoral_rank,
                    'ordination_date': ordination_date,
                    'ordination_place': ordination_place,
                    'ordaining_minister': ordaining_minister,
                    'address': address,
                    'city': city,
                    'region': region,
                    'marital_status': marital_status,
                    'profession': profession,
                    'employer': employer,
                    'baptism_date': baptism_date,
                    'baptism_by': baptism_by,
                    'membership_date': membership_date,
                    'previous_church': previous_church,
                    'emergency_contact_name': emergency_name,
                    'emergency_contact_phone': emergency_phone,
                    'emergency_contact_relationship': emergency_relationship,
                    'skills': skills,
                    'talents': talents,
                    'pastoral_notes': pastoral_notes,
                    'counseling_status': counseling_status,
                    'base_salary': base_salary,
                }
            }
            return render(request, 'accounts/user_form.html', context)
        
        # Validate PIN
        if len(pin) < 5:
            # Return error with ALL form data to repopulate
            context = {
                'edit_user': None,
                'profile': None,
                'roles': User.Role.choices,
                'branches': Branch.objects.filter(is_active=True),
                'groups': Group.objects.filter(is_active=True).select_related('category'),
                'error': 'PIN must be at least 5 characters.',
                'form_data': {
                    'user_id': member_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'other_names': other_names,
                    'email': email,
                    'phone': phone,
                    'gender': gender,
                    'date_of_birth': date_of_birth,
                    'role': role,
                    'branch': branch_id,
                    'pastoral_rank': pastoral_rank,
                    'ordination_date': ordination_date,
                    'ordination_place': ordination_place,
                    'ordaining_minister': ordaining_minister,
                    'address': address,
                    'city': city,
                    'region': region,
                    'marital_status': marital_status,
                    'profession': profession,
                    'employer': employer,
                    'baptism_date': baptism_date,
                    'baptism_by': baptism_by,
                    'membership_date': membership_date,
                    'previous_church': previous_church,
                    'emergency_contact_name': emergency_name,
                    'emergency_contact_phone': emergency_phone,
                    'emergency_contact_relationship': emergency_relationship,
                    'skills': skills,
                    'talents': talents,
                    'pastoral_notes': pastoral_notes,
                    'counseling_status': counseling_status,
                    'base_salary': base_salary,
                }
            }
            return render(request, 'accounts/user_form.html', context)
        
        try:
            user = User(
                member_id=member_id,
                first_name=first_name,
                other_names=other_names,
                last_name=last_name,
                email=email if email else None,  # Handle empty email
                phone=phone,
                gender=gender,
                date_of_birth=date_of_birth,
                role=role,
                pin=pin,
                pastoral_rank=pastoral_rank,
                ordination_date=ordination_date,
                ordination_place=ordination_place,
                ordaining_minister=ordaining_minister,
                base_salary=Decimal(base_salary) if base_salary else 0,
            )
            user.set_password(pin)  # Also set password for Django auth
            if branch_id:
                user.branch_id = branch_id

            # Set pastor-specific fields
            if role == 'pastor':
                user.is_commission_eligible = is_commission_eligible

            user.save()
            
            # Create/update profile with all fields
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.address = address
            profile.city = city
            profile.region = region
            profile.marital_status = marital_status
            profile.profession = profession
            profile.employer = employer
            profile.baptism_date = baptism_date
            profile.baptism_by = baptism_by
            profile.membership_date = membership_date
            profile.previous_church = previous_church
            profile.emergency_contact_name = emergency_name
            profile.emergency_contact_phone = emergency_phone
            profile.emergency_contact_relationship = emergency_relationship
            profile.skills = skills
            profile.talents = talents
            profile.pastoral_notes = pastoral_notes
            profile.counseling_status = counseling_status
            profile.save()
            
            # Create payroll record for pastor/staff if salary provided
            if role in ['pastor', 'staff'] and base_salary and Decimal(base_salary) > 0:
                StaffPayrollProfile.objects.create(
                    user=user,
                    base_salary=Decimal(base_salary),
                    is_active=True,
                )
            
            # Add to groups
            for group_id in group_ids:
                try:
                    group = Group.objects.get(pk=group_id)
                    GroupMembership.objects.create(group=group, member=user)
                except Group.DoesNotExist:
                    pass
            
            messages.success(request, f'User {user.get_full_name()} created successfully. Member ID: {user.member_id}')
            return redirect('accounts:users')
        except Exception as e:
            # Return error with ALL form data to repopulate
            context = {
                'edit_user': None,
                'profile': None,
                'roles': User.Role.choices,
                'branches': Branch.objects.filter(is_active=True),
                'groups': Group.objects.filter(is_active=True).select_related('category'),
                'error': f'Error adding member: {str(e)}',
                'form_data': {
                    'user_id': member_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'other_names': other_names,
                    'email': email,
                    'phone': phone,
                    'gender': gender,
                    'date_of_birth': date_of_birth,
                    'role': role,
                    'branch': branch_id,
                    'pastoral_rank': pastoral_rank,
                    'ordination_date': ordination_date,
                    'ordination_place': ordination_place,
                    'ordaining_minister': ordaining_minister,
                    'address': address,
                    'city': city,
                    'region': region,
                    'marital_status': marital_status,
                    'profession': profession,
                    'employer': employer,
                    'baptism_date': baptism_date,
                    'baptism_by': baptism_by,
                    'membership_date': membership_date,
                    'previous_church': previous_church,
                    'emergency_contact_name': emergency_name,
                    'emergency_contact_phone': emergency_phone,
                    'emergency_contact_relationship': emergency_relationship,
                    'skills': skills,
                    'talents': talents,
                    'pastoral_notes': pastoral_notes,
                    'counseling_status': counseling_status,
                    'base_salary': base_salary,
                }
            }
            return render(request, 'accounts/user_form.html', context)
    
    context = {
        'edit_user': None,
        'profile': None,
        'form_data': {},
        'roles': User.Role.choices,
        'branches': Branch.objects.filter(is_active=True),
        'groups': Group.objects.filter(is_active=True).select_related('category'),
    }
    return render(request, 'accounts/user_form.html', context)


@login_required
def edit_user(request, user_id):
    """Edit a user."""
    from core.models import Branch
    from groups.models import Group, GroupMembership
    
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    user = get_object_or_404(User, pk=user_id)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.gender = request.POST.get('gender', user.gender)
        user.date_of_birth = request.POST.get('date_of_birth') or user.date_of_birth
        user.role = request.POST.get('role', user.role)
        branch_id = request.POST.get('branch')
        if branch_id:
            user.branch_id = branch_id
        else:
            user.branch = None
        user.is_active = request.POST.get('is_active') == 'on'
        
        # Update PIN if provided
        new_pin = request.POST.get('pin', '').strip()
        if new_pin:
            if len(new_pin) >= 5:
                user.pin = new_pin
                user.set_password(new_pin)
            else:
                messages.warning(request, 'PIN not updated - must be at least 5 characters.')
        
        user.save()
        
        # Update emergency contact
        profile.emergency_contact_name = request.POST.get('emergency_contact_name', '')
        profile.emergency_contact_phone = request.POST.get('emergency_contact_phone', '')
        profile.emergency_contact_relationship = request.POST.get('emergency_contact_relationship', '')
        profile.save()
        
        # Update groups
        group_ids = request.POST.getlist('groups')
        # Remove current memberships
        GroupMembership.objects.filter(member=user).delete()
        # Add new memberships
        for group_id in group_ids:
            try:
                group = Group.objects.get(pk=group_id)
                GroupMembership.objects.create(group=group, member=user)
            except Group.DoesNotExist:
                pass
        
        messages.success(request, f'User {user.get_full_name()} updated successfully.')
        return redirect('accounts:users')
    
    # Get user's current groups
    user_groups = list(user.group_memberships.values_list('group_id', flat=True))
    
    context = {
        'edit_user': user,
        'profile': profile,
        'form_data': {},
        'roles': User.Role.choices,
        'branches': Branch.objects.filter(is_active=True),
        'groups': Group.objects.filter(is_active=True).select_related('category'),
        'user_groups': user_groups,
    }
    return render(request, 'accounts/user_form.html', context)


@login_required
def delete_user(request, user_id):
    """Delete a user."""
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    user = get_object_or_404(User, pk=user_id)
    
    # Prevent self-deletion
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('accounts:users')
    
    if request.method == 'POST':
        name = user.get_full_name()
        user.delete()
        messages.success(request, f'User "{name}" has been deleted.')
        return redirect('accounts:users')
    
    return render(request, 'accounts/user_confirm_delete.html', {'delete_user': user})


# Helper functions

def get_client_ip(request):
    """Get client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def dismiss_pin_change_modal(request):
    """AJAX endpoint to dismiss PIN change modal."""
    if request.method == 'POST':
        request.session['show_pin_change_modal'] = False
        return JsonResponse({'status': 'success', 'message': 'Modal dismissed'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def update_pin_ajax(request):
    """AJAX endpoint to update PIN."""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            new_pin = data.get('new_pin', '').strip()
            confirm_pin = data.get('confirm_pin', '').strip()
            
            if not new_pin or not confirm_pin:
                return JsonResponse({'status': 'error', 'message': 'All fields are required'}, status=400)
            
            if new_pin != confirm_pin:
                return JsonResponse({'status': 'error', 'message': 'PINs do not match'}, status=400)
            
            if len(new_pin) < 4:
                return JsonResponse({'status': 'error', 'message': 'PIN must be at least 4 characters'}, status=400)
            
            user = request.user
            user.pin = new_pin
            user.pin_changed = True
            user.save()
            
            # Clear the modal flag
            request.session['show_pin_change_modal'] = False
            
            return JsonResponse({'status': 'success', 'message': 'PIN updated successfully'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=400)


# ============ USER CHANGE REQUEST SYSTEM ============

@login_required
def request_profile_change(request):
    """Member submits a profile change request."""
    from .models import UserChangeRequest
    
    if request.method == 'POST':
        field_name = request.POST.get('field_name')
        new_value = request.POST.get('new_value', '').strip()
        reason = request.POST.get('reason', '').strip()
        
        if not field_name or not new_value:
            messages.error(request, 'Field name and new value are required.')
            return redirect('accounts:profile')
        
        # Get current value
        try:
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            
            user_fields = ['first_name', 'last_name', 'other_names', 'email', 'phone', 'date_of_birth', 'gender']
            
            if field_name in user_fields:
                old_value = str(getattr(request.user, field_name, ''))
            else:
                old_value = str(getattr(profile, field_name, ''))
            
            # Check if value is actually changing
            if old_value == new_value:
                messages.warning(request, 'New value is the same as current value.')
                return redirect('accounts:profile')
            
            # Create change request
            change_request = UserChangeRequest.objects.create(
                user=request.user,
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                reason=reason
            )
            
            messages.success(request, f'Change request submitted for {change_request.get_field_name_display()}. An administrator will review it.')
            return redirect('accounts:my_change_requests')
            
        except Exception as e:
            messages.error(request, f'Error submitting change request: {str(e)}')
            return redirect('accounts:profile')
    
    return redirect('accounts:profile')


@login_required
def my_change_requests(request):
    """View user's own change requests."""
    from .models import UserChangeRequest
    
    change_requests = UserChangeRequest.objects.filter(user=request.user).order_by('-requested_at')
    
    # Count by status
    pending_count = change_requests.filter(status='pending').count()
    approved_count = change_requests.filter(status='approved').count()
    rejected_count = change_requests.filter(status='rejected').count()
    
    context = {
        'change_requests': change_requests,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    
    return render(request, 'accounts/my_change_requests.html', context)


@login_required
def manage_change_requests(request):
    """Admin view to manage all change requests."""
    from .models import UserChangeRequest
    
    if not (request.user.is_mission_admin or request.user.is_branch_executive):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Filter by status
    status_filter = request.GET.get('status', 'pending')
    
    change_requests = UserChangeRequest.objects.select_related('user', 'reviewed_by').order_by('-requested_at')
    
    if status_filter and status_filter != 'all':
        change_requests = change_requests.filter(status=status_filter)
    
    # Filter by branch for branch executives
    if request.user.is_branch_executive and request.user.branch:
        change_requests = change_requests.filter(user__branch=request.user.branch)
    
    # Count by status
    all_requests = UserChangeRequest.objects.all()
    if request.user.is_branch_executive and request.user.branch:
        all_requests = all_requests.filter(user__branch=request.user.branch)
    
    pending_count = all_requests.filter(status='pending').count()
    approved_count = all_requests.filter(status='approved').count()
    rejected_count = all_requests.filter(status='rejected').count()
    applied_count = all_requests.filter(status='applied').count()
    
    context = {
        'change_requests': change_requests,
        'status_filter': status_filter,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'applied_count': applied_count,
    }
    
    return render(request, 'accounts/manage_change_requests.html', context)


@login_required
def review_change_request(request, request_id):
    """Admin reviews and approves/rejects a change request."""
    from .models import UserChangeRequest
    
    if not (request.user.is_mission_admin or request.user.is_branch_executive):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    change_request = get_object_or_404(UserChangeRequest, pk=request_id)
    
    # Branch executives can only review requests from their branch
    if request.user.is_branch_executive and request.user.branch:
        if change_request.user.branch != request.user.branch:
            messages.error(request, 'Access denied.')
            return redirect('accounts:manage_change_requests')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '').strip()
        
        if action == 'approve':
            change_request.approve(request.user, notes)
            messages.success(request, f'Change request approved and applied for {change_request.user.get_full_name()}.')
        elif action == 'reject':
            change_request.reject(request.user, notes)
            messages.success(request, f'Change request rejected for {change_request.user.get_full_name()}.')
        
        return redirect('accounts:manage_change_requests')
    
    context = {
        'change_request': change_request,
    }
    
    return render(request, 'accounts/review_change_request.html', context)

