from django.contrib import admin
from .models import (
    ExpenditureCategory, Expenditure, UtilityBill, WelfarePayment, Asset
)

@admin.register(ExpenditureCategory)
class ExpenditureCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category_type', 'scope', 'is_active')
    list_filter = ('category_type', 'scope', 'is_active')
    search_fields = ('name', 'code')

@admin.register(Expenditure)
class ExpenditureAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'date', 'category', 'level', 'status', 'location_name')
    list_filter = ('status', 'level', 'category', 'date', 'fiscal_year')
    search_fields = ('title', 'description', 'vendor', 'reference_number')
    date_hierarchy = 'date'
    raw_id_fields = ('branch', 'district', 'area', 'approved_by')

@admin.register(UtilityBill)
class UtilityBillAdmin(admin.ModelAdmin):
    list_display = ('branch', 'utility_type', 'month', 'year', 'amount', 'is_paid')
    list_filter = ('utility_type', 'is_paid', 'year', 'month')
    search_fields = ('branch__name', 'account_number', 'meter_number')

@admin.register(WelfarePayment)
class WelfarePaymentAdmin(admin.ModelAdmin):
    list_display = ('recipient_name', 'welfare_type', 'amount', 'date', 'branch')
    list_filter = ('welfare_type', 'date', 'branch')
    search_fields = ('recipient_name', 'description')
    date_hierarchy = 'date'

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'level', 'purchase_date', 'current_value')
    list_filter = ('status', 'category', 'level')
    search_fields = ('name', 'description', 'serial_number')
