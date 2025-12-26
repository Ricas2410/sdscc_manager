"""
Auditing Models - Audit logs, trails, and reporting
"""

import uuid
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from core.models import TimeStampedModel


class AuditLog(models.Model):
    """Generic audit log for tracking all changes in the system."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Who made the change
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs'
    )
    user_name = models.CharField(max_length=200, blank=True)  # Backup in case user is deleted
    user_role = models.CharField(max_length=50, blank=True)
    
    # What was changed (generic relation)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=50)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Type of action
    class Action(models.TextChoices):
        CREATE = 'create', 'Created'
        UPDATE = 'update', 'Updated'
        DELETE = 'delete', 'Deleted'
        VIEW = 'view', 'Viewed'
        APPROVE = 'approve', 'Approved'
        REJECT = 'reject', 'Rejected'
        LOGIN = 'login', 'Logged In'
        LOGOUT = 'logout', 'Logged Out'
        EXPORT = 'export', 'Exported'
        IMPORT = 'import', 'Imported'
    
    action = models.CharField(max_length=20, choices=Action.choices)
    
    # Change details
    object_repr = models.CharField(max_length=500, blank=True)
    changes = models.JSONField(default=dict, blank=True)  # Before/after values
    reason = models.TextField(blank=True)
    
    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Hierarchy context
    branch = models.ForeignKey(
        'core.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs'
    )
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user_name or 'System'} - {self.get_action_display()} - {self.object_repr}"
    
    @classmethod
    def log(cls, user, action, obj, changes=None, reason='', request=None):
        """Helper method to create audit log entry."""
        log = cls(
            user=user,
            user_name=user.get_full_name() if user else 'System',
            user_role=user.role if user else '',
            content_type=ContentType.objects.get_for_model(obj),
            object_id=str(obj.pk),
            object_repr=str(obj)[:500],
            action=action,
            changes=changes or {},
            reason=reason,
        )
        
        if request:
            log.ip_address = cls.get_client_ip(request)
            log.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        if hasattr(obj, 'branch'):
            log.branch = obj.branch
        
        log.save()
        return log
    
    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class FinancialAuditReport(TimeStampedModel):
    """Annual or periodic financial audit reports."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    title = models.CharField(max_length=300)
    fiscal_year = models.ForeignKey('core.FiscalYear', on_delete=models.PROTECT, related_name='audit_reports')
    
    class ReportType(models.TextChoices):
        ANNUAL = 'annual', 'Annual Audit Report'
        QUARTERLY = 'quarterly', 'Quarterly Report'
        MONTHLY = 'monthly', 'Monthly Report'
        SPECIAL = 'special', 'Special Investigation'
    
    report_type = models.CharField(max_length=20, choices=ReportType.choices, default=ReportType.ANNUAL)
    
    # Scope
    class Scope(models.TextChoices):
        MISSION = 'mission', 'Mission (National)'
        AREA = 'area', 'Area'
        DISTRICT = 'district', 'District'
        BRANCH = 'branch', 'Branch'
    
    scope = models.CharField(max_length=20, choices=Scope.choices, default=Scope.MISSION)
    
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_reports')
    district = models.ForeignKey('core.District', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_reports')
    area = models.ForeignKey('core.Area', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_reports')
    
    # Period covered
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Financial Summary
    total_income = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_expenditure = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    net_balance = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    
    # Report content
    summary = models.TextField(blank=True)
    findings = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    
    # Attachments
    report_file = models.FileField(upload_to='audit_reports/', blank=True, null=True)
    
    # Auditor info
    auditor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='authored_audit_reports'
    )
    auditor_signature = models.ImageField(upload_to='auditor_signatures/', blank=True, null=True)
    
    # Status
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        UNDER_REVIEW = 'review', 'Under Review'
        APPROVED = 'approved', 'Approved'
        PUBLISHED = 'published', 'Published'
        REJECTED = 'rejected', 'Rejected'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_audit_reports'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Visibility
    visible_to_members = models.BooleanField(default=False)
    visible_to_branch_admins = models.BooleanField(default=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-period_end', '-created_at']
        verbose_name = 'Financial Audit Report'
        verbose_name_plural = 'Financial Audit Reports'
    
    def __str__(self):
        return f"{self.title} - {self.fiscal_year}"


class AuditFlag(TimeStampedModel):
    """Flags for potential issues detected during auditing."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class FlagType(models.TextChoices):
        LATE_ENTRY = 'late_entry', 'Late Entry'
        DUPLICATE = 'duplicate', 'Possible Duplicate'
        MISSING_RECEIPT = 'missing_receipt', 'Missing Receipt'
        AMOUNT_ANOMALY = 'amount_anomaly', 'Unusual Amount'
        MISSING_REMITTANCE = 'missing_remittance', 'Missing Remittance'
        OVERSPENDING = 'overspending', 'Overspending'
        CASHFLOW_IMBALANCE = 'cashflow', 'Cashflow Imbalance'
        UNAUTHORIZED = 'unauthorized', 'Unauthorized Action'
        OTHER = 'other', 'Other'
    
    flag_type = models.CharField(max_length=30, choices=FlagType.choices)
    
    # Related object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=50)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='medium')
    
    # Hierarchy
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_flags')
    
    # Resolution
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        UNDER_REVIEW = 'review', 'Under Review'
        RESOLVED = 'resolved', 'Resolved'
        DISMISSED = 'dismissed', 'Dismissed'
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_flags'
    )
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Audit Flag'
        verbose_name_plural = 'Audit Flags'
    
    def __str__(self):
        return f"{self.get_flag_type_display()} - {self.severity}"
