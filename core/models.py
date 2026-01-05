"""
Core Models - Church Hierarchy Structure
SDSCC: Mission → Area → District → Branch → Members
"""

import uuid
from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    """Abstract base model with created/updated timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated'
    )

    class Meta:
        abstract = True


class SiteSettings(models.Model):
    """Global site settings for SDSCC."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Branding - Logo & Images
    site_name = models.CharField(max_length=100, default='SDSCC')
    site_logo = models.ImageField(upload_to='settings/', blank=True, null=True, help_text='Main site logo')
    site_logo_url = models.URLField(blank=True, help_text='Fallback logo URL if no upload')
    site_favicon = models.ImageField(upload_to='settings/', blank=True, null=True)
    site_favicon_url = models.URLField(blank=True, help_text='Fallback favicon URL')
    login_background = models.ImageField(upload_to='settings/', blank=True, null=True, help_text='Login page background image')
    login_background_url = models.URLField(blank=True, default='https://images.unsplash.com/photo-1438232992991-995b7058bbb3?w=1920', help_text='Fallback login background URL')
    dashboard_banner = models.ImageField(upload_to='settings/', blank=True, null=True, help_text='Dashboard banner image')
    dashboard_banner_url = models.URLField(blank=True, help_text='Fallback dashboard banner URL')
    
    # Branding - Text & Colors
    tagline = models.CharField(max_length=255, blank=True, default='Seventh Day Sabbath Church of Christ')
    footer_text = models.CharField(max_length=255, blank=True, default='© 2024 SDSCC. All rights reserved.')
    primary_color = models.CharField(max_length=7, default='#1e40af', help_text='Hex color code')
    secondary_color = models.CharField(max_length=7, default='#3b82f6', help_text='Hex color code')
    accent_color = models.CharField(max_length=7, default='#10b981', help_text='Accent color for highlights')
    sidebar_color = models.CharField(max_length=7, default='#1e293b', help_text='Sidebar background color')
    
    # Contact Info
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    alternate_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    postal_address = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    
    # Social Media
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text='WhatsApp number with country code')
    tiktok_url = models.URLField(blank=True)
    
    # Financial Settings
    default_tithe_target = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10)
    currency_symbol = models.CharField(max_length=10, default='GH₵')
    currency_code = models.CharField(max_length=3, default='GHS')
    
    # System Mode
    maintenance_mode = models.BooleanField(default=False, help_text='Put system in maintenance mode')
    maintenance_message = models.TextField(blank=True, default='System is under maintenance. Please check back later.')
    maintenance_allowed_ips = models.TextField(blank=True, help_text='Comma-separated IPs allowed during maintenance')
    
    # Feature Toggles - General
    enable_pwa = models.BooleanField(default=True, help_text='Enable Progressive Web App features')
    enable_offline_mode = models.BooleanField(default=True, help_text='Enable offline data caching')
    enable_push_notifications = models.BooleanField(default=False, help_text='Enable push notifications')
    enable_sms_notifications = models.BooleanField(default=False, help_text='Enable SMS notifications')
    enable_email_notifications = models.BooleanField(default=True, help_text='Enable email notifications')
    
    # Feature Toggles - Modules
    enable_contributions = models.BooleanField(default=True, help_text='Enable contributions module')
    enable_expenditure = models.BooleanField(default=True, help_text='Enable expenditure module')
    enable_attendance = models.BooleanField(default=True, help_text='Enable attendance tracking')
    enable_sermons = models.BooleanField(default=True, help_text='Enable sermons module')
    enable_announcements = models.BooleanField(default=True, help_text='Enable announcements module')
    enable_groups = models.BooleanField(default=True, help_text='Enable groups/ministries module')
    enable_payroll = models.BooleanField(default=True, help_text='Enable payroll module')
    enable_reports = models.BooleanField(default=True, help_text='Enable reports module')
    enable_csv_import = models.BooleanField(default=True, help_text='Enable CSV import functionality')
    
    # Feature Toggles - Role-specific
    allow_pastor_announcements = models.BooleanField(default=True, help_text='Allow pastors to create announcements')
    allow_pastor_events = models.BooleanField(default=True, help_text='Allow pastors to create events')
    show_pastor_contribution_panel = models.BooleanField(default=False, help_text='Show contribution panel to pastors')
    allow_member_profile_edit = models.BooleanField(default=True, help_text='Allow members to edit their profiles')
    allow_member_contribution_view = models.BooleanField(default=True, help_text='Allow members to view their contributions')
    allow_auditor_payroll_access = models.BooleanField(
        default=False,
        help_text='Allow auditors to access payroll dashboards for read-only oversight'
    )
    show_archives = models.BooleanField(default=True, help_text='Show archives in member sidebar')
    
    # Security Settings
    session_timeout_minutes = models.IntegerField(default=60, help_text='Session timeout in minutes')
    max_login_attempts = models.IntegerField(default=5, help_text='Max failed login attempts before lockout')
    lockout_duration_minutes = models.IntegerField(default=30, help_text='Account lockout duration in minutes')
    require_strong_password = models.BooleanField(default=True, help_text='Require strong passwords')
    enable_two_factor_auth = models.BooleanField(default=False, help_text='Enable two-factor authentication')
    
    # Backup & Data
    auto_backup_enabled = models.BooleanField(default=False, help_text='Enable automatic database backups')
    backup_frequency_days = models.IntegerField(default=7, help_text='Backup frequency in days')
    data_retention_years = models.IntegerField(default=7, help_text='Years to retain historical data')
    
    # Current Fiscal Year
    current_fiscal_year = models.IntegerField(default=2024)
    fiscal_year_start_month = models.IntegerField(default=1, help_text='Month fiscal year starts (1-12)')
    
    # Audit
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return self.site_name
    
    @classmethod
    def get_settings(cls):
        """Get or create site settings singleton."""
        settings_obj, _ = cls.objects.get_or_create(pk=uuid.UUID('00000000-0000-0000-0000-000000000001'))
        return settings_obj
    
    def is_ip_allowed_during_maintenance(self, ip_address):
        """Check if IP is allowed during maintenance mode."""
        if not self.maintenance_mode:
            return True
        if not self.maintenance_allowed_ips:
            return False
        allowed_ips = [ip.strip() for ip in self.maintenance_allowed_ips.split(',')]
        return ip_address in allowed_ips
    
    def get_logo_url(self):
        """Get logo URL - uploaded file or fallback URL."""
        if self.site_logo:
            return self.site_logo.url
        return self.site_logo_url or '/static/images/logo.png'
    
    def get_favicon_url(self):
        """Get favicon URL - uploaded file or fallback URL."""
        if self.site_favicon:
            return self.site_favicon.url
        return self.site_favicon_url or '/static/images/favicon.ico'
    
    def get_login_background_url(self):
        """Get login background URL - uploaded file or fallback URL."""
        if self.login_background:
            return self.login_background.url
        return self.login_background_url or 'https://images.unsplash.com/photo-1438232992991-995b7058bbb3?w=1920'
    
    def get_dashboard_banner_url(self):
        """Get dashboard banner URL - uploaded file or fallback URL."""
        if self.dashboard_banner:
            return self.dashboard_banner.url
        return self.dashboard_banner_url or ''


