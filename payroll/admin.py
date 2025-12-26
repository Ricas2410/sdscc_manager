from django.contrib import admin
from .models import (
    StaffPayrollProfile, AllowanceType, DeductionType, StaffAllowance,
    StaffDeduction, PayrollRun, PaySlip, StaffLoan
)

class StaffAllowanceInline(admin.TabularInline):
    model = StaffAllowance
    extra = 0

class StaffDeductionInline(admin.TabularInline):
    model = StaffDeduction
    extra = 0

@admin.register(StaffPayrollProfile)
class StaffPayrollProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'position', 'employment_type', 'base_salary', 'is_active')
    list_filter = ('employment_type', 'is_active', 'department')
    search_fields = ('user__first_name', 'user__last_name', 'employee_id', 'position')
    inlines = [StaffAllowanceInline, StaffDeductionInline]
    raw_id_fields = ('user',)

@admin.register(AllowanceType)
class AllowanceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_taxable', 'is_active')
    list_filter = ('is_taxable', 'is_active')
    search_fields = ('name', 'code')

@admin.register(DeductionType)
class DeductionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')

class PaySlipInline(admin.TabularInline):
    model = PaySlip
    extra = 0
    readonly_fields = ('base_salary', 'total_allowances', 'total_deductions', 'net_pay')
    can_delete = False

@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'fiscal_year', 'status', 'total_net_pay', 'processed_at')
    list_filter = ('status', 'year', 'month')
    inlines = [PaySlipInline]
    readonly_fields = ('processed_by', 'processed_at', 'approved_by', 'approved_at')

@admin.register(StaffLoan)
class StaffLoanAdmin(admin.ModelAdmin):
    list_display = ('staff', 'loan_type', 'amount', 'outstanding_amount', 'status', 'loan_date')
    list_filter = ('status', 'loan_type', 'loan_date')
    search_fields = ('staff__user__first_name', 'staff__employee_id')
