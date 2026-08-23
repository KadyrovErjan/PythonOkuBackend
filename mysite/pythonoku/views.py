import logging
import math

from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.db.models import F, Prefetch, Q
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.throttling import AnonRateThrottle
from django_rest_passwordreset.serializers import EmailSerializer
from django_rest_passwordreset.signals import reset_password_token_created
from django_rest_passwordreset.views import (
    clear_expired_tokens,
    generate_token_for_email,
)


from .models import *
from .serializers import *
from .permissions import (
    IsSelfOrTeacherAdmin,
    IsStudent,
    IsTeacherAdmin,
    IsTeacherAdminOrReadOnly,
    has_teacher_access,
)
from .activity import touch_learning_streak
from .notifications import queue_notification, queue_notifications

logger = logging.getLogger(__name__)

WATCH_REQUIRED_RATIO = 0.95
WATCH_SERVER_GRACE_SECONDS = 6
WATCH_FIRST_UPDATE_ALLOWANCE_SECONDS = 15


def _to_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalise_watch_ranges(ranges, total_seconds):
    if not isinstance(ranges, list) or total_seconds <= 0:
        return []

    cleaned = []
    for item in ranges[:500]:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            continue
        start = max(0, min(total_seconds, _to_int(item[0], 0)))
        end = max(0, min(total_seconds, _to_int(item[1], 0)))
        if end > start:
            cleaned.append([start, end])

    cleaned.sort(key=lambda item: item[0])
    merged = []
    for start, end in cleaned:
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return merged


def _watch_ranges_duration(ranges):
    return sum(max(0, end - start) for start, end in ranges)


def _merge_watch_ranges(*range_groups, total_seconds):
    combined = []
    for ranges in range_groups:
        if isinstance(ranges, list):
            combined.extend(ranges)
    return _normalise_watch_ranges(combined, total_seconds)


def _add_watch_ranges_with_limit(existing_ranges, incoming_ranges, total_seconds, max_duration):
    accepted = _normalise_watch_ranges(existing_ranges, total_seconds)
    max_duration = max(0, min(total_seconds, int(max_duration)))

    for start, end in _normalise_watch_ranges(incoming_ranges, total_seconds):
        full = _merge_watch_ranges(accepted, [[start, end]], total_seconds=total_seconds)
        if _watch_ranges_duration(full) <= max_duration:
            accepted = full
            continue

        for second in range(start, end):
            if _watch_ranges_duration(accepted) >= max_duration:
                break
            partial = _merge_watch_ranges(accepted, [[second, min(second + 1, end)]], total_seconds=total_seconds)
            if _watch_ranges_duration(partial) > max_duration:
                break
            accepted = partial
        break

    return accepted


def _required_watch_seconds(total_seconds):
    if total_seconds <= 0:
        return 0
    return min(total_seconds, max(1, math.ceil(total_seconds * WATCH_REQUIRED_RATIO)))


def _lesson_video_urls(lesson):
    urls = []
    raw_urls = lesson.video_urls if isinstance(lesson.video_urls, list) else []
    for item in raw_urls:
        url = str(item or '').strip()
        if url and url not in urls:
            urls.append(url)

    legacy_url = str(lesson.youtube_url or '').strip()
    if legacy_url and legacy_url not in urls:
        urls.insert(0, legacy_url)

    return urls


# ── Auth ──────────────────────────────────────────────────────────────────────

