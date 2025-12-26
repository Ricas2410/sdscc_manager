"""
Attendance Models - Track church service attendance
Supports Sabbath (Saturday), midweek, and special services
"""

import uuid
from django.db import models
from django.conf import settings
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
