"""
Attendance Views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Sum, Q
from django.contrib.auth import get_user_model
from datetime import date, datetime, timedelta
from django.utils import timezone

from .models import AttendanceSession, AttendanceRecord, ServiceType, VisitorRecord, WeeklyAttendance


@login_required
def weekly_report(request):
    """Weekly attendance report view - Branch-focused with hierarchical filtering."""
    if not (request.user.is_any_admin or request.user.is_pastor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    from core.models import Area, District, Branch
    from datetime import datetime, timedelta
    from django.db.models import Sum, Count, Avg, Q
    from django.utils import timezone
    
    # Get filters
    area_id = request.GET.get('area')
    district_id = request.GET.get('district')
    branch_id = request.GET.get('branch')
    week_offset = int(request.GET.get('week', 0))  # 0 = current week, -1 = last week, etc.
    
    # Calculate week dates
    today = timezone.now().date()
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday) + timedelta(weeks=week_offset)
    week_end = week_start + timedelta(days=6)
    
    # Base queryset for attendance sessions in the selected week
    sessions = AttendanceSession.objects.filter(
        date__gte=week_start,
        date__lte=week_end
    ).select_related('branch', 'branch__district', 'branch__district__area', 'service_type')
    
    # Apply user scope filters
    if request.user.branch and not request.user.is_mission_admin:
        # Branch executives and pastors see only their branch
        sessions = sessions.filter(branch=request.user.branch)
    elif request.user.is_pastor and request.user.pastoral_rank == 'area' and request.user.managed_area:
        # Area pastors see only their area
        sessions = sessions.filter(branch__district__area=request.user.managed_area)
    elif request.user.is_district_executive and request.user.managed_district:
        # District executives see their district
        sessions = sessions.filter(branch__district=request.user.managed_district)
    elif request.user.is_area_executive and request.user.managed_area:
        # Area executives see their area
        sessions = sessions.filter(branch__district__area=request.user.managed_area)
    
    # Apply additional filters from URL
    if area_id:
        sessions = sessions.filter(branch__district__area_id=area_id)
    if district_id:
        sessions = sessions.filter(branch__district_id=district_id)
    if branch_id:
        sessions = sessions.filter(branch_id=branch_id)
    
    # Group by branch for summary
    branch_summaries = []
    branches_queryset = Branch.objects.filter(is_active=True).select_related('district', 'district__area')
    
    # Filter branches for area pastors
    if request.user.is_pastor and request.user.pastoral_rank == 'area' and request.user.managed_area:
        branches_queryset = branches_queryset.filter(district__area=request.user.managed_area)
    
    for branch in branches_queryset:
        branch_sessions = sessions.filter(branch=branch)
        
        if branch_sessions.exists():
            # Calculate branch statistics
            total_attendance = branch_sessions.aggregate(total=Sum('total_attendance'))['total'] or 0
            total_sessions = branch_sessions.count()
            avg_attendance = total_attendance / total_sessions if total_sessions > 0 else 0
            
            # Get member count for this branch
            branch_member_count = get_user_model().objects.filter(
                branch=branch, 
                is_active=True
            ).count()
            
            # Calculate attendance rate
            attendance_rate = (total_attendance / (branch_member_count * total_sessions)) * 100 if branch_member_count > 0 and total_sessions > 0 else 0
            
            # Service type breakdown
            sabbath_attendance = branch_sessions.filter(
                service_type__day='sabbath'
            ).aggregate(total=Sum('total_attendance'))['total'] or 0
            
            midweek_attendance = branch_sessions.filter(
                service_type__day='weekday'
            ).aggregate(total=Sum('total_attendance'))['total'] or 0
            
            special_attendance = branch_sessions.filter(
                service_type__day='any'
            ).aggregate(total=Sum('total_attendance'))['total'] or 0
            
            # Visitor count
            visitors_count = branch_sessions.aggregate(total=Sum('visitors_count'))['total'] or 0
            
            branch_summaries.append({
                'branch': branch,
                'total_attendance': total_attendance,
                'total_sessions': total_sessions,
                'avg_attendance': round(avg_attendance, 1),
                'attendance_rate': round(attendance_rate, 1),
                'member_count': branch_member_count,
                'sabbath_attendance': sabbath_attendance,
                'midweek_attendance': midweek_attendance,
                'special_attendance': special_attendance,
                'visitors_count': visitors_count,
            })
    
    # Sort by attendance rate (descending)
    branch_summaries.sort(key=lambda x: x['attendance_rate'], reverse=True)
    
    # Calculate overall statistics
    overall_total_attendance = sum(b['total_attendance'] for b in branch_summaries)
    overall_total_sessions = sum(b['total_sessions'] for b in branch_summaries)
    overall_total_members = sum(b['member_count'] for b in branch_summaries)
    overall_visitors = sum(b['visitors_count'] for b in branch_summaries)
    
    overall_avg_attendance = overall_total_attendance / overall_total_sessions if overall_total_sessions > 0 else 0
    overall_attendance_rate = (overall_total_attendance / (overall_total_members * overall_total_sessions)) * 100 if overall_total_members > 0 and overall_total_sessions > 0 else 0
    
    # Filter options for hierarchical dropdowns
    areas = Area.objects.filter(is_active=True).order_by('name')
    districts = District.objects.filter(is_active=True).order_by('name')
    branches = Branch.objects.filter(is_active=True).order_by('name')
    
    # Apply filters to dropdown options
    if area_id:
        districts = districts.filter(area_id=area_id)
        branches = branches.filter(district__area_id=area_id)
    elif district_id:
        branches = branches.filter(district_id=district_id)
    
    context = {
        'branch_summaries': branch_summaries,
        'week_start': week_start,
        'week_end': week_end,
        'week_offset': week_offset,
        'current_week': week_offset == 0,
        
        # Overall statistics
        'overall_total_attendance': overall_total_attendance,
        'overall_total_sessions': overall_total_sessions,
        'overall_avg_attendance': round(overall_avg_attendance, 1),
        'overall_attendance_rate': round(overall_attendance_rate, 1),
        'overall_total_members': overall_total_members,
        'overall_visitors': overall_visitors,
        'total_branches': len(branch_summaries),
        
        # Filter options
        'areas': areas,
        'districts': districts,
        'branches': branches,
        'selected_area': area_id,
        'selected_district': district_id,
        'selected_branch': branch_id,
    }
    
    return render(request, 'attendance/weekly_report.html', context)


@login_required
def branch_weekly_detail(request, branch_id, week_start):
    """Detailed attendance for a specific branch in a specific week."""
    from core.models import Branch
    from datetime import datetime, timedelta
    
    # Parse week start date and calculate week end
    week_start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
    week_end_date = week_start_date + timedelta(days=6)
    
    # Get branch
    branch = get_object_or_404(Branch, id=branch_id)
    
    # Check permissions
    if not (request.user.is_mission_admin or 
            (request.user.branch == branch) or
            (request.user.is_district_executive and request.user.managed_district == branch.district) or
            (request.user.is_area_executive and request.user.managed_area == branch.district.area)):
        messages.error(request, 'Access denied.')
        return redirect('attendance:weekly_report')
    
    # Get attendance sessions for this branch and week
    sessions = AttendanceSession.objects.filter(
        branch=branch,
        date__gte=week_start_date,
        date__lte=week_end_date
    ).select_related('service_type').order_by('date', 'start_time')
    
    # Get individual attendance records
    records = AttendanceRecord.objects.filter(
        session__branch=branch,
        session__date__gte=week_start_date,
        session__date__lte=week_end_date
    ).select_related('session', 'session__service_type', 'member').order_by('-session__date', 'member__first_name')
    
    # Calculate statistics
    total_sessions = sessions.count()
    total_attendance = sessions.aggregate(total=Sum('total_attendance'))['total'] or 0
    total_visitors = sessions.aggregate(total=Sum('visitors_count'))['total'] or 0
    
    # Get member count
    branch_member_count = get_user_model().objects.filter(
        branch=branch, 
        is_active=True
    ).count()
    
    # Calculate attendance rate
    attendance_rate = (total_attendance / (branch_member_count * total_sessions)) * 100 if branch_member_count > 0 and total_sessions > 0 else 0
    
    # Group records by member for summary
    member_stats = {}
    for record in records:
        member_id = record.member.id
        if member_id not in member_stats:
            member_stats[member_id] = {
                'member': record.member,
                'present': 0,
                'absent': 0,
                'excused': 0,
                'late': 0,
                'total': 0,
            }
        
        member_stats[member_id][record.status] += 1
        member_stats[member_id]['total'] += 1
    
    # Calculate attendance rates for each member
    for member_id, stats in member_stats.items():
        if stats['total'] > 0:
            stats['attendance_rate'] = (stats['present'] / stats['total']) * 100
        else:
            stats['attendance_rate'] = 0
    
    # Sort by attendance rate
    sorted_members = sorted(member_stats.values(), key=lambda x: x['attendance_rate'], reverse=True)
    
    context = {
        'branch': branch,
        'week_start': week_start_date,
        'week_end': week_end_date,
        'sessions': sessions,
        'member_stats': sorted_members,
        
        # Statistics
        'total_sessions': total_sessions,
        'total_attendance': total_attendance,
        'total_visitors': total_visitors,
        'branch_member_count': branch_member_count,
        'attendance_rate': round(attendance_rate, 1),
        'avg_per_service': round(total_attendance / total_sessions, 1) if total_sessions > 0 else 0,
    }
    
    return render(request, 'attendance/branch_weekly_detail.html', context)


@login_required
def attendance_list(request):
    """Attendance history with filters."""
    if not (request.user.is_any_admin or request.user.is_pastor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    from core.models import Branch
    
    sessions = AttendanceSession.objects.select_related('branch', 'service_type').prefetch_related('visitor_records')
    
    # Branch filter
    if request.user.branch and not request.user.is_mission_admin:
        sessions = sessions.filter(branch=request.user.branch)
    elif request.user.is_pastor and request.user.pastoral_rank == 'area' and request.user.managed_area:
        # Area pastors see only sessions in their area
        sessions = sessions.filter(branch__district__area=request.user.managed_area)
    elif request.user.is_area_executive and request.user.managed_area:
        # Area executives see only sessions in their area
        sessions = sessions.filter(branch__district__area=request.user.managed_area)
    elif request.user.is_district_executive and request.user.managed_district:
        # District executives see only sessions in their district
        sessions = sessions.filter(branch__district=request.user.managed_district)
    else:
        branch_filter = request.GET.get('branch')
        if branch_filter:
            sessions = sessions.filter(branch_id=branch_filter)
    
    # Date filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        sessions = sessions.filter(date__gte=date_from)
    if date_to:
        sessions = sessions.filter(date__lte=date_to)
    
    # Service type filter
    service_type = request.GET.get('service_type')
    if service_type:
        sessions = sessions.filter(service_type_id=service_type)
    
    # Sorting
    sort_by = request.GET.get('sort', '-date')
    if sort_by in ['date', '-date', 'branch__name', '-branch__name', 'total_attendance', '-total_attendance']:
        sessions = sessions.order_by(sort_by)
    else:
        sessions = sessions.order_by('-date')
    
    # Pagination
    paginator = Paginator(sessions, 25)
    page = request.GET.get('page')
    sessions = paginator.get_page(page)
    
    # Get branches for filter dropdown based on user role
    if request.user.is_mission_admin:
        branches = Branch.objects.filter(is_active=True)
    elif request.user.is_area_executive:
        branches = Branch.objects.filter(district__area=request.user.managed_area, is_active=True)
    elif request.user.is_district_executive:
        branches = Branch.objects.filter(district=request.user.managed_district, is_active=True)
    else:
        branches = None
    
    context = {
        'sessions': sessions,
        'branches': branches,
        'service_types': ServiceType.objects.filter(is_active=True),
        'today': date.today(),
        'sort': sort_by,
    }
    return render(request, 'attendance/attendance_list.html', context)


@login_required
def take_attendance(request):
    """Take attendance for a service."""
    from accounts.models import User
    
    if not (request.user.is_any_admin or (request.user.is_pastor and request.user.pastoral_rank != 'area')):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    branch = request.user.branch
    if not branch:
        messages.error(request, 'You must be assigned to a branch to take attendance.')
        return redirect('attendance:list')
    
    service_types = ServiceType.objects.filter(is_active=True)
    members = User.objects.filter(branch=branch, is_active=True).order_by('first_name', 'last_name')
    
    if request.method == 'POST':
        service_type_id = request.POST.get('service_type')
        attendance_date = request.POST.get('date')
        present_members = request.POST.getlist('present')
        session_notes = request.POST.get('session_notes', '')
        
        # Check for existing session
        service_type = get_object_or_404(ServiceType, pk=service_type_id)
        session, created = AttendanceSession.objects.get_or_create(
            branch=branch,
            service_type=service_type,
            date=attendance_date,
            defaults={
                'total_attendance': 0,
                'notes': session_notes
            }
        )
        
        if not created:
            # Clear existing records if editing
            session.attendance_records.all().delete()
            session.visitor_records.all().delete()
        
        # Create attendance records
        present_count = 0
        for member in members:
            status = 'present' if str(member.id) in present_members else 'absent'
            AttendanceRecord.objects.create(
                session=session,
                member=member,
                status=status
            )
            if status == 'present':
                present_count += 1
        
        # Process visitors added during attendance
        visitor_count = 0
        for key, value in request.POST.items():
            if key.startswith('visitor_name_'):
                visitor_id = key.split('_')[-1]
                name = value.strip()
                
                if name:  # Only create visitor if name is provided
                    phone = request.POST.get(f'visitor_phone_{visitor_id}', '').strip()
                    gender = request.POST.get(f'visitor_gender_{visitor_id}', 'M')
                    notes = request.POST.get(f'visitor_notes_{visitor_id}', '').strip()
                    
                    VisitorRecord.objects.create(
                        session=session,
                        name=name,
                        phone=phone,
                        visit_date=session.date,
                        notes=f"Gender: {gender}. {notes}" if notes else f"Gender: {gender}",
                        status='new',
                        is_first_time=True,
                        visit_count=1
                    )
                    visitor_count += 1
        
        # Process children count
        children_count = int(request.POST.get('children_count', 0))
        boys_count = int(request.POST.get('boys_count', 0))
        girls_count = int(request.POST.get('girls_count', 0))
        
        session.total_attendance = present_count
        session.male_count = session.attendance_records.filter(status='present', member__gender='M').count()
        session.female_count = session.attendance_records.filter(status='present', member__gender='F').count()
        session.children_count = children_count
        session.update_counts()
        
        message_parts = [f'Attendance recorded: {present_count} present out of {members.count()} members']
        if visitor_count > 0:
            message_parts.append(f'{visitor_count} visitor{"s" if visitor_count != 1 else ""}')
        if children_count > 0:
            message_parts.append(f'{children_count} child{"ren" if children_count != 1 else ""}')
        
        messages.success(request, '. '.join(message_parts) + '.')
        return redirect('attendance:session_detail', session_id=session.id)
    
    context = {
        'branch': branch,
        'members': members,
        'service_types': service_types,
        'today': date.today(),
    }
    return render(request, 'attendance/take_attendance.html', context)


@login_required
def session_detail(request, session_id):
    """View attendance session detail with present/absent lists."""
    session = get_object_or_404(AttendanceSession, pk=session_id)
    
    # Check access
    if not request.user.is_mission_admin and request.user.branch != session.branch:
        messages.error(request, 'Access denied.')
        return redirect('attendance:list')
    
    records = session.attendance_records.select_related('member').order_by('member__first_name')
    present = records.filter(status='present')
    absent = records.filter(status='absent')
    visitors = session.visitor_records.all().order_by('-created_at')
    
    context = {
        'session': session,
        'present': present,
        'absent': absent,
        'visitors': visitors,
        'total': records.count(),
    }
    return render(request, 'attendance/session_detail.html', context)


@login_required
def member_attendance(request, user_id):
    """View a member's attendance history."""
    from accounts.models import User
    
    member = get_object_or_404(User, pk=user_id)
    
    # Check access
    if not request.user.is_mission_admin and request.user.branch != member.branch:
        messages.error(request, 'Access denied.')
        return redirect('attendance:list')
    
    records = AttendanceRecord.objects.filter(member=member).select_related('session', 'session__service_type').order_by('-session__date')
    
    total_sessions = records.count()
    present_count = records.filter(status='present').count()
    absent_count = records.filter(status='absent').count()
    attendance_percentage = (present_count / total_sessions * 100) if total_sessions > 0 else 0
    
    context = {
        'member': member,
        'records': records[:50],
        'total_sessions': total_sessions,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_percentage': attendance_percentage,
    }
    return render(request, 'attendance/member_attendance.html', context)


