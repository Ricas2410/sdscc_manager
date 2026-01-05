"""
Attendance Models - Track church service attendance
Supports Sabbath (Saturday), midweek, and special services
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from core.models import TimeStampedModel


class ServiceType(models.Model):
    """Define types of church services."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    class ServiceDay(models.TextChoices):
        SABBATH = 'sabbath', 'Sabbath (Saturday)'
        SUNDAY = 'sunday', 'Sunday'
        WEEKDAY = 'weekday', 'Weekday'
        ANY = 'any', 'Any Day'
    
    day = models.CharField(max_length=20, choices=ServiceDay.choices, default=ServiceDay.SABBATH)
    default_start_time = models.TimeField(null=True, blank=True)
    default_end_time = models.TimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Service Type'
        verbose_name_plural = 'Service Types'
    
    def __str__(self):
        return self.name


class AttendanceSession(TimeStampedModel):
    """A specific service session for attendance tracking."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    branch = models.ForeignKey('core.Branch', on_delete=models.PROTECT, related_name='attendance_sessions')
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT, related_name='sessions')
    
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    
    # Counts
    total_attendance = models.IntegerField(default=0)
    male_count = models.IntegerField(default=0)
    female_count = models.IntegerField(default=0)
    children_count = models.IntegerField(default=0)
    visitors_count = models.IntegerField(default=0)
    
    # Service details
    preacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='preached_sessions'
    )
    sermon_topic = models.CharField(max_length=300, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date', '-start_time']
        unique_together = ['branch', 'service_type', 'date']
        verbose_name = 'Attendance Session'
        verbose_name_plural = 'Attendance Sessions'
    
    def __str__(self):
        return f"{self.branch.name} - {self.service_type.name} - {self.date}"
    
    def update_counts(self):
        """Update total counts from individual records."""
        records = self.attendance_records.all()
        self.total_attendance = records.filter(status='present').count()
        self.male_count = records.filter(status='present', member__gender='M').count()
        self.female_count = records.filter(status='present', member__gender='F').count()
        self.save()


class AttendanceRecord(TimeStampedModel):
    """Individual member attendance record."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='attendance_records')
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendance_records')
    
    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'
        EXCUSED = 'excused', 'Excused'
        LATE = 'late', 'Late'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT)
    
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    
    # QR code check-in (future feature)
    checked_in_via = models.CharField(max_length=50, blank=True, default='manual')
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-session__date']
        unique_together = ['session', 'member']
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.session.date} - {self.get_status_display()}"


class VisitorRecord(TimeStampedModel):
    """Track visitors who attend services."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='visitor_records')
    
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='attendance_invited_visitors'
    )
    
    # Follow-up
    is_first_time = models.BooleanField(default=True)
    visit_count = models.IntegerField(default=1)
    follow_up_needed = models.BooleanField(default=True)
    follow_up_notes = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    interested_in_membership = models.BooleanField(default=False)
    follow_up_assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='visitor_followups'
    )
    
    # Visit details
    visit_date = models.DateField()
    
    class Status(models.TextChoices):
        NEW = 'new', 'First Time Visitor'
        RETURNING = 'returning', 'Returning Visitor'
        JOINED = 'joined', 'Became Member'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-visit_date', 'name']
        verbose_name = 'Visitor Record'
        verbose_name_plural = 'Visitor Records'
    
    def __str__(self):
        return f"{self.name} - {self.visit_date}"
    
    def save(self, *args, **kwargs):
        # Update session visitor count
        super().save(*args, **kwargs)
        self.session.visitors_count = self.session.visitor_records.count()
        self.session.save()


class WeeklyAttendance(TimeStampedModel):
    """Track weekly attendance statistics across all branches."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    week_start_date = models.DateField(help_text="Start date of the week (Monday)")
    week_end_date = models.DateField(help_text="End date of the week (Sunday)")
    
    # Attendance counts
    total_attendees = models.IntegerField(default=0, help_text="Total unique attendees for the week")
    total_members = models.IntegerField(default=0, help_text="Total active members in the system")
    
    # Percentages
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, 
                                               help_text="Percentage of members who attended")
    
    # Breakdown by service type
    sabbath_attendance = models.IntegerField(default=0)
    midweek_attendance = models.IntegerField(default=0)
    special_service_attendance = models.IntegerField(default=0)
    
    # Additional stats
    first_time_visitors = models.IntegerField(default=0)
    average_per_service = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-week_start_date']
        unique_together = ['week_start_date', 'week_end_date']
        verbose_name = 'Weekly Attendance'
        verbose_name_plural = 'Weekly Attendances'
    
    def __str__(self):
        return f"Week of {self.week_start_date} - {self.attendance_percentage}%"
    
    def save(self, *args, **kwargs):
        # Calculate attendance percentage if not set
        if self.total_members > 0:
            self.attendance_percentage = (self.total_attendees / self.total_members) * 100
        
        # Calculate average per service
        total_services = 0
        if self.sabbath_attendance > 0:
            total_services += 1
        if self.midweek_attendance > 0:
            total_services += 1
        if self.special_service_attendance > 0:
            total_services += 1
        
        if total_services > 0:
            self.average_per_service = self.total_attendees / total_services
        
        super().save(*args, **kwargs)
    
    @classmethod
    def get_current_week(cls):
        """Get or create the current week's attendance record."""
        today = timezone.now().date()
        
        # Find Monday (start of week)
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)  # Sunday
        
        obj, created = cls.objects.get_or_create(
            week_start_date=week_start,
            week_end_date=week_end,
            defaults={'total_members': get_user_model().objects.filter(is_active=True).count()}
        )
        
        return obj