class PasswordResetThrottle(AnonRateThrottle):
    rate = '5/hour'


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([PasswordResetThrottle])
def request_password_reset(request):
    serializer = EmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    if settings.EMAIL_BACKEND.endswith('console.EmailBackend'):
        return Response({
            'detail': (
                'Отправка почты не настроена. Добавьте EMAIL_HOST_USER и '
                'EMAIL_HOST_PASSWORD в файл mysite/.env и перезапустите сервер.'
            )
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    clear_expired_tokens()
    token = generate_token_for_email(
        email=serializer.validated_data['email'],
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        ip_address=request.META.get('REMOTE_ADDR', ''),
    )

    try:
        if token:
            reset_password_token_created.send(
                sender=request_password_reset,
                instance=request_password_reset,
                reset_password_token=token,
            )
    except Exception:
        logger.exception('Password reset email delivery failed')
        return Response({
            'detail': (
                'Gmail отклонил отправку. Проверьте адрес и Google App Password '
                'в mysite/.env, затем перезапустите сервер.'
            )
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response({
        'status': 'OK',
        'message': 'Если аккаунт существует, письмо с кодом отправлено.',
    })

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserProfileDetailSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailOrUsernameTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailOrUsernameTokenObtainPairSerializer


# ── Users ─────────────────────────────────────────────────────────────────────

class UserProfileListView(generics.ListAPIView):
    serializer_class = UserProfileListSerializer
    permission_classes = [IsTeacherAdmin]

    def get_queryset(self):
        return UserProfile.objects.filter(
            is_admin=False, is_staff=False, is_superuser=False
        ).order_by('username')


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileDetailSerializer
    permission_classes = [IsAuthenticated, IsSelfOrTeacherAdmin]



@api_view(['POST'])
@permission_classes([AllowAny])
def verify_reset_code(request):
    serializer = VerifyResetCodeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Пароль успешно сброшен.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserProfileDetailSerializer(request.user).data)

    def patch(self, request):
        serializer = UserProfileDetailSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ── Leaderboard ───────────────────────────────────────────────────────────────

class LeaderboardView(generics.ListAPIView):
    serializer_class = LeaderboardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(
            is_admin=False, is_staff=False, is_superuser=False
        ).order_by('-xp')[:50]


# ── Courses ───────────────────────────────────────────────────────────────────

class CourseListView(generics.ListCreateAPIView):
    serializer_class = CourseListSerializer
    permission_classes = [IsTeacherAdminOrReadOnly]

    def get_queryset(self):
        if has_teacher_access(self.request.user):
            return Course.objects.all()
        return Course.objects.filter(is_published=True)

    def perform_create(self, serializer):
        serializer.save()


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseDetailSerializer
    permission_classes = [IsTeacherAdminOrReadOnly]


# ── Lessons ───────────────────────────────────────────────────────────────────

class LessonListView(generics.ListCreateAPIView):
    serializer_class = LessonListSerializer
    permission_classes = [IsTeacherAdminOrReadOnly]

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        qs = Lesson.objects.filter(course_id=course_id)
        if not has_teacher_access(self.request.user):
            qs = qs.filter(is_published=True)
        return qs

    def perform_create(self, serializer):
        serializer.save(course_id=self.kwargs['course_id'])


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonDetailSerializer
    permission_classes = [IsTeacherAdminOrReadOnly]


# ── Progress ──────────────────────────────────────────────────────────────────

class UserProgressView(generics.ListAPIView):
    serializer_class = UserProgressSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)


class LegacyCompleteLessonView(APIView):
    """Ученик отмечает урок как выполненный — начисляем XP"""
    permission_classes = [IsStudent]

    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response({'error': 'Урок не найден'}, status=404)

        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )

        if not progress.completed:
            progress.completed = True
            progress.completed_at = timezone.now()
            progress.code_submitted = request.data.get('code', '')
            progress.save()

            # Начисляем XP
            request.user.xp += lesson.xp_reward
            request.user.save()

            return Response({
                'message': f'+{lesson.xp_reward} XP получено!',
                'xp': request.user.xp
            })

        return Response({'message': 'Урок уже выполнен', 'xp': request.user.xp})


# ── Comments ──────────────────────────────────────────────────────────────────

class LessonCommentListView(generics.ListCreateAPIView):
    serializer_class = LessonCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Только корневые комментарии (без parent) — replies вложены внутрь
        return LessonComment.objects.filter(
            lesson_id=self.kwargs['lesson_id'],
            parent=None
        )

    def perform_create(self, serializer):
        lesson = Lesson.objects.get(id=self.kwargs['lesson_id'])
        serializer.save(author=self.request.user, lesson=lesson)


class LessonCommentDeleteView(generics.DestroyAPIView):
    queryset = LessonComment.objects.all()
    serializer_class = LessonCommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        # Удалять может только автор или админ
        if instance.author == self.request.user or self.request.user.is_admin:
            instance.delete()
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Нет доступа')


# ── Achievements ──────────────────────────────────────────────────────────────

class MyAchievementsView(generics.ListAPIView):
    serializer_class = UserAchievementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserAchievement.objects.filter(user=self.request.user)


class AllAchievementsView(generics.ListAPIView):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [IsAuthenticated]


# ── Forum ─────────────────────────────────────────────────────────────────────

class ForumPostListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ForumPostDetailSerializer
        return ForumPostListSerializer

    def get_queryset(self):
        queryset = ForumPost.objects.select_related('author', 'lesson').prefetch_related('replies')
        query = self.request.query_params.get('q')
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(text__icontains=query))
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        touch_learning_streak(self.request.user, reason='forum_post')

        teacher_ids = UserProfile.objects.filter(
            Q(is_admin=True) | Q(is_staff=True) | Q(is_superuser=True)
        ).exclude(pk=self.request.user.pk).values_list('pk', flat=True)
        queue_notifications(
            teacher_ids,
            'system',
            'Новый вопрос на форуме',
            f'{self.request.user.username} создал тему «{post.title}».',
        )


class ForumPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ForumPostDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ForumPost.objects.select_related('author', 'lesson').prefetch_related('replies__author')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        ForumPost.objects.filter(pk=instance.pk).update(views=F('views') + 1)
        instance.refresh_from_db(fields=['views'])
        return Response(self.get_serializer(instance).data)

    def perform_update(self, serializer):
        if self.get_object().author_id != self.request.user.pk and not has_teacher_access(self.request.user):
            raise PermissionDenied('Можно редактировать только свой пост.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author_id != self.request.user.pk and not has_teacher_access(self.request.user):
            raise PermissionDenied('Можно удалить только свой пост.')
        instance.delete()


class ForumReplyListCreateView(generics.ListCreateAPIView):
    serializer_class = ForumReplySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ForumReply.objects.filter(
            post_id=self.kwargs['post_id']
        ).select_related('author').order_by('created_at')

    def perform_create(self, serializer):
        post = ForumPost.objects.select_related('author').get(pk=self.kwargs['post_id'])
        reply = serializer.save(author=self.request.user, post=post)
        touch_learning_streak(self.request.user, reason='forum_reply')

        if post.author_id != self.request.user.pk:
            queue_notification(
                post.author_id,
                'system',
                'Новый ответ на форуме',
                f'{self.request.user.username} ответил в теме «{post.title}».',
            )

        return reply


class ForumReplyCreateView(generics.CreateAPIView):
    serializer_class = ForumReplySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.request.data.get('post')
        post = ForumPost.objects.select_related('author').filter(pk=post_id).first()
        if not post:
            raise PermissionDenied('Нужно указать пост для ответа.')

        reply = serializer.save(author=self.request.user, post=post)
        touch_learning_streak(self.request.user, reason='forum_reply')
        if post.author_id != self.request.user.pk:
            queue_notification(
                post.author_id,
                'system',
                'Новый ответ на форуме',
                f'{self.request.user.username} ответил в теме «{post.title}».',
            )


# ── Schedule ──────────────────────────────────────────────────────────────────

class ScheduleListView(generics.ListCreateAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsTeacherAdminOrReadOnly]


class ScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsTeacherAdminOrReadOnly]



from .serializers import AIMessageSerializer, AIChatInputSerializer
from .models import AIMessage