class Area(TimeStampedModel):
    """Area level in church hierarchy - manages multiple districts."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Area'
        verbose_name_plural = 'Areas'
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def district_count(self):
        return self.districts.filter(is_active=True).count()
    
    @property
    def branch_count(self):
        return Branch.objects.filter(district__area=self, is_active=True).count()
    
    @property
    def member_count(self):
        from accounts.models import User
        return User.objects.filter(branch__district__area=self, is_active=True, role='member').count()


class District(TimeStampedModel):
    """District level in church hierarchy - manages multiple branches."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='districts')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['area__name', 'name']
        verbose_name = 'District'
        verbose_name_plural = 'Districts'
    
    def __str__(self):
        return f"{self.name} ({self.code}) - {self.area.name}"
    
    @property
    def branch_count(self):
        return self.branches.filter(is_active=True).count()
    
    @property
    def member_count(self):
        from accounts.models import User
        return User.objects.filter(branch__district=self, is_active=True, role='member').count()


class Branch(TimeStampedModel):
    """Branch level in church hierarchy - local church assembly."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district = models.ForeignKey(District, on_delete=models.PROTECT, related_name='branches')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    
    # Leadership
    pastor = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pastored_branches',
        limit_choices_to={'role': 'pastor'}
    )
    
    # Location Details
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    
    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Financial Settings
    monthly_tithe_target = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    local_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    is_active = models.BooleanField(default=True)
    established_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['district__area__name', 'district__name', 'name']
        verbose_name = 'Branch'
        verbose_name_plural = 'Branches'
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def area(self):
        return self.district.area
    
    @property
    def member_count(self):
        """Get total count of all active users in this branch."""
        from accounts.models import User
        return User.objects.filter(branch=self, is_active=True).count()
    
    @property
    def full_hierarchy(self):
        """Return full hierarchy path."""
        return f"{self.district.area.name} > {self.district.name} > {self.name}"


class FiscalYear(TimeStampedModel):
    """Fiscal year for financial tracking and year-end rollover."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.IntegerField(unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    closed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-year']
        verbose_name = 'Fiscal Year'
        verbose_name_plural = 'Fiscal Years'
    
    def __str__(self):
        return f"FY {self.year}"
    
    def save(self, *args, **kwargs):
        # DEPRECATED: Year-as-state architecture
        # is_current functionality disabled to eliminate global year state
        # Multiple years can now be "current" - this field is ignored
        super().save(*args, **kwargs)
    
    @classmethod
    def get_current(cls):
        """DEPRECATED: Year-as-state architecture - Returns None to eliminate current year dependency.
        Reports should use date filtering instead of fiscal year filtering.
        """
        return None


