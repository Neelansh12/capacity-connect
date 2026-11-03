from django.contrib import admin
from .models import Announcement, Notification, CourseFeedback, TrainerResource

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'announcement_type', 'is_public', 'is_pinned', 'author', 'created_at')
    list_filter = ('announcement_type', 'is_public', 'is_pinned')
    search_fields = ('title', 'content')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('user__username', 'title')

@admin.register(CourseFeedback)
class CourseFeedbackAdmin(admin.ModelAdmin):
    list_display = ('course', 'employee', 'course_rating', 'trainer_rating', 'created_at')
    list_filter = ('course_rating', 'trainer_rating')
    search_fields = ('course__title', 'employee__username')

@admin.register(TrainerResource)
class TrainerResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_by', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'description')