@login_required
def my_attendance(request):
    """Member view - shows only their own attendance history."""
    from django.utils import timezone
    
    user = request.user
    current_year = timezone.now().year
    
    # Get only the current user's attendance records
    records = AttendanceRecord.objects.filter(
        member=user
    ).select_related('session', 'session__service_type', 'session__branch').order_by('-session__date')
    
    # Calculate statistics
    total_records = records.count()
    present_count = records.filter(status='present').count()
    absent_count = records.filter(status='absent').count()
    late_count = records.filter(status='late').count()
    
    # This year stats
    year_records = records.filter(session__date__year=current_year)
    year_total = year_records.count()
    year_present = year_records.filter(status='present').count()
    attendance_rate = (year_present / year_total * 100) if year_total > 0 else 0
    
    # By service type
    by_service_type = year_records.filter(status='present').values(
        'session__service_type__name'
    ).annotate(count=Count('id')).order_by('-count')
    
    # Paginate
    paginator = Paginator(records, 25)
    page = request.GET.get('page')
    records = paginator.get_page(page)
    
    context = {
        'records': records,
        'total_records': total_records,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'year_total': year_total,
        'year_present': year_present,
        'attendance_rate': attendance_rate,
        'by_service_type': by_service_type,
        'current_year': current_year,
    }
    
    return render(request, 'attendance/my_attendance.html', context)