class AIChatView(APIView):
    """
    POST /api/ai/chat/
    Body: { "message": "Что такое список?", "lesson_id": 3 }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """История чата текущего пользователя (последние 50 сообщений)"""
        lesson_id = request.query_params.get('lesson_id')
        qs = AIMessage.objects.filter(user=request.user)
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        qs = qs.order_by('-created_at')[:50]
        return Response(AIMessageSerializer(reversed(list(qs)), many=True).data)

    def post(self, request):
        serializer = AIChatInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user_message = serializer.validated_data['message']
        lesson_id = serializer.validated_data.get('lesson_id')

        # Загружаем урок если передан
        lesson = None
        if lesson_id:
            try:
                lesson = Lesson.objects.get(id=lesson_id)
            except Lesson.DoesNotExist:
                pass

        # Загружаем последние 10 сообщений для контекста истории
        history_qs = AIMessage.objects.filter(
            user=request.user,
            lesson=lesson
        ).order_by('-created_at')[:10]
        history = list(reversed(list(history_qs)))

        # Сохраняем вопрос пользователя
        AIMessage.objects.create(
            user=request.user,
            lesson=lesson,
            role='user',
            content=user_message
        )

        # Получаем ответ от ИИ
        try:
            from .ai_assistant import chat_with_ai
            ai_response = chat_with_ai(
                user_message=user_message,
                history=history,
                lesson=lesson
            )
        except Exception as e:
            return Response(
                {'error': f'Ошибка ИИ: {str(e)}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Сохраняем ответ ИИ
        AIMessage.objects.create(
            user=request.user,
            lesson=lesson,
            role='assistant',
            content=ai_response
        )

        return Response({
            'message': ai_response,
            'lesson_id': lesson_id
        })


class AIClearHistoryView(APIView):
    """DELETE /api/ai/clear/ — очистить историю чата"""
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        lesson_id = request.query_params.get('lesson_id')
        qs = AIMessage.objects.filter(user=request.user)
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        count = qs.count()
        qs.delete()
        return Response({'deleted': count})


from .models import Quiz, QuizResult, Homework, Notification
from .serializers import (QuizSerializer, QuizResultSerializer,
                          HomeworkSerializer, HomeworkReviewSerializer,
                          NotificationSerializer)


# ── Тесты ─────────────────────────────────────────────────────────────────────

class QuizListView(generics.ListCreateAPIView):
    serializer_class = QuizSerializer
    permission_classes = [IsTeacherAdminOrReadOnly]

    def get_queryset(self):
        return Quiz.objects.filter(lesson_id=self.kwargs['lesson_id'])


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quiz.objects.select_related('lesson', 'lesson__course')
    serializer_class = QuizSerializer
    permission_classes = [IsTeacherAdmin]


class AnswerQuizView(APIView):
    """POST /api/lessons/<id>/quiz/<quiz_id>/answer/"""
    permission_classes = [IsStudent]

    def post(self, request, lesson_id, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id, lesson_id=lesson_id)
        except Quiz.DoesNotExist:
            return Response({'error': 'Тест не найден'}, status=404)

        existing_result = QuizResult.objects.filter(user=request.user, quiz=quiz).first()
        if existing_result:
            return Response({
                'already': True,
                'answer': existing_result.answer,
                'is_correct': existing_result.is_correct,
                'correct': quiz.correct,
                'xp_gained': 0,
                'total_xp': request.user.xp,
                'streak': request.user.streak,
                'streak_updated': False,
                'message': 'Вы уже отвечали на этот вопрос.',
            })

        answer = request.data.get('answer', '').lower()
        if answer not in {'a', 'b', 'c', 'd'}:
            return Response({'error': 'Выберите вариант A, B, C или D'}, status=status.HTTP_400_BAD_REQUEST)

        is_correct = answer == quiz.correct

        QuizResult.objects.create(
            user=request.user, quiz=quiz,
            answer=answer, is_correct=is_correct
        )

        if is_correct:
            request.user.xp += quiz.xp_reward
            request.user.save()

        streak, streak_updated = touch_learning_streak(request.user, reason='quiz_answer')

        return Response({
            'already': False,
            'answer': answer,
            'is_correct': is_correct,
            'correct':    quiz.correct,
            'xp_gained':  quiz.xp_reward if is_correct else 0,
            'total_xp':   request.user.xp,
            'streak': streak,
            'streak_updated': streak_updated,
        })


# ── Домашние задания ───────────────────────────────────────────────────────────

class HomeworkSubmitView(APIView):
    """POST /api/lessons/<id>/homework/ — ученик сдаёт ДЗ"""
    permission_classes = [IsStudent]

    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response({'error': 'Урок не найден'}, status=404)

        hw, created = Homework.objects.get_or_create(
            lesson=lesson, student=request.user,
            defaults={'code': request.data.get('code', '')}
        )
        if not created:
            hw.code   = request.data.get('code', hw.code)
            hw.status = 'pending'
            hw.save()

        # Уведомление учителю (если есть)
        admins = UserProfile.objects.filter(
            Q(is_admin=True) | Q(is_staff=True) | Q(is_superuser=True)
        ).distinct()
        for admin in admins:
            Notification.objects.create(
                user=admin, type='system',
                title='Новое домашнее задание',
                text=f'{request.user.username} сдал ДЗ по уроку «{lesson.title}»'
            )

        return Response(HomeworkSerializer(hw).data)

    def get(self, request, lesson_id):
        """Получить своё ДЗ по уроку"""
        hw = Homework.objects.filter(
            lesson_id=lesson_id, student=request.user
        ).first()
        if not hw:
            return Response({'status': 'not_submitted'})
        return Response(HomeworkSerializer(hw).data)


class HomeworkListTeacherView(generics.ListAPIView):
    """GET /api/teacher/homeworks/ — все ДЗ для учителя"""
    serializer_class = HomeworkSerializer
    permission_classes = [IsTeacherAdmin]

    def get_queryset(self):
        qs = Homework.objects.select_related('student', 'lesson')
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-submitted_at')


class HomeworkListStudentView(generics.ListAPIView):
    """GET /api/homework/ — домашние задания текущего ученика."""
    serializer_class = HomeworkSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return Homework.objects.filter(
            student=self.request.user
        ).select_related('lesson').order_by('-submitted_at')


class HomeworkReviewView(APIView):
    """PATCH /api/teacher/homeworks/<id>/review/ — учитель проверяет ДЗ"""
    permission_classes = [IsTeacherAdmin]

    def patch(self, request, pk):
        try:
            hw = Homework.objects.get(id=pk)
        except Homework.DoesNotExist:
            return Response({'error': 'Не найдено'}, status=404)

        serializer = HomeworkReviewSerializer(hw, data=request.data, partial=True)
        if serializer.is_valid():
            hw = serializer.save(reviewed_at=timezone.now())

            # Уведомление ученику
            Notification.objects.create(
                user=hw.student,
                type='hw_feedback',
                title='Обратная связь по ДЗ',
                text=f'Учитель проверил ваше ДЗ по уроку «{hw.lesson.title}». '
                     f'Статус: {hw.get_status_display()}. {hw.feedback}'
            )

            if hw.status == 'approved':
                hw.student.xp += 20
                hw.student.save()

            return Response(HomeworkSerializer(hw).data)
        return Response(serializer.errors, status=400)


# ── Проверяемые Python-задачи ────────────────────────────────────────────────

class CodingTaskListCreateView(generics.ListCreateAPIView):
    serializer_class = CodingTaskSerializer
    permission_classes = [IsTeacherAdminOrReadOnly]

    def get_queryset(self):
        queryset = CodingTask.objects.select_related('lesson', 'lesson__course')
        if not has_teacher_access(self.request.user):
            queryset = queryset.filter(
                is_published=True,
                lesson__is_published=True,
                lesson__course__is_published=True,
            ).prefetch_related(Prefetch(
                'submissions',
                queryset=CodingSubmission.objects.filter(student=self.request.user),
                to_attr='current_user_submissions',
            ))
        lesson_id = self.request.query_params.get('lesson')
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)
        return queryset


class CodingTaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CodingTaskSerializer
    permission_classes = [IsTeacherAdminOrReadOnly]

    def get_queryset(self):
        queryset = CodingTask.objects.select_related('lesson', 'lesson__course')
        if not has_teacher_access(self.request.user):
            queryset = queryset.filter(is_published=True).prefetch_related(Prefetch(
                'submissions',
                queryset=CodingSubmission.objects.filter(student=self.request.user),
                to_attr='current_user_submissions',
            ))
        return queryset


class CodingTaskCheckView(APIView):
    permission_classes = [IsStudent]

    def post(self, request, pk):
        task = CodingTask.objects.filter(
            pk=pk, is_published=True,
            lesson__is_published=True,
            lesson__course__is_published=True,
        ).select_related('lesson').first()
        if not task:
            return Response({'detail': 'Задача не найдена.'}, status=status.HTTP_404_NOT_FOUND)

        code = request.data.get('code', '')
        if not isinstance(code, str):
            return Response({'code': 'Код должен быть текстом.'}, status=status.HTTP_400_BAD_REQUEST)
        if len(code) > 12_000:
            return Response({'code': 'Код слишком длинный.'}, status=status.HTTP_400_BAD_REQUEST)

        from .code_checker import check_code
        check = check_code(code, task.tests)
        xp_gained = 0

        with transaction.atomic():
            submission, _ = CodingSubmission.objects.select_for_update().get_or_create(
                task=task,
                student=request.user,
                defaults={'code': code},
            )
            first_success = check['passed'] and submission.passed_at is None
            submission.code = code
            submission.status = 'passed' if check['passed'] else 'failed'
            submission.test_results = check['results']
            submission.checker_error = check['error']
            submission.attempts += 1
            if first_success:
                submission.passed_at = timezone.now()
                student = UserProfile.objects.select_for_update().get(pk=request.user.pk)
                student.xp += task.xp_reward
                student.save(update_fields=['xp'])
                xp_gained = task.xp_reward
            submission.save()

        streak = request.user.streak
        streak_updated = False
        if check['passed']:
            streak, streak_updated = touch_learning_streak(request.user, reason='coding_task')

        request.user.refresh_from_db(fields=['xp'])
        data = CodingSubmissionSerializer(submission).data
        data.update({
            'passed': check['passed'],
            'xp_gained': xp_gained,
            'total_xp': request.user.xp,
            'streak': streak,
            'streak_updated': streak_updated,
        })
        return Response(data)


class CodingSubmissionListView(generics.ListAPIView):
    serializer_class = CodingSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CodingSubmission.objects.select_related(
            'student', 'task', 'task__lesson', 'task__lesson__course',
        )
        if not has_teacher_access(self.request.user):
            queryset = queryset.filter(student=self.request.user)
        status_filter = self.request.query_params.get('status')
        if status_filter in {'passed', 'failed'}:
            queryset = queryset.filter(status=status_filter)
        task_id = self.request.query_params.get('task')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        return queryset


# ── Уведомления ───────────────────────────────────────────────────────────────

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user)
        if self.request.query_params.get('unread') in {'1', 'true', 'True'}:
            queryset = queryset.filter(is_read=False)
        return queryset.order_by('-created_at')[:100]


class NotificationReadView(APIView):
    """PATCH /api/notifications/<id>/read/"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            notif = Notification.objects.get(id=pk, user=request.user)
            notif.is_read = True
            notif.save()
            return Response({'ok': True})
        except Notification.DoesNotExist:
            return Response({'error': 'Не найдено'}, status=404)


