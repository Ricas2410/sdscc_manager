from django.contrib import admin
from .models import MonthlyReport, MonthlyReportItem
from .models_hierarchy import AreaFinancialReport, DistrictFinancialReport

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

@admin.register(AreaFinancialReport)
class AreaFinancialReportAdmin(admin.ModelAdmin):
    list_display = ('area', 'month', 'year', 'total_income', 'total_expenditure', 'closing_balance', 'is_generated')
    list_filter = ('is_generated', 'year', 'month', 'area')
    search_fields = ('area__name',)
    readonly_fields = ('generated_by', 'generated_at')
    
    fieldsets = (
        ('Period Info', {'fields': ('area', 'month', 'year')}),
        ('Balance', {'fields': ('opening_balance', 'closing_balance')}),
        ('Income', {'fields': ('contributions_received', 'remittances_received', 'transfers_received', 'total_income')}),
        ('Expenditure', {'fields': ('expenditures', 'transfers_sent', 'total_expenditure')}),
        ('Report Status', {'fields': ('is_generated', 'generated_by', 'generated_at')}),
        ('Report Data', {'fields': ('report_data',)}),
    )

@admin.register(DistrictFinancialReport)
class DistrictFinancialReportAdmin(admin.ModelAdmin):
    list_display = ('district', 'month', 'year', 'total_income', 'total_expenditure', 'closing_balance', 'is_generated')
    list_filter = ('is_generated', 'year', 'month', 'district__area')
    search_fields = ('district__name',)
    readonly_fields = ('generated_by', 'generated_at')
    
    fieldsets = (
        ('Period Info', {'fields': ('district', 'month', 'year')}),
        ('Balance', {'fields': ('opening_balance', 'closing_balance')}),
        ('Income', {'fields': ('contributions_received', 'remittances_received', 'transfers_received', 'total_income')}),
        ('Expenditure', {'fields': ('expenditures', 'transfers_sent', 'total_expenditure')}),
        ('Report Status', {'fields': ('is_generated', 'generated_by', 'generated_at')}),
        ('Report Data', {'fields': ('report_data',)}),
    )
