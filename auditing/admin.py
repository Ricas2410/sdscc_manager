from django.contrib import admin

from .models import AuditLog, FinancialAuditReport, AuditFlag


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user_name', 'action', 'object_repr', 'branch')
    list_filter = ('action', 'timestamp', 'branch')
    search_fields = ('user_name', 'object_repr', 'reason')
    readonly_fields = ('timestamp', 'user', 'content_type', 'object_id', 'changes')


@admin.register(FinancialAuditReport)
class FinancialAuditReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'fiscal_year', 'report_type', 'scope', 'status', 'created_at')
    list_filter = ('report_type', 'scope', 'status', 'fiscal_year')
    search_fields = ('title', 'summary', 'findings')


@admin.register(AuditFlag)
class AuditFlagAdmin(admin.ModelAdmin):
    list_display = ('flag_type', 'severity', 'status', 'branch', 'created_at')
    list_filter = ('flag_type', 'severity', 'status', 'branch')
    search_fields = ('description', 'resolution_notes')
