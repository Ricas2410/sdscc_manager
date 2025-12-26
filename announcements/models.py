"""
Announcements Models - Hierarchical church communication system
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import TimeStampedModel


class Announcement(TimeStampedModel):
    """Church announcements with hierarchical visibility."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    title = models.CharField(max_length=300)
    content = models.TextField()
    
    # Scope - determines who can see the announcement
    class Scope(models.TextChoices):
        MISSION = 'mission', 'Mission (Everyone)'
        AREA = 'area', 'Area'
        DISTRICT = 'district', 'District'
        BRANCH = 'branch', 'Branch'
    
    scope = models.CharField(max_length=20, choices=Scope.choices, default=Scope.BRANCH)
    
    # Target hierarchy
    branch = models.ForeignKey(
        'core.Branch', on_delete=models.CASCADE, null=True, blank=True, related_name='announcements'
    )
    district = models.ForeignKey(
        'core.District', on_delete=models.CASCADE, null=True, blank=True, related_name='announcements'
    )
    area = models.ForeignKey(
        'core.Area', on_delete=models.CASCADE, null=True, blank=True, related_name='announcements'
    )
    
    # Priority
    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        NORMAL = 'normal', 'Normal'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'
    
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.NORMAL)
    
    # Scheduling
    publish_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    
    # Media
    image = models.ImageField(upload_to='announcements/', blank=True, null=True)
    
    # Stats
    view_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-is_pinned', '-publish_date']
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
    
    def __str__(self):
        return self.title
    
    @property
    def is_active(self):
        from django.utils import timezone
        now = timezone.now()
        if not self.is_published:
            return False
        if self.expiry_date and self.expiry_date < now:
            return False
        return self.publish_date <= now


class AnnouncementAttachment(models.Model):
    """File attachments for announcements."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='attachments')
    
    file = models.FileField(upload_to='announcement_attachments/')
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50, blank=True)
    file_size = models.IntegerField(default=0)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['filename']
    
    def __str__(self):
        return self.filename


class Event(TimeStampedModel):
    """Church events and calendar items."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    
    # Scope
    class Scope(models.TextChoices):
        MISSION = 'mission', 'Mission (National)'
        AREA = 'area', 'Area'
        DISTRICT = 'district', 'District'
        BRANCH = 'branch', 'Branch'
    
    scope = models.CharField(max_length=20, choices=Scope.choices, default=Scope.BRANCH)
    
    # Target hierarchy
    branch = models.ForeignKey(
        'core.Branch', on_delete=models.CASCADE, null=True, blank=True, related_name='events'
    )
    district = models.ForeignKey(
        'core.District', on_delete=models.CASCADE, null=True, blank=True, related_name='events'
    )
    area = models.ForeignKey(
        'core.Area', on_delete=models.CASCADE, null=True, blank=True, related_name='events'
    )
    
    # Event details
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    
    location = models.CharField(max_length=300, blank=True)
    address = models.TextField(blank=True)
    
    # Event type
    class EventType(models.TextChoices):
        SERVICE = 'service', 'Church Service'
        MEETING = 'meeting', 'Meeting'
        CONFERENCE = 'conference', 'Conference'
        WORKSHOP = 'workshop', 'Workshop'
        FELLOWSHIP = 'fellowship', 'Fellowship'
        OUTREACH = 'outreach', 'Outreach'
        FUNDRAISING = 'fundraising', 'Fundraising'
        OTHER = 'other', 'Other'
    
    event_type = models.CharField(max_length=20, choices=EventType.choices, default=EventType.SERVICE)
    
    # Organizer
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='organized_events'
    )
    
    # Media
    banner_image = models.ImageField(upload_to='event_banners/', blank=True, null=True)
    
    is_published = models.BooleanField(default=True)
    is_cancelled = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-start_date', '-start_time']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
    
    def __str__(self):
        return f"{self.title} - {self.start_date}"
