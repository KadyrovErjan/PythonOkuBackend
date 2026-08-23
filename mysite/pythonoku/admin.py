from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    list_display = ['username', 'email', 'xp', 'streak', 'last_activity', 'is_admin']
    fieldsets = UserAdmin.fieldsets + (
        ('PythonOku', {'fields': ('avatar', 'bio', 'xp', 'streak', 'last_activity', 'is_admin')}),
    )

admin.register(Course)(admin.ModelAdmin)
admin.register(Lesson)(admin.ModelAdmin)
admin.register(LessonComment)(admin.ModelAdmin)
admin.register(UserProgress)(admin.ModelAdmin)
admin.register(Achievement)(admin.ModelAdmin)
admin.register(UserAchievement)(admin.ModelAdmin)
admin.register(Schedule)(admin.ModelAdmin)


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'lesson', 'views', 'is_solved', 'created_at']
    list_filter = ['is_solved', 'lesson']
    search_fields = ['title', 'text', 'author__username']
    readonly_fields = ['views', 'created_at']


@admin.register(ForumReply)
class ForumReplyAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'is_best_answer', 'created_at']
    list_filter = ['is_best_answer']
    search_fields = ['text', 'author__username', 'post__title']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'type', 'is_read', 'created_at']
    list_filter = ['type', 'is_read']
    search_fields = ['title', 'text', 'user__username']
    readonly_fields = ['created_at']


@admin.register(CodingTask)
class CodingTaskAdmin(admin.ModelAdmin):
    list_display = ['title_ru', 'lesson', 'order', 'xp_reward', 'is_published']
    list_filter = ['is_published', 'lesson__course', 'lesson']
    search_fields = ['title_ru', 'title_kg', 'description_ru', 'description_kg']
    ordering = ['lesson', 'order']


@admin.register(CodingSubmission)
class CodingSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'task', 'status', 'attempts', 'passed_at', 'updated_at']
    list_filter = ['status', 'task__lesson']
    search_fields = ['student__username', 'task__title_ru', 'code']
    readonly_fields = ['submitted_at', 'updated_at', 'passed_at']