class MonthlyClose(TimeStampedModel):
    """Track monthly closing for tithe calculations and commission."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.PROTECT, related_name='monthly_closes')
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='monthly_closes')
    month = models.IntegerField()  # 1-12
    year = models.IntegerField()
    
    # Financial Summary
    total_tithe = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_contributions = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_expenditure = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    mission_allocation = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    branch_retained = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    # Target & Commission
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    target_achieved = models.BooleanField(default=False)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    commission_paid = models.BooleanField(default=False)
    commission_paid_date = models.DateField(null=True, blank=True)
    
    # Status
    is_closed = models.BooleanField(default=False)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='closed_months'
    )
    
    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['branch', 'month', 'year']
        verbose_name = 'Monthly Close'
        verbose_name_plural = 'Monthly Closes'
    
    def __str__(self):
        return f"{self.branch.name} - {self.month}/{self.year}"


# ============ NOTIFICATION SYSTEM ============

class Notification(TimeStampedModel):
    """Real-time notifications for users."""
    
    class NotificationType(models.TextChoices):
        MEMBER_ADDED = 'member_added', 'New Member'
        CONTRIBUTION = 'contribution', 'Contribution'
        EXPENDITURE = 'expenditure', 'Expenditure'
        ANNOUNCEMENT = 'announcement', 'Announcement'
        REMITTANCE = 'remittance', 'Remittance'
        COMMISSION = 'commission', 'Commission'
        PAYROLL = 'payroll', 'Payroll'
        ATTENDANCE = 'attendance', 'Attendance'
        BIRTHDAY = 'birthday', 'Birthday'
        ANNIVERSARY = 'anniversary', 'Anniversary'
        SYSTEM = 'system', 'System'
        PRAYER_REQUEST = 'prayer_request', 'Prayer Request'
        VISITOR = 'visitor', 'Visitor'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)  # URL to related item
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Scope - for filtering notifications
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"{self.notification_type}: {self.title}"
    
    def mark_as_read(self):
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])


# ============ PRAYER REQUEST SYSTEM ============

class PrayerRequest(TimeStampedModel):
    """Prayer requests from members."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PRAYED = 'prayed', 'Prayed For'
        ANSWERED = 'answered', 'Answered'
        CLOSED = 'closed', 'Closed'
    
    class VisibilityScope(models.TextChoices):
        BRANCH = 'branch', 'Branch Only'
        DISTRICT = 'district', 'District Wide'
        AREA = 'area', 'Area Wide'
        MISSION = 'mission', 'Mission Wide'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prayer_requests'
    )
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='prayer_requests')
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Visibility settings
    visibility_scope = models.CharField(
        max_length=10, 
        choices=VisibilityScope.choices, 
        default=VisibilityScope.BRANCH,
        help_text='Who can see this prayer request'
    )
    is_approved = models.BooleanField(
        default=False, 
        help_text='Must be approved by pastor/admin before others can see'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_prayer_requests'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    
    # Tracking
    prayer_count = models.PositiveIntegerField(default=0)  # How many prayed
    answered_date = models.DateField(null=True, blank=True)
    testimony = models.TextField(blank=True)  # Testimony when answered
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Prayer Request'
        verbose_name_plural = 'Prayer Requests'
    
    def __str__(self):
        return f"{self.requester.get_full_name()}: {self.title}"
    
    # Permission methods
    def can_be_managed_by(self, user=None):
        """
        Check if user can edit/delete this prayer request.
        - Creators can always manage their own requests
        - Mission Admin (National) can manage any prayer request
        - Branch admins can only manage prayer requests from their branch members
        - Area/District admins can manage requests from their hierarchy
        """
        if user is None:
            return False
        # Creator can always manage their own requests
        if self.requester == user:
            return True
        # Mission Admin (National) can manage any prayer request
        if user.is_mission_admin:
            return True
        # Area Executive can manage requests from their area
        if user.is_area_executive and user.managed_area:
            return self.branch.district.area == user.managed_area
        # District Executive can manage requests from their district
        if user.is_district_executive and user.managed_district:
            return self.branch.district == user.managed_district
        # Branch Executive/Pastor can only manage requests from their branch members
        if (user.is_branch_executive or user.is_pastor) and user.branch:
            return self.branch == user.branch
        return False
    
    def can_be_approved_by(self, user=None):
        """Check if user can approve this prayer request."""
        if user is None:
            # When called from template, we can't pass user, so return False for safety
            return False
        return (user.is_mission_admin or 
                (user.is_pastor and self.branch == user.branch) or 
                (user.is_branch_executive and self.branch == user.branch))
    
    def can_be_prayed_by(self, user=None):
        """Check if user can mark this as prayed (i.e., can see it)."""
        if user is None:
            # When called from template, we can't pass user, so return False for safety
            return False
        # User can always pray for their own requests
        if self.requester == user:
            return True
        
        # Must be approved for others to see and pray
        if not self.is_approved:
            return False
        
        # Check visibility based on user role and scope
        if user.is_mission_admin:
            return True
        elif user.is_area_executive:
            return (self.visibility_scope in ['mission', 'area'] or 
                   (self.visibility_scope in ['branch', 'district'] and self.branch.district.area == user.managed_area))
        elif user.is_district_executive:
            return (self.visibility_scope in ['mission', 'area', 'district'] or
                   (self.visibility_scope == 'branch' and self.branch.district == user.managed_district))
        elif user.is_pastor or user.is_branch_executive:
            return (self.visibility_scope in ['mission', 'area', 'district'] or
                   self.branch == user.branch)
        else:
            # Regular members
            return (self.visibility_scope in ['mission', 'area', 'district'] or
                   (self.visibility_scope == 'branch' and self.branch == user.branch))


class PrayerInteraction(models.Model):
    """Track who prayed for a request."""
    prayer_request = models.ForeignKey(PrayerRequest, on_delete=models.CASCADE, related_name='interactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prayed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['prayer_request', 'user']


# ============ VISITOR FOLLOW-UP SYSTEM ============

class Visitor(TimeStampedModel):
    """Track visitors for follow-up."""
    
    class Status(models.TextChoices):
        NEW = 'new', 'New Visitor'
        CONTACTED = 'contacted', 'Contacted'
        FOLLOW_UP = 'follow_up', 'Follow-up Scheduled'
        RETURNED = 'returned', 'Returned'
        CONVERTED = 'converted', 'Became Member'
        DECLINED = 'declined', 'Not Interested'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='visitors')
    
    # Personal Info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    # Visit Info
    first_visit_date = models.DateField()
    how_heard = models.CharField(max_length=200, blank=True)  # How they heard about church
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='core_invited_visitors'
    )
    
    # Follow-up
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.NEW)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_visitors'
    )
    notes = models.TextField(blank=True)
    next_follow_up = models.DateField(null=True, blank=True)
    
    # Conversion
    converted_member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='visitor_record'
    )
    converted_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-first_visit_date']
        verbose_name = 'Visitor'
        verbose_name_plural = 'Visitors'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class VisitorFollowUp(TimeStampedModel):
    """Track follow-up actions for visitors."""
    
    class Method(models.TextChoices):
        PHONE = 'phone', 'Phone Call'
        SMS = 'sms', 'SMS'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        VISIT = 'visit', 'Home Visit'
        EMAIL = 'email', 'Email'
    
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='follow_ups')
    followed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    method = models.CharField(max_length=15, choices=Method.choices)
    notes = models.TextField()
    follow_up_date = models.DateField()
    response = models.TextField(blank=True)  # Visitor's response
    
    class Meta:
        ordering = ['-follow_up_date']


