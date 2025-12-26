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
        'areas': Area.objects.filter(is_active=True),
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
        profession = request.POST.get('profession', '')
        marital_status = request.POST.get('marital_status', '')
        
        # Branch selection - branch admins auto-assign to their branch
        if request.user.is_mission_admin:
            branch_id = request.POST.get('branch')
        else:
            branch_id = request.user.branch_id
        
        # Emergency contact
        emergency_name = request.POST.get('emergency_contact_name', '')
        emergency_phone = request.POST.get('emergency_contact_phone', '')
        emergency_relationship = request.POST.get('emergency_contact_relationship', '')
        
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
                    last_num = int(last_member.member_id[len(branch_code):])
                    next_num = last_num + 1
                except ValueError:
                    next_num = 1
            else:
                next_num = 1
            
            # Format: AN001, AN002, etc.
    from core.models import Branch, Area
    
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
        
        # Branch for mission admins only
        if request.user.is_mission_admin:
            branch_id = request.POST.get('branch')
            if branch_id:
                member.branch_id = branch_id
        
        member.save()
        
        # Update profile
        profile.address = request.POST.get('address', '')
        profile.profession = request.POST.get('profession', '')
        profile.marital_status = request.POST.get('marital_status', '')
        profile.emergency_contact_name = request.POST.get('emergency_contact_name', '')
        profile.emergency_contact_phone = request.POST.get('emergency_contact_phone', '')
        profile.emergency_contact_relationship = request.POST.get('emergency_contact_relationship', '')
        profile.save()
        
        messages.success(request, f'Member "{member.get_full_name()}" updated successfully.')
        return redirect('members:detail', member_id=member_id)
    
    context = {
        'member': member,
        'profile': profile,
        'areas': Area.objects.filter(is_active=True).order_by('name'),
        'is_branch_admin': not request.user.is_mission_admin,
        'user_branch': request.user.branch,
    }
    return render(request, 'members/member_form.html', context)


@login_required
def get_districts(request, area_id):
    """AJAX endpoint to get districts for an area."""
    from core.models import District
    districts = District.objects.filter(area_id=area_id, is_active=True).values('id', 'name')
    return JsonResponse({'districts': list(districts)})


@login_required
def get_branches(request, district_id):
    """AJAX endpoint to get branches for a district."""
    from core.models import Branch
    branches = Branch.objects.filter(district_id=district_id, is_active=True).values('id', 'name')
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
