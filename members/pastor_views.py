from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from datetime import date, timedelta
import json

from members.models import Member
from core.models import Branch


@login_required
def pastor_manage_members(request):
    """
    Member management for pastors.
    Branch pastors can manage their assigned branch.
    Area/District pastors can manage all branches under them.
    """
    if not request.user.is_pastor:
        messages.error(request, 'Access denied. This page is for pastors only.')
        return redirect('core:dashboard')
    
    # Get branches this pastor can manage
    managed_branches = []
    selected_branch = None
    
    if request.user.pastoral_rank == 'branch' and request.user.branch:
        # Branch pastor can only manage their assigned branch
        managed_branches = [request.user.branch]
        selected_branch = request.user.branch
    elif request.user.pastoral_rank == 'area' and request.user.managed_area:
        # Area pastor can manage all branches in their area
        managed_branches = Branch.objects.filter(area=request.user.managed_area, is_active=True)
        selected_branch = managed_branches.first()
    elif request.user.pastoral_rank == 'district' and request.user.managed_district:
        # District pastor can manage all branches in their district
        managed_branches = Branch.objects.filter(district=request.user.managed_district, is_active=True)
        selected_branch = managed_branches.first()
    elif request.user.is_mission_admin:
        # Mission admin can manage all branches
        managed_branches = Branch.objects.filter(is_active=True)
        selected_branch = managed_branches.first()
    
    # Handle branch selection
    branch_id = request.GET.get('branch')
    if branch_id:
        try:
            selected_branch = managed_branches.get(id=branch_id)
        except Branch.DoesNotExist:
            pass
    
    if not selected_branch:
        messages.warning(request, 'No branches assigned for management.')
        return render(request, 'members/pastor_manage_members.html', {
            'managed_branches': [],
            'selected_branch': None,
            'members': [],
            'total_members': 0,
            'active_members': 0,
            'new_members_month': 0,
            'branch_members': 0,
        })
    
    # Get members for the selected branch or all managed branches
    if request.user.is_branch_pastor:
        # Branch pastor sees only their branch members
        members = Member.objects.filter(branch=selected_branch)
    else:
        # Area/District pastors can see all members in their managed branches
        members = Member.objects.filter(branch__in=managed_branches)
    
    # Apply filters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        members = members.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(member_id__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if status_filter:
        members = members.filter(status=status_filter)
    
    members = members.select_related('branch', 'branch__district').order_by('-join_date')
    
    # Calculate statistics
    total_members = members.count()
    active_members = members.filter(status='active').count()
    
    # New members this month
    this_month = date.today().replace(day=1)
    new_members_month = members.filter(join_date__gte=this_month).count()
    
    # Members in current branch
    branch_members = Member.objects.filter(branch=selected_branch).count()
    
    # Add member_since calculation
    for member in members:
        if member.join_date:
            years = (date.today() - member.join_date).days // 365
            member.member_since = years
    
    context = {
        'managed_branches': managed_branches,
        'selected_branch': selected_branch,
        'members': members,
        'total_members': total_members,
        'active_members': active_members,
        'new_members_month': new_members_month,
        'branch_members': branch_members,
    }
    
    return render(request, 'members/pastor_manage_members.html', context)


