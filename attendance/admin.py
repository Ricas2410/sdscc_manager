from django.contrib import admin
from .models import ServiceType, AttendanceSession, AttendanceRecord, VisitorRecord


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'day', 'default_start_time', 'is_active')
    list_filter = ('day', 'is_active')
    search_fields = ('name', 'code')


class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    extra = 0
    raw_id_fields = ('member',)


class VisitorRecordInline(admin.TabularInline):
    model = VisitorRecord
    extra = 0


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ('branch', 'service_type', 'date', 'total_attendance', 'visitors_count')
    list_filter = ('service_type', 'date', 'branch')
    search_fields = ('branch__name', 'sermon_topic', 'preacher__first_name')
    inlines = [AttendanceRecordInline, VisitorRecordInline]
    date_hierarchy = 'date'


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('member', 'session', 'status', 'check_in_time')
    list_filter = ('status', 'session__date')
    search_fields = ('member__first_name', 'member__last_name', 'member__member_id')
    raw_id_fields = ('member', 'session')


@admin.register(VisitorRecord)
class VisitorRecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'session', 'is_first_time', 'interested_in_membership')
    list_filter = ('is_first_time', 'interested_in_membership', 'session__date')
    search_fields = ('name', 'phone', 'email')