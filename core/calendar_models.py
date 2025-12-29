"""
Church Calendar Models - Yearly events and activities management
"""

import uuid
from django.db import models
from django.conf import settings
from .models import TimeStampedModel


class CalendarEvent(TimeStampedModel):
    """Church calendar events and activities."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    class EventType(models.TextChoices):
        SERVICE = 'service', 'Church Service'
        MEETING = 'meeting', 'Meeting'
        CONFERENCE = 'conference', 'Conference'
        REVIVAL = 'revival', 'Revival'
        CAMP = 'camp', 'Camp Meeting'
        FELLOWSHIP = 'fellowship', 'Fellowship'
        OUTREACH = 'outreach', 'Outreach/Evangelism'
        TRAINING = 'training', 'Training/Workshop'
        CELEBRATION = 'celebration', 'Celebration/Anniversary'
        HOLIDAY = 'holiday', 'Holiday'
        OTHER = 'other', 'Other'
    
    event_type = models.CharField(max_length=20, choices=EventType.choices, default=EventType.SERVICE)
    
    # Date & Time
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_all_day = models.BooleanField(default=False)
    
    # Recurrence
    class Recurrence(models.TextChoices):
        NONE = 'none', 'One-time Event'
        WEEKLY = 'weekly', 'Weekly'
        MONTHLY = 'monthly', 'Monthly'
        YEARLY = 'yearly', 'Yearly'
    
    recurrence = models.CharField(max_length=20, choices=Recurrence.choices, default=Recurrence.NONE)
    
    # Scope
    class Scope(models.TextChoices):
        MISSION = 'mission', 'Mission-wide'
        AREA = 'area', 'Area'
        DISTRICT = 'district', 'District'
        BRANCH = 'branch', 'Branch'
    
    scope = models.CharField(max_length=20, choices=Scope.choices, default=Scope.MISSION)
    
    # Location
    location = models.CharField(max_length=300, blank=True)
    venue_address = models.TextField(blank=True)
    
    # Hierarchy (for scoped events)
    branch = models.ForeignKey(
        'core.Branch', on_delete=models.CASCADE, null=True, blank=True, related_name='calendar_events'
    )
    area = models.ForeignKey(
        'core.Area', on_delete=models.CASCADE, null=True, blank=True, related_name='calendar_events'
    )
    
    # Additional info
    contact_person = models.CharField(max_length=200, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    
    # Status
    is_published = models.BooleanField(default=True)
    is_cancelled = models.BooleanField(default=False)
    
    # Creator
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_events'
    )
    
    class Meta:
        ordering = ['start_date', 'start_time']
        verbose_name = 'Calendar Event'
        verbose_name_plural = 'Calendar Events'
    
    def __str__(self):
        return f"{self.title} ({self.start_date})"
    
    @property
    def is_multi_day(self):
        return self.end_date and self.end_date != self.start_date


class YearlyCalendar(models.Model):
    """Yearly calendar configuration."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    year = models.IntegerField(unique=True)
    theme = models.CharField(max_length=200, blank=True)
    theme_verse = models.TextField(blank=True)
    
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-year']
        verbose_name = 'Yearly Calendar'
        verbose_name_plural = 'Yearly Calendars'
    
    def __str__(self):
        return f"Calendar {self.year}"