@login_required
@require_POST
@csrf_exempt
def pastor_add_member(request):
    """
    Add a new member (AJAX endpoint for pastor interface).
    """
    if not request.user.is_pastor:
        return JsonResponse({'success': False, 'message': 'Access denied'})
    
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'branch']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'success': False, 'message': f'{field.replace("_", " ").title()} is required'})
        
        # Check if pastor can manage this branch
        branch = get_object_or_404(Branch, id=data['branch'])
        
        if not _can_manage_branch(request.user, branch):
            return JsonResponse({'success': False, 'message': 'You cannot manage this branch'})
        
        # Generate member ID
        from members.models import generate_member_id
        member_id = generate_member_id(branch)
        
        # Create member
        member = Member.objects.create(
            member_id=member_id,
            first_name=data['first_name'].title(),
            last_name=data['last_name'].title(),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            address=data.get('address', ''),
            date_of_birth=data.get('date_of_birth'),
            gender=data.get('gender', ''),
            branch=branch,
            join_date=date.today(),
            status='active',
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Member {member.get_full_name} added successfully',
            'member_id': member.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid data format'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def pastor_member_detail(request, member_id):
    """
    View member details (pastor interface).
    """
    if not request.user.is_pastor:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    member = get_object_or_404(Member, id=member_id)
    
    # Check if pastor can manage this member's branch
    if not _can_manage_branch(request.user, member.branch):
        messages.error(request, 'You cannot view members from this branch.')
        return redirect('members:pastor_manage')
    
    # Get member statistics
    from contributions.models import Contribution
    from attendance.models import Attendance
    
    total_contributions = Contribution.objects.filter(member=member).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    attendance_count = Attendance.objects.filter(member=member).count()
    
    context = {
        'member': member,
        'total_contributions': total_contributions,
        'attendance_count': attendance_count,
    }
    
    return render(request, 'members/pastor_member_detail.html', context)


@login_required
def pastor_edit_notes(request, member_id):
    """Edit pastoral notes for a member."""
    if not request.user.is_pastor:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    member = get_object_or_404(Member, id=member_id)
    
    # Check permissions
    if not _can_manage_branch(request.user, member.branch):
        messages.error(request, 'You cannot manage members from this branch.')
        return redirect('members:pastor_manage')
        
    if request.method == 'POST':
        notes = request.POST.get('notes', '').strip()
        member.notes = notes
        member.save(update_fields=['notes'])
        messages.success(request, 'Pastoral notes updated.')
        
    return redirect('members:pastor_detail', member_id=member.id)


@login_required
def pastor_transfer_member(request, member_id):
    """
    Transfer member to another branch (for area/district pastors).
    """
    if not request.user.is_pastor:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    member = get_object_or_404(Member, id=member_id)
    
    # Check if pastor can manage this member's branch
    if not _can_manage_branch(request.user, member.branch):
        messages.error(request, 'You cannot transfer members from this branch.')
        return redirect('members:pastor_manage')
    
    # Branch pastors cannot transfer members
    if request.user.is_branch_pastor:
        messages.error(request, 'Branch pastors cannot transfer members.')
        return redirect('members:pastor_manage')
    
    # Get available branches for transfer
    available_branches = []
    if request.user.is_area_pastor and request.user.area:
        available_branches = Branch.objects.filter(area=request.user.area, is_active=True)
    elif request.user.is_district_pastor and request.user.district:
        available_branches = Branch.objects.filter(district=request.user.district, is_active=True)
    elif request.user.is_mission_admin:
        available_branches = Branch.objects.filter(is_active=True)
    
    if request.method == 'POST':
        new_branch_id = request.POST.get('new_branch')
        transfer_reason = request.POST.get('reason', '')
        
        if new_branch_id:
            new_branch = get_object_or_404(Branch, id=new_branch_id)
            
            # Create transfer record
            member.status = 'transferred'
            member.save()
            
            # Create new member record in new branch
            new_member = Member.objects.create(
                member_id=generate_member_id(new_branch),
                first_name=member.first_name,
                last_name=member.last_name,
                phone=member.phone,
                email=member.email,
                address=member.address,
                date_of_birth=member.date_of_birth,
                gender=member.gender,
                branch=new_branch,
                join_date=date.today(),
                status='active',
                transfer_from=member.branch,
                transfer_reason=transfer_reason,
                created_by=request.user
            )
            
            messages.success(request, f'Member transferred to {new_branch.name} successfully.')
            return redirect('members:pastor_manage')
    
    context = {
        'member': member,
        'available_branches': available_branches,
    }
    
    return render(request, 'members/pastor_transfer_member.html', context)


def _can_manage_branch(user, branch):
    """Helper function to check if user can manage a branch."""
    if user.is_mission_admin:
        return True
    elif user.is_branch_pastor:
        return user.branch == branch
    elif user.is_area_pastor and user.area:
        return branch.area == user.area
    elif user.is_district_pastor and user.district:
        return branch.district == user.district
    return False


def generate_member_id(branch):
    """Generate a unique member ID for a branch."""
    import random
    year = date.today().year
    branch_code = branch.code.upper() if branch.code else branch.name[:3].upper()
    
    # Get count of members this year for this branch
    count = Member.objects.filter(
        branch=branch,
        member_id__startswith=f'{branch_code}-{year}'
    ).count()
    
    # Generate unique ID
    return f'{branch_code}-{year}-{count + 1:04d}'


@login_required
def pastor_export_members(request):
    """
    Export members to Excel (for pastors).
    """
    if not request.user.is_pastor:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Get branches this pastor can manage
    managed_branches = _get_managed_branches(request.user)
    
    if not managed_branches:
        messages.warning(request, 'No branches available for export.')
        return redirect('members:pastor_manage')
    
    # Filter by branch if specified
    branch_id = request.GET.get('branch')
    if branch_id:
        managed_branches = managed_branches.filter(id=branch_id)
    
    # Get members
    members = Member.objects.filter(branch__in=managed_branches).select_related('branch', 'branch__district')
    
    # Create Excel file
    import pandas as pd
    from django.http import HttpResponse
    
    data = []
    for member in members:
        data.append({
            'Member ID': member.member_id,
            'First Name': member.first_name,
            'Last Name': member.last_name,
            'Phone': member.phone or '',
            'Email': member.email or '',
            'Address': member.address or '',
            'Date of Birth': member.date_of_birth or '',
            'Gender': member.get_gender_display() or '',
            'Branch': member.branch.name,
            'District': member.branch.district.name,
            'Join Date': member.join_date,
            'Status': member.get_status_display(),
        })
    
    df = pd.DataFrame(data)
    
    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="members_export_{date.today().strftime("%Y%m%d")}.xlsx"'
    
    # Save to response
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Members')
    
    return response


@login_required
def pastor_member_analytics(request):
    """
    Show member analytics (for pastors).
    """
    if not request.user.is_pastor:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Get branches this pastor can manage
    managed_branches = _get_managed_branches(request.user)
    
    if not managed_branches:
        messages.warning(request, 'No branches available for analytics.')
        return redirect('members:pastor_manage')
    
    # Get statistics
    members = Member.objects.filter(branch__in=managed_branches)
    
    # Basic stats
    total_members = members.count()
    active_members = members.filter(status='active').count()
    inactive_members = members.filter(status='inactive').count()
    transferred_members = members.filter(status='transferred').count()
    
    # Gender breakdown
    gender_stats = members.values('gender').annotate(count=Count('id'))
    
    # Age groups
    today = date.today()
    age_groups = {
        '0-18': 0,
        '19-30': 0,
        '31-45': 0,
        '46-60': 0,
        '60+': 0,
    }
    
    for member in members:
        if member.date_of_birth:
            age = today.year - member.date_of_birth.year - ((today.month, today.day) < (member.date_of_birth.month, member.date_of_birth.day))
            if age <= 18:
                age_groups['0-18'] += 1
            elif age <= 30:
                age_groups['19-30'] += 1
            elif age <= 45:
                age_groups['31-45'] += 1
            elif age <= 60:
                age_groups['46-60'] += 1
            else:
                age_groups['60+'] += 1
    
    # Branch breakdown
    branch_stats = members.values('branch__name').annotate(count=Count('id')).order_by('-count')
    
    # Monthly growth (last 6 months)
    monthly_growth = []
    for i in range(6):
        month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = month_start + timedelta(days=32)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        count = members.filter(join_date__range=[month_start, month_end]).count()
        monthly_growth.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })
    
    monthly_growth.reverse()
    
    context = {
        'total_members': total_members,
        'active_members': active_members,
        'inactive_members': inactive_members,
        'transferred_members': transferred_members,
        'gender_stats': gender_stats,
        'age_groups': age_groups,
        'branch_stats': branch_stats,
        'monthly_growth': monthly_growth,
    }
    
    return render(request, 'members/pastor_analytics.html', context)


def _get_managed_branches(user):
    """Helper function to get branches a user can manage."""
    if user.is_mission_admin:
        return Branch.objects.filter(is_active=True)
    elif user.is_branch_pastor and user.branch:
        return Branch.objects.filter(id=user.branch.id)
    elif user.is_area_pastor and user.area:
        return Branch.objects.filter(area=user.area, is_active=True)
    elif user.is_district_pastor and user.district:
        return Branch.objects.filter(district=user.district, is_active=True)
    return Branch.objects.none()
