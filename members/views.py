"""
Members Views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponse
import csv
import io
import random

from accounts.models import User, UserProfile
from .models import Member


@login_required
def member_list(request):
    """List all members (users assigned to branches)."""
    if not (request.user.is_any_admin or request.user.is_pastor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    from core.models import Area, District, Branch
    
    # Show all users assigned to branches (not just role='member')
    # This includes members, pastors, staff, etc. who are part of the church
    members = User.objects.filter(is_active=True).select_related('branch', 'branch__district', 'branch__district__area')
    
    # Determine user's scope and filter accordingly
    user_scope = 'mission'  # Default for mission admin
    show_hierarchy_filters = True
    
    if request.user.is_branch_executive and request.user.branch:
        # Branch executives see only their branch members
        members = members.filter(branch=request.user.branch)
        user_scope = 'branch'
        show_hierarchy_filters = False
    elif request.user.is_pastor and request.user.branch:
        # Pastors see only their branch members (Mode A)
        members = members.filter(branch=request.user.branch)
        user_scope = 'branch'
        show_hierarchy_filters = False
    elif request.user.is_pastor and request.user.pastoral_rank == 'area' and request.user.managed_area:
        # Area pastors see all members in their area
        members = members.filter(branch__district__area=request.user.managed_area)
        user_scope = 'area'
        show_hierarchy_filters = True
    elif request.user.is_district_executive and request.user.managed_district:
        # District executives see all members in their district
        members = members.filter(branch__district=request.user.managed_district)
        user_scope = 'district'
        show_hierarchy_filters = True
    elif request.user.is_area_executive and request.user.managed_area:
        # Area executives see all members in their area
        members = members.filter(branch__district__area=request.user.managed_area)
        user_scope = 'area'
        show_hierarchy_filters = True
    
    # Initialize filter options based on user scope
    if user_scope == 'area':
        # Area executives see only districts and branches in their area
        districts = District.objects.filter(area=request.user.managed_area, is_active=True)
        branches = Branch.objects.filter(district__area=request.user.managed_area, is_active=True)
    elif user_scope == 'district':
        # District executives see only branches in their district
        districts = District.objects.filter(pk=request.user.managed_district.pk, is_active=True)
        branches = Branch.objects.filter(district=request.user.managed_district, is_active=True)
    elif user_scope == 'branch':
        # Branch executives see only their branch
        districts = District.objects.none()
        branches = Branch.objects.filter(pk=request.user.branch.pk, is_active=True)
    else:
        # Mission admins see all
        districts = District.objects.filter(is_active=True)
        branches = Branch.objects.filter(is_active=True)
    
    # Apply hierarchical filters (only for users with hierarchy access)
    if show_hierarchy_filters:
        area_id = request.GET.get('area')
        district_id = request.GET.get('district')
        branch_id = request.GET.get('branch')
        
        if area_id:
            members = members.filter(branch__district__area_id=area_id)
            districts = District.objects.filter(area_id=area_id, is_active=True)
            branches = Branch.objects.filter(district__area_id=area_id, is_active=True)
        elif district_id:
            members = members.filter(branch__district_id=district_id)
            branches = Branch.objects.filter(district_id=district_id, is_active=True)
        
        if branch_id:
            members = members.filter(branch_id=branch_id)
    
    # Role filter
    role = request.GET.get('role')
    if role:
        members = members.filter(role=role)
    
    # Status filter
    status = request.GET.get('status')
    if status == 'active':
        members = members.filter(is_active=True)
    elif status == 'inactive':
        members = members.filter(is_active=False)
    
    # Search
    query = request.GET.get('q')
    if query:
        members = members.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(member_id__icontains=query) |
            Q(phone__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(members, 25)
    page = request.GET.get('page')
    members = paginator.get_page(page)
    
    context = {
        'members': members,
        'areas': Area.objects.filter(pk=request.user.managed_area.pk, is_active=True) if user_scope == 'area' else Area.objects.filter(is_active=True),
        'districts': districts,
        'branches': branches,
        'user_scope': user_scope,
        'show_hierarchy_filters': show_hierarchy_filters,
    }
    
    return render(request, 'members/member_list.html', context)


@login_required
def member_add(request):
    """Add a new member."""
    from core.models import Branch, Area, District
    from groups.models import Group, GroupMembership
    from payroll.models import StaffPayrollProfile
    
    if not request.user.is_any_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        other_names = request.POST.get('other_names', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        gender = request.POST.get('gender', '')
        date_of_birth = request.POST.get('date_of_birth') or None
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        region = request.POST.get('region', '')
        profession = request.POST.get('profession', '')
        employer = request.POST.get('employer', '')
        skills = request.POST.get('skills', '')
        talents = request.POST.get('talents', '')
        marital_status = request.POST.get('marital_status', '')
        
        # Role assignment (mission admin only)
        if request.user.is_mission_admin:
            role = request.POST.get('role', 'member')
        else:
            role = 'member'
        
        # Branch selection - branch admins auto-assign to their branch
        if request.user.is_mission_admin:
            branch_id = request.POST.get('branch')
        else:
            branch_id = request.user.branch_id
        
        # Group assignment (mission admin only)
        group_id = request.POST.get('group') if request.user.is_mission_admin else None
        
        # Salary information (mission admin only)
        qualifies_for_salary = request.POST.get('qualifies_for_salary') == 'on' if request.user.is_mission_admin else False
        base_salary = request.POST.get('base_salary', '0') if request.user.is_mission_admin else '0'
        
        # Emergency contact
        emergency_name = request.POST.get('emergency_contact_name', '')
        emergency_phone = request.POST.get('emergency_contact_phone', '')
        emergency_relationship = request.POST.get('emergency_contact_relationship', '')
        
        # Baptism information
        baptized = request.POST.get('baptized', '')
        baptism_date = request.POST.get('baptism_date') or None
        baptism_by = request.POST.get('baptism_by', '')
        membership_date = request.POST.get('membership_date') or None
        previous_church = request.POST.get('previous_church', '')
        
        # Pastor information
        pastoral_rank = request.POST.get('pastoral_rank', '')
        ordination_date = request.POST.get('ordination_date') or None
        ordination_place = request.POST.get('ordination_place', '')
        ordaining_minister = request.POST.get('ordaining_minister', '')
        
        # Profile picture
        profile_picture = request.FILES.get('profile_picture')
        remove_photo = request.POST.get('remove_photo') == 'true'
        
        if not first_name or not last_name or not phone:
            messages.error(request, 'First name, last name, and phone are required.')
            return redirect('members:add')
        
        try:
            # Generate member ID based on branch code
            branch = Branch.objects.get(pk=branch_id) if branch_id else None
            branch_code = branch.code if branch and branch.code else 'MEM'
            
            # Get the next sequence number for this branch
            last_member = User.objects.filter(
                member_id__startswith=branch_code
            ).order_by('-member_id').first()
            
            if last_member and last_member.member_id:
                # Extract number from ID like "AN001" -> 1
                try:
                    # Remove the branch code prefix and get the numeric part
                    numeric_part = last_member.member_id[len(branch_code):]
                    if numeric_part.isdigit():
                        last_num = int(numeric_part)
                        next_num = last_num + 1
                    else:
                        # If the suffix is not numeric, start fresh
                        next_num = 1
                except (ValueError, IndexError):
                    next_num = 1
            else:
                next_num = 1
            
            # Format: AN001, AN002, etc.
            member_id = f"{branch_code}{next_num:03d}"
            
            # Double-check the member_id doesn't exist (race condition protection)
            if User.objects.filter(member_id=member_id).exists():
                # If it exists, find the next available number
                for i in range(10):  # Try up to 10 times
                    next_num += 1
                    member_id = f"{branch_code}{next_num:03d}"
                    if not User.objects.filter(member_id=member_id).exists():
                        break
                else:
                    # If still exists after 10 tries, use timestamp
                    import time
                    member_id = f"{branch_code}{int(time.time()) % 1000:03d}"
            
            # Generate random 5-digit PIN
            import random
            default_pin = str(random.randint(10000, 99999))
            
            # Create member
            member = User.objects.create(
                member_id=member_id,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email or None,
                gender=gender,
                date_of_birth=date_of_birth,
                role=role,
                pin=default_pin,
                qualifies_for_salary=qualifies_for_salary,
                base_salary=base_salary if qualifies_for_salary else 0,
                pastoral_rank=pastoral_rank if role == 'pastor' else '',
                ordination_date=ordination_date if role == 'pastor' else None,
                ordination_place=ordination_place if role == 'pastor' else '',
                ordaining_minister=ordaining_minister if role == 'pastor' else '',
            )
            
            # Handle profile picture - only if provided (new member won't have existing photo)
            if profile_picture:
                member.profile_picture = profile_picture
            
            member.set_password(default_pin)
            if branch_id:
                member.branch_id = branch_id
            
            # Assign managed district for district executives
            if role == 'district_executive' and branch_id:
                branch = Branch.objects.get(pk=branch_id)
                member.managed_district = branch.district
            
            member.save()
            
            # Create profile with emergency contact
            profile, _ = UserProfile.objects.get_or_create(user=member)
            profile.address = address
            profile.city = city
            profile.region = region
            profile.profession = profession
            profile.employer = employer
            profile.skills = skills
            profile.talents = talents
            profile.marital_status = marital_status
            profile.emergency_contact_name = emergency_name
            profile.emergency_contact_phone = emergency_phone
            profile.emergency_contact_relationship = emergency_relationship
            # Save baptism information
            if baptized == 'yes' and baptism_date:
                profile.baptism_date = baptism_date
                profile.baptism_by = baptism_by
            profile.membership_date = membership_date
            profile.previous_church = previous_church
            profile.save()
            
            # Create group memberships if assigned (mission admin only)
            group_ids = request.POST.getlist('groups')
            if group_ids and request.user.is_mission_admin:
                for group_id in group_ids:
                    try:
                        group = Group.objects.get(pk=group_id)
                        GroupMembership.objects.get_or_create(
                            group=group,
                            member=member,
                            role=GroupMembership.Role.MEMBER
                        )
                    except Group.DoesNotExist:
                        pass  # Silently fail if group doesn't exist
            
            # Create payroll profile if qualifies for salary (mission admin only)
            if qualifies_for_salary and request.user.is_mission_admin:
                try:
                    employee_id = f"EMP{member_id}"
                    StaffPayrollProfile.objects.create(
                        user=member,
                        employee_id=employee_id,
                        position=role.replace('_', ' ').title(),
                        base_salary=base_salary,
                        hire_date=member.date_joined.date()
                    )
                except Exception as e:
                    # Log error but don't fail the member creation
                    print(f"Error creating payroll profile: {e}")
            
            messages.success(request, f'Member "{member.get_full_name()}" added successfully. Member ID: {member.member_id}, PIN: {default_pin}')
            return redirect('members:list')
        except Exception as e:
            messages.error(request, f'Error adding member: {str(e)}')
    
    # Context for the form
    context = {
        'areas': Area.objects.filter(is_active=True).order_by('name'),
        'is_branch_admin': not request.user.is_mission_admin,
        'user_branch': request.user.branch,
        'available_groups': Group.objects.filter(is_active=True).order_by('name') if request.user.is_mission_admin else [],
        'member_group_ids': [],  # Empty for new member
    }
    
    return render(request, 'members/member_form.html', context)


@login_required
def member_detail(request, member_id):
    """View member details with tabs for Profile, Contributions, Attendance."""
    from contributions.models import Contribution
    from attendance.models import AttendanceRecord
    
    member = get_object_or_404(User, pk=member_id)
    profile = UserProfile.objects.filter(user=member).first()
    
    # Get contribution stats
    contributions = Contribution.objects.filter(member=member).order_by('-date')[:10]
    total_contributions = Contribution.objects.filter(member=member).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Get attendance stats - Fixed calculation
    attendance_records = AttendanceRecord.objects.filter(member=member).select_related('session')[:10]
    total_attendance = AttendanceRecord.objects.filter(member=member, status='present').count()
    total_services = AttendanceRecord.objects.filter(member=member).count()
    attendance_rate = (total_attendance / total_services * 100) if total_services > 0 else 0
    
    context = {
        'member': member,
        'profile': profile,
        'contributions': contributions,
        'total_contributions': total_contributions,
        'attendance_records': attendance_records,
        'total_attendance': total_attendance,
        'attendance_rate': attendance_rate,
        'tab': request.GET.get('tab', 'profile'),
    }
    return render(request, 'members/member_detail.html', context)


@login_required
def member_edit(request, member_id):
    """Edit member details."""
    from core.models import Branch, Area
    from groups.models import Group, GroupMembership
    from payroll.models import StaffPayrollProfile
    
    if not request.user.is_any_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    member = get_object_or_404(User, pk=member_id)
    profile, _ = UserProfile.objects.get_or_create(user=member)
    
    if request.method == 'POST':
        # Update member fields
        member.first_name = request.POST.get('first_name', member.first_name)
        member.last_name = request.POST.get('last_name', member.last_name)
        member.phone = request.POST.get('phone', member.phone)
        member.email = request.POST.get('email') or None
        member.gender = request.POST.get('gender', member.gender)
        member.date_of_birth = request.POST.get('date_of_birth') or member.date_of_birth
        
        # Role assignment (mission admin only)
        if request.user.is_mission_admin:
            member.role = request.POST.get('role', member.role)
        
        # Branch for mission admins only
        if request.user.is_mission_admin:
            branch_id = request.POST.get('branch')
            if branch_id:
                member.branch_id = branch_id
        
        # Salary information (mission admin only)
        if request.user.is_mission_admin:
            qualifies_for_salary = request.POST.get('qualifies_for_salary') == 'on'
            base_salary = request.POST.get('base_salary', '0')
            
            member.qualifies_for_salary = qualifies_for_salary
            member.base_salary = base_salary if qualifies_for_salary else 0
            
            # Update or create payroll profile
            if qualifies_for_salary:
                payroll_profile, created = StaffPayrollProfile.objects.get_or_create(
                    user=member,
                    defaults={
                        'employee_id': f"EMP{member.member_id}",
                        'position': member.role.replace('_', ' ').title(),
                        'base_salary': base_salary,
                        'hire_date': member.date_joined.date()
                    }
                )
                if not created:
                    payroll_profile.base_salary = base_salary
                    payroll_profile.position = member.role.replace('_', ' ').title()
                    payroll_profile.save()
            else:
                # Delete payroll profile if exists
                StaffPayrollProfile.objects.filter(user=member).delete()
        
        # Handle password reset for mission admins
        password_reset = False
        if request.user.is_mission_admin and request.POST.get('reset_password') == 'yes':
            member.set_password('12345')
            password_reset = True
            messages.warning(request, f'Password for {member.get_full_name()} has been reset to 12345')

        # Handle profile picture - process BEFORE save()
        profile_picture = request.FILES.get('profile_picture')
        remove_photo = request.POST.get('remove_photo') == 'true'
        
        if profile_picture:
            # Delete old picture if exists (for Cloudinary cleanup)
            if member.profile_picture:
                try:
                    member.profile_picture.delete(save=False)
                except Exception:
                    pass  # Ignore deletion errors
            member.profile_picture = profile_picture
        elif remove_photo and member.profile_picture:
            try:
                member.profile_picture.delete(save=False)
            except Exception:
                pass
            member.profile_picture = None

        member.save()
        
        # Update profile
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        profile.region = request.POST.get('region', '')
        profile.profession = request.POST.get('profession', '')
        profile.employer = request.POST.get('employer', '')
        profile.skills = request.POST.get('skills', '')
        profile.talents = request.POST.get('talents', '')
        profile.marital_status = request.POST.get('marital_status', '')
        profile.emergency_contact_name = request.POST.get('emergency_contact_name', '')
        profile.emergency_contact_phone = request.POST.get('emergency_contact_phone', '')
        profile.emergency_contact_relationship = request.POST.get('emergency_contact_relationship', '')
        # Update baptism information
        baptized = request.POST.get('baptized', '')
        if baptized == 'yes':
            profile.baptism_date = request.POST.get('baptism_date') or profile.baptism_date
            profile.baptism_by = request.POST.get('baptism_by', profile.baptism_by)
        profile.membership_date = request.POST.get('membership_date') or profile.membership_date
        profile.previous_church = request.POST.get('previous_church', profile.previous_church)
        profile.save()
        
        # Update group memberships (mission admin only)
        if request.user.is_mission_admin:
            group_ids = request.POST.getlist('groups')
            
            # Remove existing group memberships
            GroupMembership.objects.filter(member=member).delete()
            
            # Add new group memberships if selected
            for group_id in group_ids:
                try:
                    group = Group.objects.get(pk=group_id)
                    GroupMembership.objects.create(
                        group=group,
                        member=member,
                        role=GroupMembership.Role.MEMBER
                    )
                except Group.DoesNotExist:
                    pass  # Silently fail if group doesn't exist
        
        messages.success(request, f'Member "{member.get_full_name()}" updated successfully.')
        return redirect('members:detail', member_id=member_id)
    
    context = {
        'member': member,
        'profile': profile,
        'areas': Area.objects.filter(is_active=True).order_by('name'),
        'is_branch_admin': not request.user.is_mission_admin,
        'user_branch': request.user.branch,
        'available_groups': Group.objects.filter(is_active=True).order_by('name') if request.user.is_mission_admin else [],
        'member_group_ids': [g.group.id for g in member.group_memberships.all()],
    }
    return render(request, 'members/member_form.html', context)


@login_required
def get_districts(request, area_id):
    """AJAX endpoint to get districts for an area."""
    from core.models import District
    
    # Respect user hierarchy - only show districts they can access
    if request.user.is_area_executive and request.user.managed_area:
        # Area executives can only see districts in their area
        if str(area_id) != str(request.user.managed_area.pk):
            return JsonResponse({'districts': []})  # Return empty if trying to access other areas
        districts = District.objects.filter(area_id=area_id, is_active=True).values('id', 'name')
    elif request.user.is_district_executive and request.user.managed_district:
        # District executives can only see their own district
        if str(request.user.managed_district.area_id) != str(area_id):
            return JsonResponse({'districts': []})  # Return empty if not their area
        districts = District.objects.filter(pk=request.user.managed_district.pk, is_active=True).values('id', 'name')
    elif request.user.is_mission_admin or request.user.is_auditor:
        # Mission admins and auditors can see all districts in the area
        districts = District.objects.filter(area_id=area_id, is_active=True).values('id', 'name')
    else:
        # Other roles get no districts
        districts = District.objects.none().values('id', 'name')
    
    return JsonResponse({'districts': list(districts)})


@login_required
def get_branches(request, district_id):
    """AJAX endpoint to get branches for a district."""
    from core.models import Branch
    
    # Respect user hierarchy - only show branches they can access
    if request.user.is_area_executive and request.user.managed_area:
        # Area executives can only see branches in districts within their area
        district = District.objects.filter(pk=district_id, area=request.user.managed_area, is_active=True).first()
        if not district:
            return JsonResponse({'branches': []})  # Return empty if district not in their area
        branches = Branch.objects.filter(district_id=district_id, is_active=True).values('id', 'name')
    elif request.user.is_district_executive and request.user.managed_district:
        # District executives can only see branches in their district
        if str(district_id) != str(request.user.managed_district.pk):
            return JsonResponse({'branches': []})  # Return empty if not their district
        branches = Branch.objects.filter(district_id=district_id, is_active=True).values('id', 'name')
    elif request.user.is_branch_executive and request.user.branch:
        # Branch executives can only see their own branch
        if str(request.user.branch.district_id) != str(district_id):
            return JsonResponse({'branches': []})  # Return empty if not their district
        branches = Branch.objects.filter(pk=request.user.branch.pk, is_active=True).values('id', 'name')
    elif request.user.is_mission_admin or request.user.is_auditor:
        # Mission admins and auditors can see all branches in the district
        branches = Branch.objects.filter(district_id=district_id, is_active=True).values('id', 'name')
    else:
        # Other roles get no branches
        branches = Branch.objects.none().values('id', 'name')
    
    return JsonResponse({'branches': list(branches)})


@login_required
def download_import_template(request):
    """Download CSV template for member import."""
    if not request.user.is_any_admin:
        messages.error(request, 'Access denied.')
        return redirect('members:list')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="member_import_template.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'first_name', 'last_name', 'other_names', 'phone', 'email', 
        'gender', 'date_of_birth', 'branch_code', 'address', 
        'profession', 'marital_status', 'emergency_contact_name',
        'emergency_contact_phone', 'emergency_contact_relationship'
    ])
    # Sample row
    writer.writerow([
        'John', 'Doe', 'Middle', '+233201234567', 'john@example.com',
        'male', '1990-01-15', 'AN', '123 Main Street',
        'Teacher', 'married', 'Jane Doe', '+233209876543', 'Spouse'
    ])
    
    return response


@login_required
def member_import(request):
    """Import members from CSV file."""
    from core.models import Branch
    
    if not request.user.is_any_admin:
        messages.error(request, 'Access denied.')
        return redirect('members:list')
    
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        default_branch_id = request.POST.get('default_branch')
        
        if not csv_file:
            messages.error(request, 'Please select a CSV file.')
            return redirect('members:import')
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File must be a CSV file.')
            return redirect('members:import')
        
        try:
            # Read CSV file
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            success_count = 0
            error_count = 0
            errors = []
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    first_name = row.get('first_name', '').strip()
                    last_name = row.get('last_name', '').strip()
                    phone = row.get('phone', '').strip()
                    
                    if not first_name or not last_name or not phone:
                        errors.append(f"Row {row_num}: Missing required fields (first_name, last_name, phone)")
                        error_count += 1
                        continue
                    
                    # Check for duplicate phone
                    if User.objects.filter(phone=phone).exists():
                        errors.append(f"Row {row_num}: Phone {phone} already exists")
                        error_count += 1
                        continue
                    
                    # Determine branch
                    branch_code = row.get('branch_code', '').strip()
                    branch = None
                    if branch_code:
                        branch = Branch.objects.filter(code__iexact=branch_code).first()
                    if not branch and default_branch_id:
                        branch = Branch.objects.filter(pk=default_branch_id).first()
                    if not branch and request.user.branch:
                        branch = request.user.branch
                    
                    # Generate member ID
                    code = branch.code if branch else 'MEM'
                    last_member = User.objects.filter(
                        member_id__startswith=code
                    ).order_by('-member_id').first()
                    
                    if last_member and last_member.member_id:
                        try:
                            last_num = int(last_member.member_id[len(code):])
                            next_num = last_num + 1
                        except ValueError:
                            next_num = 1
                    else:
                        next_num = 1
                    
                    member_id = f"{code}{next_num:03d}"
                    default_pin = str(random.randint(10000, 99999))
                    
                    # Create member
                    member = User.objects.create(
                        member_id=member_id,
                        first_name=first_name,
                        last_name=last_name,
                        phone=phone,
                        email=row.get('email', '').strip() or None,
                        gender=row.get('gender', '').strip().lower() or 'other',
                        date_of_birth=row.get('date_of_birth', '').strip() or None,
                        role='member',
                        pin=default_pin,
                        branch=branch,
                    )
                    member.set_password(default_pin)
                    member.save()
                    
                    # Create profile
                    profile, _ = UserProfile.objects.get_or_create(user=member)
                    profile.address = row.get('address', '').strip()
                    profile.profession = row.get('profession', '').strip()
                    profile.marital_status = row.get('marital_status', '').strip().lower()
                    profile.emergency_contact_name = row.get('emergency_contact_name', '').strip()
                    profile.emergency_contact_phone = row.get('emergency_contact_phone', '').strip()
                    profile.emergency_contact_relationship = row.get('emergency_contact_relationship', '').strip()
                    profile.save()
                    
                    success_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    error_count += 1
            
            if success_count > 0:
                messages.success(request, f'Successfully imported {success_count} members.')
            if error_count > 0:
                messages.warning(request, f'{error_count} rows had errors.')
                for error in errors[:10]:  # Show first 10 errors
                    messages.error(request, error)
            
            return redirect('members:list')
            
        except Exception as e:
            messages.error(request, f'Error processing CSV: {str(e)}')
            return redirect('members:import')
    
    # GET request - show import form
    from core.models import Branch, Area
    
    context = {
        'areas': Area.objects.filter(is_active=True).order_by('name'),
        'branches': Branch.objects.filter(is_active=True).select_related('district').order_by('name'),
    }
    return render(request, 'members/member_import.html', context)