class NotificationReadAllView(APIView):
    """PATCH /api/notifications/read-all/"""
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'ok': True})


# ── Аналитика учителя ─────────────────────────────────────────────────────────

class TeacherAnalyticsView(APIView):
    """GET /api/teacher/analytics/"""
    permission_classes = [IsTeacherAdmin]

    def get(self, request):
        students = UserProfile.objects.filter(
            is_admin=False, is_staff=False, is_superuser=False
        )
        total    = students.count()
        avg_xp   = students.aggregate(avg=models.Avg('xp'))['avg'] or 0

        top = students.order_by('-xp')[:5]
        pending_hw = Homework.objects.filter(status='pending').count()

        progress_data = UserProgress.objects.filter(completed=True).values(
            'lesson__title'
        ).annotate(count=models.Count('id')).order_by('-count')[:5]

        return Response({
            'total_students': total,
            'avg_xp':         round(avg_xp, 1),
            'pending_hw':     pending_hw,
            'top_students':   UserProfileListSerializer(top, many=True).data,
            'popular_lessons': list(progress_data),
        })


class CompleteLessonView(APIView):
    """Завершение урока только после реального просмотра видео."""
    permission_classes = [IsStudent]

    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response({'error': 'Урок не найден'}, status=404)

        raw_ranges = request.data.get('watched_ranges')
        client_watched_seconds = _to_int(request.data.get('watched_seconds'), 0)
        client_duration_seconds = _to_int(request.data.get('video_duration_seconds'), 0)
        current_position = max(0.0, _to_float(request.data.get('current_time'), 0.0))
        ended = request.data.get('ended') is True
        video_urls = _lesson_video_urls(lesson)
        video_count = max(1, len(video_urls))
        video_index = max(0, min(_to_int(request.data.get('video_index'), 0), video_count - 1))
        video_key = str(video_index)

        lesson_duration_seconds = (lesson.duration_minutes or 0) * 60
        total_seconds = max(client_duration_seconds, lesson_duration_seconds, 1)

        if raw_ranges is None and client_watched_seconds <= 0 and client_duration_seconds <= 0:
            return Response({
                'error': 'Урок завершается автоматически только после просмотра видео.',
            }, status=status.HTTP_400_BAD_REQUEST)

        incoming_ranges = _normalise_watch_ranges(raw_ranges, total_seconds)
        if not incoming_ranges and client_watched_seconds > 0:
            fallback_end = min(total_seconds, max(_to_int(current_position), client_watched_seconds))
            incoming_ranges = _normalise_watch_ranges(
                [[max(0, fallback_end - client_watched_seconds), fallback_end]],
                total_seconds,
            )

        now = timezone.now()
        xp_gained = 0
        streak_should_update = False

        with transaction.atomic():
            progress, _ = UserProgress.objects.select_for_update().get_or_create(
                user=request.user,
                lesson=lesson,
            )

            if progress.watch_started_at is None:
                progress.watch_started_at = now

            parts_progress = progress.video_parts_progress if isinstance(progress.video_parts_progress, dict) else {}
            part_progress = parts_progress.get(video_key) if isinstance(parts_progress.get(video_key), dict) else {}

            previous_ranges = _normalise_watch_ranges(part_progress.get('watched_ranges'), total_seconds)
            previous_watched_seconds = _to_int(part_progress.get('watched_seconds'), 0)
            if not previous_ranges and previous_watched_seconds > 0:
                previous_ranges = _normalise_watch_ranges([[0, previous_watched_seconds]], total_seconds)

            if not previous_ranges and video_index == 0:
                previous_ranges = _normalise_watch_ranges(progress.watched_ranges, total_seconds)
                if not previous_ranges and progress.watched_seconds > 0 and not parts_progress:
                    previous_ranges = _normalise_watch_ranges([[0, progress.watched_seconds]], total_seconds)

            previous_seconds = _watch_ranges_duration(previous_ranges)
            last_update = progress.last_watch_update_at or progress.watch_started_at
            elapsed_seconds = max(0, (now - last_update).total_seconds()) if last_update else 0
            allowance = elapsed_seconds + WATCH_SERVER_GRACE_SECONDS
            if progress.last_watch_update_at is None and previous_seconds == 0:
                allowance = max(allowance, WATCH_FIRST_UPDATE_ALLOWANCE_SECONDS)

            accepted_limit = min(total_seconds, previous_seconds + int(math.ceil(allowance)))
            accepted_ranges = _add_watch_ranges_with_limit(
                previous_ranges,
                incoming_ranges,
                total_seconds,
                accepted_limit,
            )
            accepted_seconds = _watch_ranges_duration(accepted_ranges)
            required_seconds = _required_watch_seconds(total_seconds)
            near_video_end = ended or current_position >= max(required_seconds, total_seconds - 12)
            part_completed = accepted_seconds >= required_seconds and near_video_end
            streak_should_update = accepted_seconds > previous_seconds

            parts_progress[video_key] = {
                'watched_ranges': accepted_ranges,
                'watched_seconds': accepted_seconds,
                'video_duration_seconds': total_seconds,
                'required_seconds': required_seconds,
                'watch_percent': min(100, round((accepted_seconds / total_seconds) * 100)) if total_seconds else 0,
                'last_video_position': min(current_position, total_seconds),
                'completed': bool(part_completed or part_progress.get('completed')),
                'updated_at': now.isoformat(),
            }

            completed_video_indexes = sorted(
                int(key)
                for key, value in parts_progress.items()
                if str(key).isdigit() and isinstance(value, dict) and value.get('completed')
            )
            all_parts_completed = all(parts_progress.get(str(index), {}).get('completed') for index in range(video_count))
            aggregate_watched_seconds = sum(
                _to_int(value.get('watched_seconds'), 0)
                for value in parts_progress.values()
                if isinstance(value, dict)
            )
            aggregate_duration_seconds = sum(
                _to_int(value.get('video_duration_seconds'), 0)
                for value in parts_progress.values()
                if isinstance(value, dict)
            )

            progress.video_parts_progress = parts_progress
            progress.watched_ranges = accepted_ranges
            progress.watched_seconds = aggregate_watched_seconds or accepted_seconds
            progress.video_duration_seconds = aggregate_duration_seconds or total_seconds
            progress.last_video_position = min(current_position, total_seconds)
            progress.last_watch_update_at = now

            if not progress.completed and all_parts_completed:
                progress.completed = True
                progress.completed_at = now

                student = UserProfile.objects.select_for_update().get(pk=request.user.pk)
                student.xp += lesson.xp_reward
                student.save(update_fields=['xp'])
                request.user.xp = student.xp
                xp_gained = lesson.xp_reward

            progress.save()

        streak = request.user.streak
        streak_updated = False
        if streak_should_update:
            streak, streak_updated = touch_learning_streak(request.user, reason='video_watch')

        next_video_index = video_index + 1 if part_completed and video_index + 1 < video_count else None
        watch_percent = min(100, round((accepted_seconds / total_seconds) * 100)) if total_seconds else 0
        if progress.completed and xp_gained:
            message = f'+{xp_gained} XP за просмотр урока!'
        elif progress.completed:
            message = 'Урок уже выполнен'
        elif part_completed and next_video_index is not None:
            message = 'Часть просмотрена. Можно перейти к следующему видео.'
        elif part_completed:
            message = 'Видео просмотрено. Осталось завершить другие части урока.'
        else:
            message = 'Прогресс просмотра сохранён'

        return Response({
            'message': message,
            'completed': progress.completed,
            'xp_gained': xp_gained,
            'xp': request.user.xp,
            'total_xp': request.user.xp,
            'watched_seconds': accepted_seconds,
            'video_duration_seconds': total_seconds,
            'required_seconds': required_seconds,
            'watch_percent': watch_percent,
            'watched_ranges': accepted_ranges,
            'last_video_position': progress.last_video_position,
            'video_index': video_index,
            'video_count': video_count,
            'part_completed': bool(parts_progress.get(video_key, {}).get('completed')),
            'next_video_index': next_video_index,
            'completed_video_indexes': completed_video_indexes,
            'video_parts_progress': parts_progress,
            'streak': streak,
            'streak_updated': streak_updated,
        })


