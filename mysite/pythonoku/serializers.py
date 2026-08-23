from rest_framework import serializers
from .models import *
from datetime import timedelta
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from django.db.models import Q
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django_rest_passwordreset.models import (
    ResetPasswordToken,
    get_password_reset_token_expiry_time,
)
from .permissions import has_teacher_access


# ── User ──────────────────────────────────────────────────────────────────────

class UserProfileListSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'avatar', 'xp', 'streak', 'is_admin']

    def get_is_admin(self, obj):
        return bool(obj.is_admin or obj.is_staff or obj.is_superuser)


class UserProfileDetailSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'avatar', 'bio',
                  'xp', 'streak', 'last_activity', 'is_admin', 'date_joined']
        read_only_fields = [
            'id', 'username', 'email', 'xp', 'streak',
            'last_activity', 'is_admin', 'date_joined',
        ]

    def get_is_admin(self, obj):
        return bool(obj.is_admin or obj.is_staff or obj.is_superuser)


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, allow_blank=False, trim_whitespace=True)
    email = serializers.EmailField(allow_blank=False)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password']

    def validate_username(self, value):
        username = ' '.join((value or '').strip().split())
        if len(username) < 2:
            raise serializers.ValidationError('Имя пользователя должно быть минимум 2 символа.')
        if len(username) > 150:
            raise serializers.ValidationError('Имя пользователя должно быть не длиннее 150 символов.')
        if UserProfile.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError('Пользователь с таким именем уже существует.')
        return username

    def validate_email(self, value):
        email = (value or '').strip().lower()
        if UserProfile.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('Пользователь с такой почтой уже существует.')
        return email

    def create(self, validated_data):
        return UserProfile.objects.create_user(**validated_data)


class EmailOrUsernameTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': 'Неверный email/имя пользователя или пароль.',
    }

    def validate(self, attrs):
        identifier = (attrs.get(self.username_field) or '').strip()
        if not identifier:
            raise serializers.ValidationError({
                self.username_field: 'Введите email или имя пользователя.',
            })

        user = UserProfile.objects.filter(
            Q(username__iexact=identifier) | Q(email__iexact=identifier)
        ).order_by('id').first()

        if user:
            attrs[self.username_field] = user.username

        data = super().validate(attrs)
        data['user'] = UserProfileDetailSerializer(self.user).data
        return data

class VerifyResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_code = serializers.CharField(min_length=6, max_length=6, trim_whitespace=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        reset_code = data.get('reset_code')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not reset_code.isdigit():
            raise serializers.ValidationError({'reset_code': 'Код должен состоять из шести цифр.'})

        if new_password != confirm_password:
            raise serializers.ValidationError({'confirm_password': 'Пароли не совпадают.'})

        token = ResetPasswordToken.objects.filter(
            user__email__iexact=email,
            key=reset_code,
        ).select_related('user').first()

        if not token:
            raise serializers.ValidationError({'reset_code': 'Неверный код или email.'})

        expires_at = token.created_at + timedelta(
            hours=get_password_reset_token_expiry_time()
        )
        if timezone.now() > expires_at:
            token.delete()
            raise serializers.ValidationError({'reset_code': 'Срок действия кода истёк. Запросите новый.'})

        try:
            validate_password(new_password, user=token.user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'new_password': list(exc.messages)})

        data['user'] = token.user
        data['token'] = token
        return data

    def save(self):
        user = self.validated_data['user']
        token = self.validated_data['token']
        new_password = self.validated_data['new_password']

        user.set_password(new_password)
        user.save()

        ResetPasswordToken.objects.filter(user=user).delete()


def clean_video_urls(value):
    if not isinstance(value, list):
        return []

    cleaned = []
    for item in value:
        url = str(item or '').strip()
        if url and url not in cleaned:
            cleaned.append(url)
    return cleaned


