from django.contrib import admin
from .models import ContributionType, Contribution, Remittance, TitheCommission
from .models_opening_balance import OpeningBalance
from .models_transfers import HierarchyTransfer
from .models_remittance import HierarchyRemittance

@admin.register(ContributionType)
class ContributionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'scope', 'is_active')
    list_filter = ('category', 'scope', 'is_active')
    search_fields = ('name',)

@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('member', 'amount', 'contribution_type', 'branch', 'date', 'fiscal_year')
    list_filter = ('contribution_type', 'branch__district__area', 'date', 'fiscal_year')
    search_fields = ('member__member_id', 'member__first_name', 'member__last_name', 'reference')
    date_hierarchy = 'date'
    autocomplete_fields = ['member', 'branch']

@admin.register(Remittance)
class RemittanceAdmin(admin.ModelAdmin):
    list_display = ('branch', 'month', 'year', 'amount_due', 'amount_sent', 'status')
    list_filter = ('status', 'branch__district__area', 'year', 'month')
    search_fields = ('branch__name', 'payment_reference')
    date_hierarchy = 'created_at'

@admin.register(TitheCommission)
class TitheCommissionAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'branch', 'commission_amount', 'month', 'year', 'status')
    list_filter = ('status', 'year', 'month')
    search_fields = ('recipient__first_name', 'branch__name')

@admin.register(OpeningBalance)
class OpeningBalanceAdmin(admin.ModelAdmin):
    list_display = ('level', 'branch', 'contribution_type', 'amount', 'date', 'status')
    list_filter = ('level', 'status', 'date')
    search_fields = ('branch__name', 'description')
    date_hierarchy = 'date'
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only for new objects
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(HierarchyTransfer)
class HierarchyTransferAdmin(admin.ModelAdmin):
    list_display = ('source_level', 'destination_level', 'amount', 'date', 'purpose', 'status')
    list_filter = ('source_level', 'destination_level', 'purpose', 'status', 'date')
    search_fields = ('description', 'reference')
    date_hierarchy = 'date'
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
    
    fieldsets = (
        ('Transfer Details', {
            'fields': ('amount', 'date', 'purpose', 'description', 'reference', 'status')
        }),
        ('Source', {
            'fields': ('source_level', 'source_area', 'source_district', 'source_branch')
        }),
        ('Destination', {
            'fields': ('destination_level', 'destination_area', 'destination_district', 'destination_branch')
        }),
        ('Documentation', {
            'fields': ('documentation',)
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_at')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only for new objects
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(HierarchyRemittance)
class HierarchyRemittanceAdmin(admin.ModelAdmin):
    list_display = ('branch', 'destination_level', 'get_destination_name', 'amount_due', 'amount_sent', 'month', 'year', 'status')
    list_filter = ('destination_level', 'status', 'year', 'month', 'branch__district__area')
    search_fields = ('branch__name', 'payment_reference', 'notes')
    date_hierarchy = 'payment_date'
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
    
    fieldsets = (
        ('Remittance Details', {
            'fields': ('branch', 'destination_level', 'area', 'district', 'month', 'year')
        }),
        ('Financial', {
            'fields': ('amount_due', 'amount_sent', 'status')
        }),
        ('Payment Information', {
            'fields': ('payment_date', 'payment_method', 'payment_reference', 'payment_proof')
        }),
        ('Verification', {
            'fields': ('verified_by', 'verified_at', 'verification_notes')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at')
        }),
    )
    
    def get_destination_name(self, obj):
        if obj.destination_level == 'area' and obj.area:
            return obj.area.name
        elif obj.destination_level == 'district' and obj.district:
            return obj.district.name
        return '-'
    get_destination_name.short_description = 'Destination'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only for new objects
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