class HomeworkSubmitView(APIView):
    """Ученик сдаёт ДЗ; уведомления преподавателям уходят через Celery/fallback."""
    permission_classes = [IsStudent]

    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response({'error': 'Урок не найден'}, status=404)

        homework, created = Homework.objects.get_or_create(
            lesson=lesson,
            student=request.user,
            defaults={'code': request.data.get('code', '')},
        )

        if not created:
            homework.code = request.data.get('code', homework.code)
            homework.status = 'pending'
            homework.feedback = ''
            homework.reviewed_at = None
            homework.save(update_fields=['code', 'status', 'feedback', 'reviewed_at'])

        teacher_ids = UserProfile.objects.filter(
            Q(is_admin=True) | Q(is_staff=True) | Q(is_superuser=True)
        ).values_list('pk', flat=True)
        queue_notifications(
            teacher_ids,
            'system',
            'Новое домашнее задание',
            f'{request.user.username} сдал ДЗ по уроку «{lesson.title}».',
        )
        touch_learning_streak(request.user, reason='homework_submit')

        return Response(HomeworkSerializer(homework).data)

    def get(self, request, lesson_id):
        homework = Homework.objects.filter(
            lesson_id=lesson_id,
            student=request.user,
        ).first()
        if not homework:
            return Response({'status': 'not_submitted'})
        return Response(HomeworkSerializer(homework).data)


class HomeworkReviewView(APIView):
    """Преподаватель проверяет ДЗ; уведомление ученику уходит через Celery/fallback."""
    permission_classes = [IsTeacherAdmin]

    def patch(self, request, pk):
        homework = Homework.objects.filter(pk=pk).select_related('student', 'lesson').first()
        if not homework:
            return Response({'error': 'Не найдено'}, status=404)

        serializer = HomeworkReviewSerializer(homework, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        homework = serializer.save(reviewed_at=timezone.now())

        queue_notification(
            homework.student_id,
            'hw_feedback',
            'Обратная связь по ДЗ',
            f'Учитель проверил ваше ДЗ по уроку «{homework.lesson.title}». '
            f'Статус: {homework.get_status_display()}. {homework.feedback}',
        )

        if homework.status == 'approved':
            homework.student.xp += 20
            homework.student.save(update_fields=['xp'])

        return Response(HomeworkSerializer(homework).data)