class Meeting(TimeStampedModel):
    """
    Meeting scheduling and calendar system.
    Allows admins to schedule meetings and track attendance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Scheduling
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    
    # Location
    location = models.CharField(max_length=200, blank=True)
    is_virtual = models.BooleanField(default=False)
    virtual_link = models.URLField(blank=True)
    
    # Scope - who should attend
    class Scope(models.TextChoices):
        MISSION = 'mission', 'Mission-Wide'
        AREA = 'area', 'Area'
        DISTRICT = 'district', 'District'
        BRANCH = 'branch', 'Branch'
        CUSTOM = 'custom', 'Custom Selection'
    
    scope = models.CharField(max_length=20, choices=Scope.choices, default=Scope.BRANCH)
    
    # Hierarchy references for scope
    branch = models.ForeignKey(
        'core.Branch', on_delete=models.CASCADE, null=True, blank=True, related_name='meetings'
    )
    district = models.ForeignKey(
        'core.District', on_delete=models.CASCADE, null=True, blank=True, related_name='meetings'
    )
    area = models.ForeignKey(
        'core.Area', on_delete=models.CASCADE, null=True, blank=True, related_name='meetings'
    )
    
    # Meeting type
    class MeetingType(models.TextChoices):
        GENERAL = 'general', 'General Meeting'
        BOARD = 'board', 'Board Meeting'
        STAFF = 'staff', 'Staff Meeting'
        EXECUTIVE = 'executive', 'Executive Meeting'
        TRAINING = 'training', 'Training Session'
        PRAYER = 'prayer', 'Prayer Meeting'
        OTHER = 'other', 'Other'
    
    meeting_type = models.CharField(max_length=20, choices=MeetingType.choices, default=MeetingType.GENERAL)
    
    # Organizer
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_meetings'
    )
    
    # Status
    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Scheduled'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        POSTPONED = 'postponed', 'Postponed'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    
    # Notifications
    send_reminder = models.BooleanField(default=True)
    reminder_hours_before = models.IntegerField(default=24)
    reminder_sent = models.BooleanField(default=False)
    
    # Attendance tracking
    attendance_required = models.BooleanField(default=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date', '-start_time']
        verbose_name = 'Meeting'
        verbose_name_plural = 'Meetings'
    
    def __str__(self):
        return f"{self.title} - {self.date}"
    
    @property
    def is_upcoming(self):
        """Check if meeting is in the future."""
        from datetime import datetime
        meeting_datetime = datetime.combine(self.date, self.start_time)
        return meeting_datetime > datetime.now()
    
    @property
    def attendee_count(self):
        """Get count of expected attendees."""
        return self.attendees.count()
    
    @property
    def present_count(self):
        """Get count of attendees marked present."""
        return self.attendees.filter(status='present').count()


class MeetingAttendee(TimeStampedModel):
    """
    Track meeting attendees and their attendance status.
    Staff members are auto-listed but NOT auto-marked present.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='attendees')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meeting_attendances')
    
    # Attendance status
    class Status(models.TextChoices):
        INVITED = 'invited', 'Invited'
        CONFIRMED = 'confirmed', 'Confirmed'
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'
        EXCUSED = 'excused', 'Excused'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INVITED)
    
    # Timestamps
    check_in_time = models.DateTimeField(null=True, blank=True)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='marked_meeting_attendances'
    )
    marked_at = models.DateTimeField(null=True, blank=True)
    
    # Is this a staff member (for sitting allowance tracking)
    is_staff_member = models.BooleanField(default=False)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        unique_together = ['meeting', 'user']
        verbose_name = 'Meeting Attendee'
        verbose_name_plural = 'Meeting Attendees'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.meeting.title}"


