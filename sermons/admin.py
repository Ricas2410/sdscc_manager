from django.contrib import admin
from .models import SermonCategory, Sermon, SermonNote, SermonBookmark

@admin.register(SermonCategory)
class SermonCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Sermon)
class SermonAdmin(admin.ModelAdmin):
    list_display = ('title', 'preacher', 'sermon_date', 'category', 'media_type', 'is_published', 'view_count')
    list_filter = ('is_published', 'media_type', 'category', 'sermon_date')
    search_fields = ('title', 'content', 'preacher__first_name', 'preacher_name')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'sermon_date'
    raw_id_fields = ('preacher', 'branch')

@admin.register(SermonNote)
class SermonNoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'sermon', 'is_private', 'created_at')
    list_filter = ('is_private', 'created_at')
    search_fields = ('content', 'user__first_name', 'sermon__title')

@admin.register(SermonBookmark)
class SermonBookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'sermon', 'created_at')
    list_filter = ('created_at',)
