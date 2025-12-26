"""
Groups Models - Church ministries, departments, and group management
"""

import uuid
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class GroupCategory(models.Model):
    """Categories for organizing groups/ministries."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class CategoryType(models.TextChoices):
        MINISTRY = 'ministry', 'Ministry'
        DEPARTMENT = 'department', 'Department'
        COMMITTEE = 'committee', 'Committee'
        FELLOWSHIP = 'fellowship', 'Fellowship'
        OTHER = 'other', 'Other'
    
    category_type = models.CharField(max_length=20, choices=CategoryType.choices, default=CategoryType.MINISTRY)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Group Category'
        verbose_name_plural = 'Group Categories'
    
    def __str__(self):
        return self.name


class Group(TimeStampedModel):
    """Church groups, ministries, and departments."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    category = models.ForeignKey(
        GroupCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='groups'
    )
    
    # Scope
    class Scope(models.TextChoices):
        MISSION = 'mission', 'Mission (National)'
        AREA = 'area', 'Area'
        DISTRICT = 'district', 'District'
        BRANCH = 'branch', 'Branch'
    
    scope = models.CharField(max_length=20, choices=Scope.choices, default=Scope.BRANCH)
    
    # Hierarchy
    branch = models.ForeignKey(
        'core.Branch', on_delete=models.CASCADE, null=True, blank=True, related_name='groups'
    )
    district = models.ForeignKey(
        'core.District', on_delete=models.CASCADE, null=True, blank=True, related_name='groups'
    )
    area = models.ForeignKey(
        'core.Area', on_delete=models.CASCADE, null=True, blank=True, related_name='groups'
    )
    
    # Leadership
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='led_groups'
    )
    assistant_leader = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assist_led_groups'
    )
    secretary = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='secretary_groups'
    )
    
    # Meeting schedule
    meeting_day = models.CharField(max_length=20, blank=True)
    meeting_time = models.TimeField(null=True, blank=True)
    meeting_location = models.CharField(max_length=200, blank=True)
    
    # Image/Logo
    image = models.ImageField(upload_to='groups/', blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    established_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'
    
    def __str__(self):
        return self.name
    
    @property
    def member_count(self):
        return self.memberships.filter(is_active=True).count()


class GroupMembership(TimeStampedModel):
    """Track member assignments to groups."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_memberships')
    
    # Role in group
    class Role(models.TextChoices):
        MEMBER = 'member', 'Member'
        LEADER = 'leader', 'Leader'
        ASSISTANT = 'assistant', 'Assistant Leader'
        SECRETARY = 'secretary', 'Secretary'
        TREASURER = 'treasurer', 'Treasurer'
    
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    
    join_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['group__name', 'member__first_name']
        unique_together = ['group', 'member']
        verbose_name = 'Group Membership'
        verbose_name_plural = 'Group Memberships'
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.group.name}"


class GroupMeeting(TimeStampedModel):
    """Track group meetings and attendance."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='meetings')
    
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    
    title = models.CharField(max_length=200, blank=True)
    agenda = models.TextField(blank=True)
    minutes = models.TextField(blank=True)
    
    # Attendance
    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='attended_group_meetings'
    )
    attendance_count = models.IntegerField(default=0)
    
    is_cancelled = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date', '-start_time']
        verbose_name = 'Group Meeting'
        verbose_name_plural = 'Group Meetings'
    
    def __str__(self):
        return f"{self.group.name} - {self.date}"