@login_required
def attendance_tracking(request):
    """Admin view for tracking member attendance across branches."""
    from accounts.models import User
    from core.models import Area, District, Branch
    from django.db.models import Count, Avg, Q, Avg
    
    if not (request.user.is_any_admin or request.user.is_auditor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Get filters
    area_id = request.GET.get('area')
    district_id = request.GET.get('district')
    branch_id = request.GET.get('branch')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    attendance_status = request.GET.get('status', 'all')  # all, good, poor
    
    # Base queryset for members
    members = User.objects.filter(role='member', is_active=True).select_related('branch__district__area')
    
    # Apply hierarchical filters
    districts = District.objects.filter(is_active=True)
    branches = Branch.objects.filter(is_active=True)
    
    if area_id:
        members = members.filter(branch__district__area_id=area_id)
        districts = districts.filter(area_id=area_id)
        branches = branches.filter(district__area_id=area_id)
    
    if district_id:
        members = members.filter(branch__district_id=district_id)
        branches = branches.filter(district_id=district_id)
    
    if branch_id:
        members = members.filter(branch_id=branch_id)
    
    # Get attendance sessions for date range
    sessions_query = AttendanceSession.objects.all()
    if from_date:
        sessions_query = sessions_query.filter(date__gte=from_date)
    if to_date:
        sessions_query = sessions_query.filter(date__lte=to_date)
    
    # Annotate members with attendance stats
    members_with_stats = []
    for member in members:
        # Get member's attendance records
        records = AttendanceRecord.objects.filter(
            member=member,
            session__in=sessions_query
        )
        
        total_sessions = records.count()
        present_count = records.filter(status='present').count()
        absent_count = records.filter(status='absent').count()
        attendance_rate = (present_count / total_sessions * 100) if total_sessions > 0 else 0
        
        # Determine status
        if attendance_rate >= 75:
            status = 'good'
        elif attendance_rate >= 50:
            status = 'average'
        else:
            status = 'poor'
        
        member_data = {
            'member': member,
            'total_sessions': total_sessions,
            'present_count': present_count,
            'absent_count': absent_count,
            'attendance_rate': attendance_rate,
            'status': status,
        }
        
        # Filter by attendance status
        if attendance_status == 'good' and attendance_rate >= 75:
            members_with_stats.append(member_data)
        elif attendance_status == 'poor' and attendance_rate < 50:
            members_with_stats.append(member_data)
        elif attendance_status == 'all':
            members_with_stats.append(member_data)
    
    # Sort by attendance rate
    members_with_stats.sort(key=lambda x: x['attendance_rate'], reverse=False)
    
    # Branch-level headcount statistics
    branch_stats = []
    for branch in branches:
        branch_sessions = sessions_query.filter(branch=branch)
        total_headcount = branch_sessions.aggregate(total=Count('id'))['total'] or 0
        avg_attendance = branch_sessions.aggregate(avg=Avg('total_attendance'))['avg'] or 0
        
        branch_stats.append({
            'branch': branch,
            'total_sessions': total_headcount,
            'avg_attendance': round(avg_attendance, 1),
        })
    
    # Paginate members
    paginator = Paginator(members_with_stats, 50)
    page = request.GET.get('page')
    members_page = paginator.get_page(page)
    
    context = {
        'members': members_page,
        'branch_stats': branch_stats,
        'areas': Area.objects.filter(is_active=True).order_by('name'),
        'districts': districts.order_by('name'),
        'branches': branches.order_by('name'),
        'selected_area': area_id,
        'selected_district': district_id,
        'selected_branch': branch_id,
        'from_date': from_date,
        'to_date': to_date,
        'attendance_status': attendance_status,
    }
    
    return render(request, 'attendance/attendance_tracking.html', context)


@login_required
def visitor_list(request):
    """List all visitors with filters."""
    if not (request.user.is_any_admin or request.user.is_pastor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    from core.models import Branch
    
    visitors = VisitorRecord.objects.select_related('session', 'session__branch', 'session__service_type', 'invited_by')
    
    # Branch filter
    if request.user.branch and not request.user.is_mission_admin:
        visitors = visitors.filter(session__branch=request.user.branch)
    else:
        branch_filter = request.GET.get('branch')
        if branch_filter:
            visitors = visitors.filter(session__branch_id=branch_filter)
    
    # Date filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        visitors = visitors.filter(visit_date__gte=date_from)
    if date_to:
        visitors = visitors.filter(visit_date__lte=date_to)
    
    # Status filter
    status = request.GET.get('status')
    if status:
        visitors = visitors.filter(status=status)
    
    visitors = visitors.order_by('-visit_date')
    
    # Calculate statistics
    total_visitors = VisitorRecord.objects.count()
    new_visitors = VisitorRecord.objects.filter(status='new').count()
    returning_visitors = VisitorRecord.objects.filter(status='returning').count()
    converted_visitors = VisitorRecord.objects.filter(status='joined').count()
    followup_due = VisitorRecord.objects.filter(follow_up_needed=True, follow_up_date__lte=date.today()).count()
    
    # Pagination
    paginator = Paginator(visitors, 25)
    page = request.GET.get('page')
    visitors_page = paginator.get_page(page)
    
    context = {
        'visitors': visitors_page,
        'branches': Branch.objects.filter(is_active=True).order_by('name'),
        'selected_branch': request.GET.get('branch'),
        'from_date': date_from,
        'to_date': date_to,
        'selected_status': status,
        'total_visitors': total_visitors,
        'new_visitors': new_visitors,
        'returning_visitors': returning_visitors,
        'converted_visitors': converted_visitors,
        'followup_due': followup_due,
    }
    
    return render(request, 'attendance/visitor_list.html', context)


@login_required
def add_visitor(request, session_id):
    """Add a visitor to an attendance session."""
    session = get_object_or_404(AttendanceSession, id=session_id)
    
    # Check permissions
    if not (request.user.is_any_admin or 
            (request.user.is_pastor and request.user.branch == session.branch) or
            (request.user.is_branch_executive and request.user.branch == session.branch)):
        messages.error(request, 'Access denied.')
        return redirect('attendance:detail', session.id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')
        invited_by_id = request.POST.get('invited_by')
        status = request.POST.get('status', 'new')
        visit_count = request.POST.get('visit_count', '1')
        interested_in_membership = request.POST.get('interested_in_membership') == 'true'
        follow_up_needed = request.POST.get('follow_up_needed') == 'true'
        follow_up_date = request.POST.get('follow_up_date', '')
        follow_up_assigned_to_id = request.POST.get('follow_up_assigned_to')
        follow_up_notes = request.POST.get('follow_up_notes', '')
        notes = request.POST.get('notes', '')
        
        if name:
            visitor = VisitorRecord.objects.create(
                session=session,
                name=name,
                phone=phone,
                email=email,
                address=address,
                visit_date=session.date,
                invited_by_id=invited_by_id if invited_by_id else None,
                status=status,
                visit_count=int(visit_count) if visit_count else 1,
                interested_in_membership=interested_in_membership,
                follow_up_needed=follow_up_needed,
                follow_up_date=follow_up_date if follow_up_date else None,
                follow_up_assigned_to_id=follow_up_assigned_to_id if follow_up_assigned_to_id else None,
                follow_up_notes=follow_up_notes,
                notes=notes,
                is_first_time=(status == 'new')
            )
            
            messages.success(request, f'Visitor {visitor.name} added successfully!')
            return redirect('attendance:session_detail', session.id)
        else:
            messages.error(request, 'Please provide visitor name.')
    
    # Get members for invitation dropdown
    from accounts.models import User
    members = User.objects.filter(branch=session.branch, is_active=True).order_by('first_name', 'last_name')
    
    context = {
        'session': session,
        'members': members,
    }
    
    return render(request, 'attendance/add_visitor.html', context)


@login_required
def visitor_detail(request, visitor_id):
    """View visitor details."""
    visitor = get_object_or_404(VisitorRecord, id=visitor_id)
    
    # Check permissions
    if not (request.user.is_any_admin or 
            (request.user.is_pastor and request.user.branch == visitor.session.branch) or
            (request.user.is_branch_executive and request.user.branch == visitor.session.branch)):
        messages.error(request, 'Access denied.')
        return redirect('attendance:visitors')
    
    context = {
        'visitor': visitor,
    }
    
    return render(request, 'attendance/visitor_detail.html', context)