class LessonVideoFieldsMixin:
    def validate_video_urls(self, value):
        return clean_video_urls(value)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        video_urls = attrs.get('video_urls')
        youtube_url = str(attrs.get('youtube_url') or '').strip()

        if video_urls is not None:
            video_urls = clean_video_urls(video_urls)
            attrs['video_urls'] = video_urls
            attrs['youtube_url'] = video_urls[0] if video_urls else youtube_url
        elif youtube_url and not getattr(self.instance, 'video_urls', None):
            attrs['video_urls'] = [youtube_url]

        return attrs


# ── Course & Lesson ───────────────────────────────────────────────────────────

class LessonListSerializer(LessonVideoFieldsMixin, serializers.ModelSerializer):
    content = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'content', 'order',
                  'duration_minutes', 'xp_reward', 'is_published', 'youtube_url',
                  'video_urls']


class LessonDetailSerializer(LessonVideoFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class CourseListSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'cover',
                  'is_published', 'lessons_count', 'created_at']

    def get_lessons_count(self, obj):
        request = self.context.get('request')
        if request and has_teacher_access(request.user):
            return obj.lessons.count()
        return obj.lessons.filter(is_published=True).count()


class CourseDetailSerializer(serializers.ModelSerializer):
    lessons = LessonListSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'


# ── Comments ──────────────────────────────────────────────────────────────────

class LessonCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.ImageField(source='author.avatar', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = LessonComment
        fields = ['id', 'lesson', 'author', 'author_name', 'author_avatar',
                  'parent', 'text', 'replies', 'created_at']
        read_only_fields = ['author']

    def get_replies(self, obj):
        if obj.replies.exists():
            return LessonCommentSerializer(obj.replies.all(), many=True).data
        return []


# ── Progress ──────────────────────────────────────────────────────────────────

class UserProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    watch_percent = serializers.SerializerMethodField()

    class Meta:
        model = UserProgress
        fields = ['id', 'lesson', 'lesson_title', 'completed',
                  'completed_at', 'code_submitted', 'watched_seconds',
                  'video_duration_seconds', 'last_video_position',
                  'watched_ranges', 'video_parts_progress', 'watch_percent']
        read_only_fields = ['user']

    def get_watch_percent(self, obj):
        parts_progress = obj.video_parts_progress if isinstance(obj.video_parts_progress, dict) else {}
        if parts_progress:
            total_duration = 0
            total_watched = 0
            for part in parts_progress.values():
                if not isinstance(part, dict):
                    continue
                total_duration += int(part.get('video_duration_seconds') or 0)
                total_watched += int(part.get('watched_seconds') or 0)
            if total_duration:
                return min(100, round((total_watched / total_duration) * 100))

        if not obj.video_duration_seconds:
            return 0
        return min(100, round((obj.watched_seconds / obj.video_duration_seconds) * 100))


# ── Achievements ──────────────────────────────────────────────────────────────

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = ['id', 'achievement', 'earned_at']


# ── Forum ─────────────────────────────────────────────────────────────────────

class ForumReplySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    content = serializers.CharField(source='text', allow_blank=False, trim_whitespace=True)

    class Meta:
        model = ForumReply
        fields = ['id', 'post', 'author', 'author_name', 'author_username',
                  'content', 'is_best_answer', 'created_at']
        read_only_fields = ['author', 'post']


class ForumPostListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    content = serializers.CharField(source='text', allow_blank=False, trim_whitespace=True)
    replies_count = serializers.SerializerMethodField()
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = ForumPost
        fields = ['id', 'title', 'author', 'author_name', 'author_username',
                  'content', 'lesson', 'lesson_title', 'views', 'is_solved',
                  'replies_count', 'created_at']
        read_only_fields = ['author', 'views']

    def get_replies_count(self, obj):
        return obj.replies.count()


class ForumPostDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    content = serializers.CharField(source='text', allow_blank=False, trim_whitespace=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    replies = ForumReplySerializer(many=True, read_only=True)

    class Meta:
        model = ForumPost
        fields = ['id', 'title', 'author', 'author_name', 'author_username',
                  'content', 'lesson', 'lesson_title', 'views', 'is_solved',
                  'replies', 'created_at']
        read_only_fields = ['author', 'views']


# ── Schedule ──────────────────────────────────────────────────────────────────

class ScheduleSerializer(serializers.ModelSerializer):
    meet_url = serializers.URLField(source='zoom_url', required=False, allow_blank=True)
    zoom_url = serializers.URLField(read_only=True)

    class Meta:
        model = Schedule
        fields = ['id', 'title', 'description', 'meet_url', 'zoom_url',
                  'date', 'duration_minutes', 'created_at']
        read_only_fields = ['created_at']


# ── Leaderboard ───────────────────────────────────────────────────────────────

class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'avatar', 'xp', 'streak']


class AIMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMessage
        fields = ['id', 'role', 'content', 'created_at']


class AIChatInputSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000)
    lesson_id = serializers.IntegerField(required=False, allow_null=True)

