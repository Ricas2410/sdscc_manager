"""
Sermons Models - Sermon library management
"""

import uuid
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class SermonCategory(models.Model):
    """Categories for organizing sermons."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Sermon Category'
        verbose_name_plural = 'Sermon Categories'
    
    def __str__(self):
        return self.name


class Sermon(TimeStampedModel):
    """Sermon entries with text, audio, and video support."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, blank=True)
    
    # Content
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True, help_text='Full sermon text')
    scripture_reference = models.CharField(max_length=200, blank=True)
    
    # Category & Tags
    category = models.ForeignKey(
        SermonCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='sermons'
    )
    tags = models.CharField(max_length=500, blank=True, help_text='Comma-separated tags')
    
    # Preacher info
    preacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sermons'
    )
    preacher_name = models.CharField(max_length=200, blank=True)  # For guest preachers
    
    # Date & Location
    sermon_date = models.DateField()
    branch = models.ForeignKey(
        'core.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='sermons'
    )
    
    # Scope - who can view
    class Scope(models.TextChoices):
        MISSION = 'mission', 'Mission (Everyone)'
        AREA = 'area', 'Area'
        DISTRICT = 'district', 'District'
        BRANCH = 'branch', 'Branch Only'
    
    scope = models.CharField(max_length=20, choices=Scope.choices, default=Scope.MISSION)
    
    # Media
    class MediaType(models.TextChoices):
        TEXT = 'text', 'Text Only'
        AUDIO = 'audio', 'Audio'
        VIDEO = 'video', 'Video'
        MIXED = 'mixed', 'Multiple Formats'
    
    media_type = models.CharField(max_length=20, choices=MediaType.choices, default=MediaType.TEXT)
    
    audio_file = models.FileField(upload_to='sermons/audio/', blank=True, null=True)
    video_url = models.URLField(blank=True, help_text='YouTube, Vimeo, or other video link')
    pdf_file = models.FileField(upload_to='sermons/pdf/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='sermons/thumbnails/', blank=True, null=True)
    
    # Duration (for audio/video)
    duration_minutes = models.IntegerField(null=True, blank=True)
    
    # Status
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Stats
    view_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-sermon_date', '-created_at']
        verbose_name = 'Sermon'
        verbose_name_plural = 'Sermons'
    
    def __str__(self):
        return f"{self.title} - {self.sermon_date}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(f"{self.title}-{self.sermon_date}")
        super().save(*args, **kwargs)


class SermonNote(TimeStampedModel):
    """User notes on sermons."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    sermon = models.ForeignKey(Sermon, on_delete=models.CASCADE, related_name='notes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sermon_notes')
    
    content = models.TextField()
    is_private = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['sermon', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.sermon.title}"


class SermonBookmark(models.Model):
    """User bookmarks for sermons."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    sermon = models.ForeignKey(Sermon, on_delete=models.CASCADE, related_name='bookmarks')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarked_sermons')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['sermon', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.sermon.title}"
