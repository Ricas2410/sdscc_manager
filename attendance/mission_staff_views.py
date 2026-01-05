"""
Mission Staff Attendance Views
Simple, session-based attendance tracking for mission-level staff
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import date, timedelta, datetime

from .models import MissionStaffAttendance, MissionStaffAttendanceRecord
from accounts.models import User


@login_required
def mission_staff_attendance_register(request):
    """
    Mission Staff Attendance Register
    Auto-loads all mission staff for easy attendance marking
    """
    # Only mission admin can take attendance
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied. Only Mission Admin can take staff attendance.')
        return redirect('core:dashboard')
    
    # Get or create attendance for today
    today = date.today()
    attendance, created = MissionStaffAttendance.objects.get_or_create(
        date=today,
        defaults={
            'title': 'Mission Staff Meeting',
            'created_by': request.user
        }
    )
    
    # Check if attendance can be edited
    can_edit = attendance.can_be_edited()
    
    # Get all mission staff (pastors, executives, admin staff)
    mission_staff = User.objects.filter(
        Q(role='mission_admin') |
        Q(role='area_executive') |
        Q(role='district_executive') |
        Q(role='pastor') |
        Q(role='staff') |
        Q(is_superuser=True)
    ).filter(is_active=True).order_by('first_name', 'last_name')
    
    # Get existing records
    existing_records = {
        record.staff_member_id: record 
        for record in attendance.records.all()
    }
    
    # Prepare staff list with attendance status
    staff_list = []
    for staff in mission_staff:
        record = existing_records.get(staff.id)
        staff_list.append({
            'staff': staff,
            'record': record,
            'status': record.status if record else 'present',
            'notes': record.notes if record else ''
        })
    
    context = {
        'attendance': attendance,
        'staff_list': staff_list,
        'can_edit': can_edit,
        'is_locked': attendance.is_locked,
        'created': created,
        'today_date': date.today().strftime('%Y-%m-%d'),
    }
    
    return render(request, 'attendance/mission_staff_attendance_register.html', context)


@login_required
@require_POST
def save_mission_staff_attendance(request):
    """Save attendance for mission staff"""
    if not request.user.is_mission_admin:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    attendance_id = request.POST.get('attendance_id')
    attendance = get_object_or_404(MissionStaffAttendance, id=attendance_id)
    
    # Check if attendance can be edited
    if not attendance.can_be_edited():
        return JsonResponse({'error': 'Attendance is locked or past 24-hour window'}, status=400)
    
    # Update attendance title if provided
    title = request.POST.get('title', 'Mission Staff Meeting')
    attendance.title = title
    attendance.created_by = request.user
    attendance.save()
    
    # Get staff attendance data
    staff_data = request.POST.getlist('staff_attendance', [])
    
    # Save each staff member's attendance
    for data in staff_data:
        parts = data.split('|')
        if len(parts) >= 2:
            staff_id = parts[0]
            status = parts[1]
            notes = parts[2] if len(parts) > 2 else ''
            
            try:
                staff = User.objects.get(id=staff_id)
                
                # Get or create record
                record, created = MissionStaffAttendanceRecord.objects.get_or_create(
                    attendance=attendance,
                    staff_member=staff,
                    defaults={'status': status}
                )
                
                # Update record
                record.status = status
                record.notes = notes
                record.marked_by = request.user
                record.marked_at = timezone.now()
                record.save()
                
            except User.DoesNotExist:
                continue
    
    # Update attendance counts
    attendance.total_staff = len(staff_data)
    attendance.update_counts()
    
    messages.success(request, 'Staff attendance saved successfully!')
    return JsonResponse({'success': True})


@login_required
def mission_staff_attendance_history(request):
    """View history of mission staff attendance"""
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Get filter parameters
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    # Get attendances
    attendances = MissionStaffAttendance.objects.all().order_by('-date')
    
    # Apply filters
    if from_date:
        attendances = attendances.filter(date__gte=from_date)
    if to_date:
        attendances = attendances.filter(date__lte=to_date)
    
    # Limit to last 30 days if no filters
    if not from_date and not to_date:
        attendances = attendances.filter(date__gte=date.today() - timedelta(days=30))
    
    # Calculate summary statistics
    total_present = attendances.aggregate(total=Sum('present_count'))['total'] or 0
    total_absent = attendances.aggregate(total=Sum('absent_count'))['total'] or 0
    avg_attendance = total_present // attendances.count() if attendances.count() > 0 else 0
    overall_rate = (total_present * 100 // (total_present + total_absent)) if (total_present + total_absent) > 0 else 0
    
    context = {
        'attendances': attendances,
        'from_date': from_date,
        'to_date': to_date,
        'total_present': total_present,
        'total_absent': total_absent,
        'avg_attendance': avg_attendance,
        'overall_rate': overall_rate,
    }
    
    return render(request, 'attendance/mission_staff_attendance_history.html', context)


@login_required
def my_meetings(request):
    """
    'My Meetings' - Staff view of their attendance history
    Read-only, filtered for the logged-in user
    """
    # Get all attendance records for this staff member
    staff_records = MissionStaffAttendanceRecord.objects.filter(
        staff_member=request.user
    ).select_related('attendance').order_by('-attendance__date')
    
    # Calculate statistics
    total_meetings = staff_records.count()
    present_count = staff_records.filter(status='present').count()
    absent_count = staff_records.filter(status='absent').count()
    excused_count = staff_records.filter(status='excused').count()
    
    attendance_percentage = 0
    if total_meetings > 0:
        attendance_percentage = (present_count / total_meetings) * 100
    
    # Get recent attendance (last 10)
    recent_attendance = staff_records[:10]
    
    # Monthly attendance for the current year
    current_year = date.today().year
    monthly_stats = {}
    for month in range(1, 13):
        month_records = staff_records.filter(
            attendance__date__year=current_year,
            attendance__date__month=month
        )
        monthly_stats[month] = {
            'name': date(current_year, month, 1).strftime('%B'),
            'total': month_records.count(),
            'present': month_records.filter(status='present').count(),
            'percentage': 0
        }
        if month_records.count() > 0:
            monthly_stats[month]['percentage'] = (
                month_records.filter(status='present').count() / month_records.count() * 100
            )
    
    context = {
        'staff_records': staff_records,
        'recent_attendance': recent_attendance,
        'total_meetings': total_meetings,
        'present_count': present_count,
        'absent_count': absent_count,
        'excused_count': excused_count,
        'attendance_percentage': round(attendance_percentage, 1),
        'monthly_stats': monthly_stats,
        'current_year': current_year,
    }
    
    return render(request, 'attendance/my_meetings.html', context)


@login_required
@require_POST
def override_attendance_lock(request, attendance_id):
    """
    Override attendance lock (Mission Admin only)
    Requires audit logging
    """
    if not request.user.is_mission_admin:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    attendance = get_object_or_404(MissionStaffAttendance, id=attendance_id)
    
    # Check if already locked
    if not attendance.is_locked:
        return JsonResponse({'error': 'Attendance is not locked'}, status=400)
    
    # Get reason for override
    reason = request.POST.get('reason', '')
    if not reason:
        return JsonResponse({'error': 'Reason is required for override'}, status=400)
    
    # Unlock attendance
    attendance.is_locked = False
    attendance.locked_at = None
    attendance.locked_by = None
    attendance.save()
    
    # Log the override (you can implement proper audit logging here)
    messages.warning(request, f'Attendance lock overridden. Reason: {reason}')
    
    return JsonResponse({'success': True})


@login_required
def mission_staff_attendance_detail(request, attendance_id):
    """View details of a specific mission staff attendance"""
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    attendance = get_object_or_404(MissionStaffAttendance, id=attendance_id)
    records = attendance.records.select_related('staff_member').order_by('staff_member__first_name')
    
    context = {
        'attendance': attendance,
        'records': records,
        'can_edit': attendance.can_be_edited(),
    }
    
    return render(request, 'attendance/mission_staff_attendance_detail.html', context)


@login_required
def mission_staff_attendance_summary(request):
    """
    Admin attendance summary with statistics and trends
    """
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Get date range from filters or default to last 30 days
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    if not from_date:
        from_date = (date.today() - timedelta(days=30)).isoformat()
    if not to_date:
        to_date = date.today().isoformat()
    
    # Get attendances in date range
    attendances = MissionStaffAttendance.objects.filter(
        date__gte=from_date,
        date__lte=to_date
    ).order_by('-date')
    
    # Calculate overall statistics
    total_sessions = attendances.count()
    total_staff_attended = attendances.aggregate(
        total=Sum('present_count')
    )['total'] or 0
    total_staff_absent = attendances.aggregate(
        total=Sum('absent_count')
    )['total'] or 0
    
    # Get individual staff statistics
    staff_stats = {}
    all_records = MissionStaffAttendanceRecord.objects.filter(
        attendance__date__gte=from_date,
        attendance__date__lte=to_date
    ).select_related('staff_member')
    
    for record in all_records:
        staff_id = record.staff_member_id
        if staff_id not in staff_stats:
            staff_stats[staff_id] = {
                'staff': record.staff_member,
                'total': 0,
                'present': 0,
                'absent': 0,
                'excused': 0
            }
        
        staff_stats[staff_id]['total'] += 1
        if record.status == 'present':
            staff_stats[staff_id]['present'] += 1
        elif record.status == 'absent':
            staff_stats[staff_id]['absent'] += 1
        elif record.status == 'excused':
            staff_stats[staff_id]['excused'] += 1
    
    # Calculate attendance percentage for each staff
    for stats in staff_stats.values():
        if stats['total'] > 0:
            stats['percentage'] = (stats['present'] / stats['total']) * 100
        else:
            stats['percentage'] = 0
    
    # Sort by attendance percentage (lowest first)
    sorted_staff_stats = sorted(staff_stats.values(), key=lambda x: x['percentage'])
    
    # Daily attendance trend for chart
    daily_data = []
    for attendance in attendances.order_by('date'):
        daily_data.append({
            'date': attendance.date.isoformat(),
            'present': attendance.present_count,
            'absent': attendance.absent_count,
            'percentage': (attendance.present_count / attendance.total_staff * 100) if attendance.total_staff > 0 else 0
        })
    
    context = {
        'attendances': attendances,
        'total_sessions': total_sessions,
        'total_staff_attended': total_staff_attended,
        'total_staff_absent': total_staff_absent,
        'staff_stats': sorted_staff_stats[:10],  # Show bottom 10 performers
        'daily_data': json.dumps(daily_data, cls=DjangoJSONEncoder),
        'from_date': from_date,
        'to_date': to_date,
    }
    
    return render(request, 'attendance/mission_staff_attendance_summary.html', context)