class MissionStaffAttendance(TimeStampedModel):
    """
    Mission Staff Attendance Register
    Simple, session-based attendance tracking for mission-level staff
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Attendance date and session details
    date = models.DateField(help_text="Date of the staff meeting/attendance")
    title = models.CharField(
        max_length=200, 
        default="Mission Staff Meeting",
        help_text="Optional custom title for this attendance session"
    )
    
    # Status and locking
    is_locked = models.BooleanField(default=False, help_text="Attendance is locked after 24 hours")
    locked_at = models.DateTimeField(null=True, blank=True)
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='locked_staff_attendances'
    )
    
    # Attendance summary
    total_staff = models.IntegerField(default=0, help_text="Total mission staff members")
    present_count = models.IntegerField(default=0)
    absent_count = models.IntegerField(default=0)
    
    # Meeting details (optional)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Meeting notes or agenda")
    
    # Created by
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_staff_attendances'
    )
    
    class Meta:
        ordering = ['-date']
        unique_together = ['date']
        verbose_name = 'Mission Staff Attendance'
        verbose_name_plural = 'Mission Staff Attendances'
    
    def __str__(self):
        return f"Mission Staff Attendance - {self.date}"
    
    def can_be_edited(self):
        """Check if attendance can still be edited (within 24 hours)."""
        from django.utils import timezone
        from datetime import timedelta
        
        if self.is_locked:
            return False
        
        # Check if 24 hours have passed
        attendance_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, timezone.datetime.min.time())
        )
        time_passed = timezone.now() - attendance_datetime
        return time_passed < timedelta(hours=24)
    
    def lock_attendance(self, user):
        """Lock the attendance to prevent further changes."""
        self.is_locked = True
        self.locked_at = timezone.now()
        self.locked_by = user
        self.save()
    
    def update_counts(self):
        """Update attendance counts from records."""
        self.present_count = self.records.filter(status='present').count()
        self.absent_count = self.records.filter(status='absent').count()
        self.save()


class MissionStaffAttendanceRecord(TimeStampedModel):
    """
    Individual attendance record for mission staff
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    attendance = models.ForeignKey(
        MissionStaffAttendance,
        on_delete=models.CASCADE,
        related_name='records'
    )
    staff_member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mission_staff_attendance_records'
    )
    
    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'
        EXCUSED = 'excused', 'Excused'
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PRESENT
    )
    
    # Who marked this attendance
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marked_staff_attendance_records'
    )
    marked_at = models.DateTimeField(null=True, blank=True)
    
    # Notes for this specific staff member
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['staff_member__first_name', 'staff_member__last_name']
        unique_together = ['attendance', 'staff_member']
        verbose_name = 'Mission Staff Attendance Record'
        verbose_name_plural = 'Mission Staff Attendance Records'
    
    def __str__(self):
        return f"{self.staff_member.get_full_name()} - {self.attendance.date} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Set marked timestamp if status is being set
        if self.marked_by and not self.marked_at:
            self.marked_at = timezone.now()
        super().save(*args, **kwargs)
        
        # Update parent attendance counts
        self.attendance.update_counts()
