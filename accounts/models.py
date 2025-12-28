"""
Accounts Models - Custom User with Role-Based Access Control
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings


class UserManager(BaseUserManager):
    """Custom user manager for SDSCC User model."""
    
    def create_user(self, member_id, password=None, **extra_fields):
        if not member_id:
            raise ValueError('Member ID is required')
        user = self.model(member_id=member_id, **extra_fields)
        user.set_password(password or settings.SDSCC_SETTINGS['DEFAULT_PASSWORD'])
        user.save(using=self._db)
        return user
    
    def create_superuser(self, member_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.MISSION_ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(member_id, password, **extra_fields)


class User(AbstractUser):
    """Custom User model for SDSCC with role-based access."""
    
    class Role(models.TextChoices):
        MISSION_ADMIN = 'mission_admin', 'Mission Admin'
        AREA_EXECUTIVE = 'area_executive', 'Area Executive'
        DISTRICT_EXECUTIVE = 'district_executive', 'District Executive'
        BRANCH_EXECUTIVE = 'branch_executive', 'Branch Executive'
        AUDITOR = 'auditor', 'Auditor / Board of Trustees'
        PASTOR = 'pastor', 'Pastor'
        STAFF = 'staff', 'Staff'
        MEMBER = 'member', 'Member'
    
    class PastoralRank(models.TextChoices):
        NONE = 'none', 'None'
        ASSOCIATE = 'associate', 'Associate Pastor'
        BRANCH = 'branch', 'Branch Pastor'
        SENIOR = 'senior', 'Senior Pastor'
        DISTRICT = 'district', 'District Pastor'
        AREA = 'area', 'Area Pastor'
        MISSION = 'mission', 'Mission Pastor'
        GENERAL_OVERSEER = 'overseer', 'General Overseer'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Remove username, use member_id instead
    username = None
    member_id = models.CharField(max_length=20, unique=True, db_index=True)
    
    # Personal Info
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    other_names = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
    
    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Role & Permissions
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    pastoral_rank = models.CharField(max_length=20, choices=PastoralRank.choices, default=PastoralRank.NONE)
    ordination_date = models.DateField(null=True, blank=True, help_text="Date of ordination into ministry")
    ordination_place = models.CharField(max_length=200, blank=True, help_text="Church/location where ordination took place")
    ordaining_minister = models.CharField(max_length=100, blank=True, help_text="Name of minister who performed ordination")
    
    # Church Hierarchy Assignment
    branch = models.ForeignKey(
        'core.Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    # For executives managing specific areas/districts
    managed_area = models.ForeignKey(
        'core.Area',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='executives'
    )
    managed_district = models.ForeignKey(
        'core.District',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='executives'
    )
    
    # Authentication
    pin = models.CharField(max_length=10, default='12345')  # 5-digit PIN
    pin_changed = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Salary Information
    qualifies_for_salary = models.BooleanField(default=False, help_text="Whether this user qualifies for salary payments")
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Monthly base salary amount")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'member_id'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.member_id})"
    
    def get_full_name(self):
        """Return the full name."""
        names = [self.first_name, self.other_names, self.last_name]
        return ' '.join(filter(None, names))
    
    def get_short_name(self):
        return self.first_name
    
    # Role Checks
    @property
    def is_mission_admin(self):
        return self.role == self.Role.MISSION_ADMIN or self.is_superuser
    
    @property
    def is_area_executive(self):
        return self.role == self.Role.AREA_EXECUTIVE
    
    @property
    def is_district_executive(self):
        return self.role == self.Role.DISTRICT_EXECUTIVE
    
    @property
    def is_branch_executive(self):
        return self.role == self.Role.BRANCH_EXECUTIVE
    
    @property
    def is_auditor(self):
        return self.role == self.Role.AUDITOR
    
    @property
    def is_pastor(self):
        return self.role == self.Role.PASTOR
    
    @property
    def is_staff_member(self):
        return self.role == self.Role.STAFF
    
    @property
    def is_regular_member(self):
        return self.role == self.Role.MEMBER
    
    @property
    def is_any_admin(self):
        """Check if user has any administrative role."""
        admin_roles = [
            self.Role.MISSION_ADMIN,
            self.Role.AREA_EXECUTIVE,
            self.Role.DISTRICT_EXECUTIVE,
            self.Role.BRANCH_EXECUTIVE
        ]
        return self.role in admin_roles or self.is_superuser
    
    @property
    def can_manage_finances(self):
        """Check if user can manage financial entries."""
        finance_roles = [
            self.Role.MISSION_ADMIN,
            self.Role.AREA_EXECUTIVE,
            self.Role.DISTRICT_EXECUTIVE,
            self.Role.BRANCH_EXECUTIVE
        ]
        return self.role in finance_roles
    
    @property
    def can_view_all_finances(self):
        """Check if user can view all financial data."""
        return self.is_mission_admin or self.is_auditor
    
    def get_accessible_branches(self):
        """Get list of branches this user can access based on role."""
        from core.models import Branch
        
        if self.is_mission_admin or self.is_auditor:
            return Branch.objects.filter(is_active=True)
        elif self.is_area_executive and self.managed_area:
            return Branch.objects.filter(district__area=self.managed_area, is_active=True)
        elif self.is_district_executive and self.managed_district:
            return Branch.objects.filter(district=self.managed_district, is_active=True)
        elif self.branch:
            return Branch.objects.filter(pk=self.branch.pk)
        return Branch.objects.none()
    
    def get_dashboard_url(self):
        """Return appropriate dashboard URL based on role."""
        from django.urls import reverse
        
        dashboard_map = {
            self.Role.MISSION_ADMIN: 'core:mission_dashboard',
            self.Role.AREA_EXECUTIVE: 'core:area_dashboard',
            self.Role.DISTRICT_EXECUTIVE: 'core:district_dashboard',
            self.Role.BRANCH_EXECUTIVE: 'core:branch_dashboard',
            self.Role.AUDITOR: 'core:auditor_dashboard',
            self.Role.PASTOR: 'core:pastor_dashboard',
            self.Role.STAFF: 'core:staff_dashboard',
            self.Role.MEMBER: 'core:member_dashboard',
        }
        return reverse(dashboard_map.get(self.role, 'core:member_dashboard'))


class UserProfile(models.Model):
    """Extended user profile for additional member information."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    
    # Personal Details
    class MaritalStatus(models.TextChoices):
        SINGLE = 'single', 'Single'
        MARRIED = 'married', 'Married'
        DIVORCED = 'divorced', 'Divorced'
        WIDOWED = 'widowed', 'Widowed'
    
    marital_status = models.CharField(max_length=10, choices=MaritalStatus.choices, blank=True)
    profession = models.CharField(max_length=100, blank=True)
    employer = models.CharField(max_length=200, blank=True)
    
    # Church Journey
    baptism_date = models.DateField(null=True, blank=True)
    baptism_by = models.CharField(max_length=100, blank=True, help_text="Name of minister who performed baptism")
    membership_date = models.DateField(null=True, blank=True)
    previous_church = models.CharField(max_length=200, blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    
    # Pastoral Notes (visible only to pastors/admins)
    pastoral_notes = models.TextField(blank=True)
    counseling_status = models.CharField(max_length=100, blank=True)
    
    # Skills & Talents
    skills = models.TextField(blank=True, help_text='Comma-separated list of skills')
    talents = models.TextField(blank=True, help_text='Comma-separated list of talents')
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"Profile: {self.user.get_full_name()}"


class LoginHistory(models.Model):
    """Track user login history for security."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    success = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Login History'
        verbose_name_plural = 'Login Histories'
    
    def __str__(self):
        status = 'Success' if self.success else 'Failed'
        return f"{self.user.member_id} - {status} - {self.timestamp}"
