"""
Members Models - Member management extending User model
"""

import uuid
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class Member(TimeStampedModel):
    """
    Member model linking to User for church-specific member data.
    This provides additional tracking beyond the base User model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='member_profile'
    )
    
    # Member Status
    class MembershipStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        TRANSFERRED = 'transferred', 'Transferred'
        DECEASED = 'deceased', 'Deceased'
        SUSPENDED = 'suspended', 'Suspended'
    
    status = models.CharField(
        max_length=20,
        choices=MembershipStatus.choices,
        default=MembershipStatus.ACTIVE
    )
    
    # Transfer Tracking
    transfer_date = models.DateField(null=True, blank=True)
    transfer_from = models.ForeignKey(
        'core.Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transferred_from_members'
    )
    transfer_to = models.ForeignKey(
        'core.Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transferred_to_members'
    )
    transfer_reason = models.TextField(blank=True)
    
    # Spiritual Records
    is_baptized = models.BooleanField(default=False)
    baptism_date = models.DateField(null=True, blank=True)
    baptism_location = models.CharField(max_length=200, blank=True)
    baptized_by = models.CharField(max_length=100, blank=True)
    
    # Roles in Church
    roles_held = models.TextField(blank=True, help_text='Previous and current roles held')
    current_position = models.CharField(max_length=100, blank=True)
    position_start_date = models.DateField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Member'
        verbose_name_plural = 'Members'
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user.member_id}"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def branch(self):
        return self.user.branch
    
    @property
    def member_id(self):
        return self.user.member_id


class MemberDocument(TimeStampedModel):
    """Documents uploaded for/by members."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='documents')
    
    class DocumentType(models.TextChoices):
        ID_CARD = 'id_card', 'ID Card'
        BAPTISM_CERT = 'baptism_cert', 'Baptism Certificate'
        MARRIAGE_CERT = 'marriage_cert', 'Marriage Certificate'
        TRANSFER_LETTER = 'transfer_letter', 'Transfer Letter'
        OTHER = 'other', 'Other'
    
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='member_documents/')
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.member.full_name} - {self.title}"


class DeceasedMember(TimeStampedModel):
    """Track deceased members and related funeral contributions."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Can be linked to existing member or just name
    member = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deceased_record'
    )
    
    # For non-members or relatives
    name = models.CharField(max_length=200)
    relationship_to_member = models.CharField(max_length=100, blank=True)
    related_member = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deceased_relatives'
    )
    
    branch = models.ForeignKey(
        'core.Branch',
        on_delete=models.PROTECT,
        related_name='deceased_records'
    )
    
    date_of_death = models.DateField()
    date_of_burial = models.DateField(null=True, blank=True)
    
    # Funeral contribution target
    contribution_target = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    contribution_collected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_contribution_closed = models.BooleanField(default=False)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date_of_death']
        verbose_name = 'Deceased Member'
        verbose_name_plural = 'Deceased Members'
    
    def __str__(self):
        return f"{self.name} - {self.date_of_death}"
    
    @property
    def outstanding_amount(self):
        return max(0, self.contribution_target - self.contribution_collected)
