from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, LoginHistory

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('member_id', 'get_full_name', 'role', 'branch', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'branch__district__area', 'branch')
    search_fields = ('member_id', 'first_name', 'last_name', 'email', 'phone')
    ordering = ('member_id',)
    inlines = (UserProfileInline,)
    
    fieldsets = (
        (None, {'fields': ('member_id', 'password', 'pin')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'other_names', 'email', 'phone', 'gender', 'date_of_birth', 'profile_picture')}),
        ('Church Assignment', {'fields': ('role', 'pastoral_rank', 'branch', 'managed_area', 'managed_district')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    def date_joined(self, obj):
        return obj.created_at
    date_joined.short_description = 'Joined'

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'ip_address', 'success')
    list_filter = ('success', 'timestamp')
    search_fields = ('user__member_id', 'user__first_name', 'user__last_name', 'ip_address')
    readonly_fields = ('user', 'timestamp', 'ip_address', 'user_agent', 'success')
    
    def has_add_permission(self, request):
        return False

