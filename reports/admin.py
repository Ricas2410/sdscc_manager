from django.contrib import admin
from .models import MonthlyReport, MonthlyReportItem

class MonthlyReportItemInline(admin.TabularInline):
    model = MonthlyReportItem
    extra = 0

@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ('branch', 'month', 'year', 'status', 'total_contributions', 'total_expenditure', 'branch_balance')
    list_filter = ('status', 'year', 'month', 'branch__district__area')
    search_fields = ('branch__name',)
    inlines = [MonthlyReportItemInline]
    readonly_fields = ('submitted_by', 'submitted_at', 'approved_by', 'approved_at')
    
    fieldsets = (
        ('Period Info', {'fields': ('branch', 'fiscal_year', 'month', 'year', 'status')}),
        ('Attendance', {'fields': ('total_services', 'total_attendance', 'average_attendance', 'visitors_count', 'new_members')}),
        ('Financial Summary', {'fields': ('total_contributions', 'total_expenditure', 'branch_balance')}),
        ('Mission Remittance', {'fields': ('mission_remittance_due', 'mission_remittance_paid', 'mission_remittance_balance')}),
        ('Approval', {'fields': ('submitted_by', 'submitted_at', 'approved_by', 'approved_at')}),
        ('Payment', {'fields': ('payment_date', 'payment_reference', 'payment_method')}),
        ('Notes', {'fields': ('notes', 'attachment')}),
    )
