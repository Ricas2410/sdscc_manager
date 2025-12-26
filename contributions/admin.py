from django.contrib import admin
from .models import ContributionType, Contribution, Remittance, TitheCommission

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