# ============ BIRTHDAY & ANNIVERSARY REMINDERS ============

class SpecialDateReminder(models.Model):
    """Track birthdays and anniversaries for reminders."""
    
    class ReminderType(models.TextChoices):
        BIRTHDAY = 'birthday', 'Birthday'
        WEDDING = 'wedding', 'Wedding Anniversary'
        BAPTISM = 'baptism', 'Baptism Anniversary'
        MEMBERSHIP = 'membership', 'Membership Anniversary'
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='special_dates'
    )
    reminder_type = models.CharField(max_length=15, choices=ReminderType.choices)
    date = models.DateField()  # Just month/day, year is for calculation
    year = models.IntegerField(null=True, blank=True)  # Original year (for anniversary calculations)
    
    # Notification settings
    notify_member = models.BooleanField(default=True)
    notify_pastor = models.BooleanField(default=True)
    notify_branch = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'reminder_type']
        verbose_name = 'Special Date Reminder'
        verbose_name_plural = 'Special Date Reminders'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_reminder_type_display()}"


# ============ FINANCIAL SUMMARY MODELS ============

class MissionFinancialSummary(TimeStampedModel):
    """Track monthly financial summary at mission level."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.PROTECT, related_name='mission_summaries')
    month = models.IntegerField()  # 1-12
    year = models.IntegerField()
    
    # Opening Balance
    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Opening balance at start of month')
    
    # Income
    total_remittances = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Total remittances from branches')
    total_other_income = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Other mission income')
    total_income = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Total income for month')
    
    # Expenditure
    total_payroll = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Total staff payroll')
    total_mission_expenses = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Total mission-level expenses')
    total_mission_returns = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Money returned to branches')
    total_expenditure = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Total expenditure for month')
    
    # Closing Balance
    closing_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Closing balance at end of month')
    
    # Status
    is_closed = models.BooleanField(default=False)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='closed_mission_summaries'
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['month', 'year']
        verbose_name = 'Mission Financial Summary'
        verbose_name_plural = 'Mission Financial Summaries'
    
    def __str__(self):
        from calendar import month_name
        return f"Mission Summary - {month_name[self.month]} {self.year}"
    
    def calculate_totals(self):
        """Calculate total income, expenditure, and closing balance."""
        self.total_income = self.total_remittances + self.total_other_income
        self.total_expenditure = self.total_payroll + self.total_mission_expenses + self.total_mission_returns
        self.closing_balance = self.opening_balance + self.total_income - self.total_expenditure
        self.save()


class BranchFinancialSummary(TimeStampedModel):
    """Track monthly financial summary at branch level."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.PROTECT, related_name='branch_summaries')
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='financial_summaries')
    month = models.IntegerField()  # 1-12
    year = models.IntegerField()
    
    # Opening Balance
    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Opening balance at start of month')
    
    # Income
    total_tithe = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Total tithe collected')
    total_offerings = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Total offerings collected')
    total_other_contributions = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Other contributions')
    mission_returns = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Money received from mission')
    total_income = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Total income for month')
    
    # Expenditure
    total_branch_expenses = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Branch-level expenses')
    remittance_to_mission = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Amount remitted to mission')
    pastor_commission = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Pastor commission paid')
    total_expenditure = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Total expenditure for month')
    
    # Closing Balance
    closing_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text='Closing balance at end of month')
    
    # Target & Performance
    tithe_target = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Monthly tithe target')
    target_achieved = models.BooleanField(default=False)
    achievement_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Percentage of target achieved')
    
    # Status
    is_closed = models.BooleanField(default=False)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='closed_branch_summaries'
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-year', '-month', 'branch__name']
        unique_together = ['branch', 'month', 'year']
        verbose_name = 'Branch Financial Summary'
        verbose_name_plural = 'Branch Financial Summaries'
    
    def __str__(self):
        from calendar import month_name
        return f"{self.branch.name} - {month_name[self.month]} {self.year}"
    
    def calculate_totals(self):
        """Calculate total income, expenditure, closing balance, and target achievement."""
        self.total_income = (
            self.total_tithe + 
            self.total_offerings + 
            self.total_other_contributions + 
            self.mission_returns
        )
        self.total_expenditure = (
            self.total_branch_expenses + 
            self.remittance_to_mission + 
            self.pastor_commission
        )
        self.closing_balance = self.opening_balance + self.total_income - self.total_expenditure
        
        # Calculate target achievement
        if self.tithe_target > 0:
            self.achievement_percentage = (self.total_tithe / self.tithe_target) * 100
            self.target_achieved = self.total_tithe >= self.tithe_target
        else:
            self.achievement_percentage = 0
            self.target_achieved = False
        
        self.save()


# Import calendar models to register them with Django
from .calendar_models import CalendarEvent, YearlyCalendar
from .models_assets import ChurchAsset, ChurchAssetMaintenance, ChurchAssetTransfer