class QuizSerializer(serializers.ModelSerializer):
    correct = serializers.CharField(max_length=1)

    class Meta:
        model = Quiz
        fields = ['id', 'lesson', 'question', 'option_a',
                  'option_b', 'option_c', 'option_d', 'correct', 'xp_reward']

    def validate_correct(self, value):
        correct = (value or '').lower()
        if correct not in {'a', 'b', 'c', 'd'}:
            raise serializers.ValidationError('Выберите правильный вариант: a, b, c или d.')
        return correct

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if not request or not has_teacher_access(request.user):
            data.pop('correct', None)
        return data

class QuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResult
        fields = ['id', 'quiz', 'answer', 'is_correct', 'answered_at']
        read_only_fields = ['user', 'is_correct']

class HomeworkSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    class Meta:
        model = Homework
        fields = '__all__'
        read_only_fields = ['student', 'status', 'feedback', 'reviewed_at']

class HomeworkReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = ['status', 'feedback']


class CodingSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)
    task_title = serializers.CharField(source='task.title_ru', read_only=True)
    lesson_title = serializers.CharField(source='task.lesson.title', read_only=True)
    course_title = serializers.CharField(source='task.lesson.course.title', read_only=True)
    completed = serializers.SerializerMethodField()
    passed = serializers.SerializerMethodField()

    class Meta:
        model = CodingSubmission
        fields = [
            'id', 'task', 'task_title', 'lesson_title', 'course_title',
            'student', 'student_name', 'code', 'status', 'passed', 'completed',
            'test_results', 'checker_error', 'attempts', 'passed_at',
            'submitted_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_completed(self, obj):
        return obj.passed_at is not None

    def get_passed(self, obj):
        return obj.status == 'passed'


class CodingTaskSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    course_title = serializers.CharField(source='lesson.course.title', read_only=True)
    my_submission = serializers.SerializerMethodField()
    tests_count = serializers.SerializerMethodField()

    class Meta:
        model = CodingTask
        fields = [
            'id', 'lesson', 'lesson_title', 'course_title', 'title_ru', 'title_kg',
            'description_ru', 'description_kg', 'starter_code', 'sample_input',
            'sample_output', 'tests', 'tests_count', 'order', 'xp_reward',
            'is_published', 'created_at', 'my_submission',
        ]
        read_only_fields = ['created_at']

    def get_my_submission(self, obj):
        submissions = getattr(obj, 'current_user_submissions', None)
        if submissions is None:
            request = self.context.get('request')
            if not request or not request.user.is_authenticated:
                return None
            submission = obj.submissions.filter(student=request.user).first()
        else:
            submission = submissions[0] if submissions else None
        return CodingSubmissionSerializer(submission).data if submission else None

    def get_tests_count(self, obj):
        return len(obj.tests) if isinstance(obj.tests, list) else 0

    def validate_tests(self, value):
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError('Добавьте хотя бы один тест.')
        if len(value) > 12:
            raise serializers.ValidationError('Можно добавить не больше 12 тестов.')
        for index, item in enumerate(value, 1):
            if not isinstance(item, dict) or 'expected' not in item:
                raise serializers.ValidationError(f'В тесте №{index} отсутствует ожидаемый результат.')
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if not request or not has_teacher_access(request.user):
            data.pop('tests', None)
        return data

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['user']
