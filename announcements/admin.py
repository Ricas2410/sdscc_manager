from django.contrib import admin
from .models import Announcement, AnnouncementAttachment, Event

class AnnouncementAttachmentInline(admin.TabularInline):
    model = AnnouncementAttachment
    extra = 1

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'scope', 'priority', 'publish_date', 'expiry_date', 'is_published', 'is_pinned')
    list_filter = ('scope', 'priority', 'is_published', 'is_pinned', 'publish_date')
    search_fields = ('title', 'content')
    inlines = [AnnouncementAttachmentInline]
    date_hierarchy = 'publish_date'

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'start_date', 'start_time', 'location', 'scope', 'is_published')
    list_filter = ('event_type', 'scope', 'is_published', 'start_date')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'start_date'
