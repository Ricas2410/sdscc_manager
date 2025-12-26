from django.contrib import admin
from .models import GroupCategory, Group, GroupMembership, GroupMeeting

@admin.register(GroupCategory)
class GroupCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'is_active')
    list_filter = ('category_type', 'is_active')
    search_fields = ('name',)

class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 0
    raw_id_fields = ('member',)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'scope', 'leader', 'member_count', 'is_active')
    list_filter = ('scope', 'category', 'is_active')
    search_fields = ('name', 'code', 'leader__first_name')
    inlines = [GroupMembershipInline]
    raw_id_fields = ('leader', 'assistant_leader', 'secretary', 'branch', 'district', 'area')

@admin.register(GroupMeeting)
class GroupMeetingAdmin(admin.ModelAdmin):
    list_display = ('group', 'date', 'start_time', 'attendance_count', 'is_cancelled')
    list_filter = ('date', 'is_cancelled', 'group')
    search_fields = ('title', 'agenda')
    date_hierarchy = 'date'
