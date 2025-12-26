from django.contrib import admin
from django.contrib.auth.models import Group as DjangoGroup
from .models import (
    SiteSettings, Area, District, Branch, FiscalYear, MonthlyClose,
    Notification, PrayerRequest, PrayerInteraction, Visitor, VisitorFollowUp,
    SpecialDateReminder
)
from .calendar_models import CalendarEvent, YearlyCalendar

# Customize Admin Site
admin.site.site_header = 'SDSCC Management Portal'
admin.site.site_title = 'SDSCC Admin'
admin.site.index_title = 'Church Administration'

# Unregister default Group model if not needed
# admin.site.unregister(DjangoGroup)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General Info', {'fields': ('site_name', 'site_description', 'logo')}),
        ('Contact', {'fields': ('contact_email', 'contact_phone', 'address')}),
        ('Features', {'fields': ('maintenance_mode', 'enable_registration')}),
        ('Social Media', {'fields': ('facebook_url', 'twitter_url', 'youtube_url')}),
    )
    
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

class BranchInline(admin.TabularInline):
    model = Branch
    extra = 0
    show_change_link = True

class DistrictInline(admin.TabularInline):
    model = District
    extra = 0
    show_change_link = True

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'district_count')
    search_fields = ('name', 'code')
    inlines = [DistrictInline]
    
    def district_count(self, obj):
        return obj.districts.count()

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'area', 'branch_count')
    list_filter = ('area',)
    search_fields = ('name', 'code')
    inlines = [BranchInline]
    
    def branch_count(self, obj):
        return obj.branches.count()

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'district', 'pastor', 'is_active')
    list_filter = ('district__area', 'district', 'is_active')
    search_fields = ('name', 'code', 'pastor__first_name')
    list_editable = ('is_active',)

@admin.register(FiscalYear)
class FiscalYearAdmin(admin.ModelAdmin):
    list_display = ('year', 'start_date', 'end_date', 'is_current', 'is_closed')
    list_filter = ('is_current', 'is_closed')
    ordering = ('-year',)

@admin.register(MonthlyClose)
class MonthlyCloseAdmin(admin.ModelAdmin):
    list_display = ('branch', 'month', 'year', 'total_tithe', 'is_closed')
    list_filter = ('is_closed', 'year', 'month', 'branch')
    search_fields = ('branch__name',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient__first_name')

class PrayerInteractionInline(admin.TabularInline):
    model = PrayerInteraction
    extra = 0
    readonly_fields = ('prayed_at',)

@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'requester', 'branch', 'status', 'visibility_scope', 'created_at')
    list_filter = ('status', 'visibility_scope', 'branch')
    search_fields = ('title', 'description', 'requester__first_name')
    inlines = [PrayerInteractionInline]

class VisitorFollowUpInline(admin.TabularInline):
    model = VisitorFollowUp
    extra = 0

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'first_visit_date', 'branch', 'status')
    list_filter = ('status', 'first_visit_date', 'branch')
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    inlines = [VisitorFollowUpInline]

@admin.register(SpecialDateReminder)
class SpecialDateReminderAdmin(admin.ModelAdmin):
    list_display = ('user', 'reminder_type', 'date', 'notify_member')
    list_filter = ('reminder_type', 'notify_member')
    search_fields = ('user__first_name', 'user__last_name')

@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'start_date', 'scope', 'is_published')
    list_filter = ('event_type', 'scope', 'is_published', 'start_date')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'start_date'

@admin.register(YearlyCalendar)
class YearlyCalendarAdmin(admin.ModelAdmin):
    list_display = ('year', 'theme', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('year', 'theme')
