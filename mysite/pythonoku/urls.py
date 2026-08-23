from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *


urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', EmailOrUsernameTokenObtainPairView.as_view(), name='token_obtain'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ── Users ─────────────────────────────────────────────────────────────
    path('users/', UserProfileListView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserProfileDetailView.as_view(), name='user_detail'),
    path('users/me/', MeView.as_view(), name='me'),

    # ── Leaderboard ───────────────────────────────────────────────────────
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),

    # ── Courses ───────────────────────────────────────────────────────────
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),

    # ── Lessons ───────────────────────────────────────────────────────────
    path('courses/<int:course_id>/lessons/', LessonListView.as_view(), name='lesson_list'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson_detail'),

    # ── Progress ──────────────────────────────────────────────────────────
    path('progress/', UserProgressView.as_view(), name='my_progress'),
    path('lessons/<int:lesson_id>/complete/', CompleteLessonView.as_view(), name='complete_lesson'),

    # ── Comments ──────────────────────────────────────────────────────────
    path('lessons/<int:lesson_id>/comments/', LessonCommentListView.as_view(), name='lesson_comments'),
    path('comments/<int:pk>/', LessonCommentDeleteView.as_view(), name='comment_delete'),

    # ── Achievements ──────────────────────────────────────────────────────
    path('achievements/', AllAchievementsView.as_view(), name='achievements'),
    path('achievements/me/', MyAchievementsView.as_view(), name='my_achievements'),

    # ── Forum ─────────────────────────────────────────────────────────────
    path('forum/', ForumPostListView.as_view(), name='forum_list'),
    path('forum/<int:pk>/', ForumPostDetailView.as_view(), name='forum_detail'),
    path('forum/<int:post_id>/replies/', ForumReplyListCreateView.as_view(), name='forum_replies'),
    path('forum/reply/', ForumReplyCreateView.as_view(), name='forum_reply'),

    # ── Schedule ──────────────────────────────────────────────────────────
    path('schedule/', ScheduleListView.as_view(), name='schedule_list'),
    path('schedule/<int:pk>/', ScheduleDetailView.as_view(), name='schedule_detail'),

    # ── AI Assistant ──────────────────────────────────────────────────────
    path('ai/chat/', AIChatView.as_view(), name='ai_chat'),
    path('ai/clear/', AIClearHistoryView.as_view(), name='ai_clear'),

# ── Тесты ─────────────────────────────────────────────────────────────────
    path('lessons/<int:lesson_id>/quizzes/', QuizListView.as_view(), name='quiz_list'),
    path('quizzes/<int:pk>/', QuizDetailView.as_view(), name='quiz_detail'),
    path('lessons/<int:lesson_id>/quiz/<int:quiz_id>/answer/', AnswerQuizView.as_view(), name='quiz_answer'),

    # ── Домашние задания ───────────────────────────────────────────────────────
    path('lessons/<int:lesson_id>/homework/', HomeworkSubmitView.as_view(), name='homework'),
    path('homework/', HomeworkListStudentView.as_view(), name='my_homeworks'),
    path('teacher/homeworks/', HomeworkListTeacherView.as_view(), name='hw_list'),
    path('teacher/homeworks/<int:pk>/review/', HomeworkReviewView.as_view(), name='hw_review'),
    path('homework/tasks/', CodingTaskListCreateView.as_view(), name='coding_task_list'),
    path('homework/tasks/<int:pk>/', CodingTaskDetailView.as_view(), name='coding_task_detail'),
    path('homework/tasks/<int:pk>/check/', CodingTaskCheckView.as_view(), name='coding_task_check'),
    path('homework/submissions/', CodingSubmissionListView.as_view(), name='coding_submission_list'),

    # ── Уведомления ───────────────────────────────────────────────────────────
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read/', NotificationReadView.as_view(), name='notif_read'),
    path('notifications/read-all/', NotificationReadAllView.as_view(), name='notif_read_all'),

    # ── Аналитика ─────────────────────────────────────────────────────────────
    path('teacher/analytics/', TeacherAnalyticsView.as_view(), name='teacher_analytics'),

    path('password_reset/', request_password_reset, name='password_reset_request'),
    path('password_reset/verify_code/', verify_reset_code, name='verify_reset_code'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]
