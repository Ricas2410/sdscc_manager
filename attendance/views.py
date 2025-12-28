"""
Attendance Views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Avg
from datetime import date

from .models import AttendanceSession, AttendanceRecord, ServiceType, VisitorRecord, WeeklyAttendance


@login_required
def weekly_report(request):
    """Weekly attendance report view."""
    if not (request.user.is_any_admin or request.user.is_pastor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Get all weekly attendance records
    weekly_stats = WeeklyAttendance.objects.all().order_by('-week_start_date')
    
    # Get current week
    current_week = WeeklyAttendance.get_current_week()
    
    # Calculate some overall stats
    total_weeks = weekly_stats.count()
    avg_attendance = weekly_stats.aggregate(avg=Avg('attendance_percentage'))['avg'] or 0
    
    context = {
        'weekly_stats': weekly_stats,
        'current_week': current_week,
        'total_weeks': total_weeks,
        'avg_attendance': avg_attendance,
    }
    
    return render(request, 'attendance/weekly_report.html', context)


@login_required
def attendance_list(request):
    """Attendance history with filters."""
    if not (request.user.is_any_admin or request.user.is_pastor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    from core.models import Branch
    
    sessions = AttendanceSession.objects.select_related('branch', 'service_type')
    
    # Branch filter
    if request.user.branch and not request.user.is_mission_admin:
        sessions = sessions.filter(branch=request.user.branch)
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
    
    sessions = sessions.order_by('-date')
    
    # Pagination
    paginator = Paginator(sessions, 25)
    page = request.GET.get('page')
    sessions = paginator.get_page(page)
    
    context = {
        'sessions': sessions,
        'branches': Branch.objects.filter(is_active=True) if request.user.is_mission_admin else None,
        'service_types': ServiceType.objects.filter(is_active=True),
        'today': date.today(),
    }
    return render(request, 'attendance/attendance_list.html', context)


@login_required
def take_attendance(request):
    """Take attendance for a service."""
    from accounts.models import User
    
    if not (request.user.is_any_admin or request.user.is_pastor):
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
        
        # Check for existing session
        service_type = get_object_or_404(ServiceType, pk=service_type_id)
        session, created = AttendanceSession.objects.get_or_create(
            branch=branch,
            service_type=service_type,
            date=attendance_date,
            defaults={
                'total_attendance': 0
            }
        )
        
        if not created:
            # Clear existing records if editing
            session.attendance_records.all().delete()
        
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
        
        session.total_attendance = present_count
        session.update_counts()
        
        messages.success(request, f'Attendance recorded: {present_count} present out of {members.count()} members.')
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
    
    context = {
        'session': session,
        'present': present,
        'absent': absent,
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
    
    visitors = VisitorRecord.objects.select_related('session', 'session__branch', 'invited_by')
    
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
        invited_by_id = request.POST.get('invited_by')
        follow_up_notes = request.POST.get('follow_up_notes', '')
        
        if name:
            visitor = VisitorRecord.objects.create(
                session=session,
                name=name,
                phone=phone,
                email=email,
                visit_date=session.date,
                invited_by_id=invited_by_id if invited_by_id else None,
                follow_up_notes=follow_up_notes
            )
            
            messages.success(request, f'Visitor {visitor.name} added successfully!')
            return redirect('attendance:detail', session.id)
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
