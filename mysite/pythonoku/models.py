from django.contrib.auth.models import AbstractUser
from django.db import models


class UserProfile(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='150 символов или меньше. Можно использовать буквы, цифры и пробелы.',
        error_messages={'unique': 'Пользователь с таким именем уже существует.'},
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    xp = models.PositiveIntegerField(default=0)
    streak = models.PositiveIntegerField(default=0)
    last_activity = models.DateField(null=True, blank=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    cover = models.ImageField(upload_to='covers/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    youtube_url = models.URLField(blank=True)      # ссылка на YouTube видео
    video_urls = models.JSONField(default=list, blank=True)
    content = models.TextField(blank=True)          # текст урока / документация
    order = models.PositiveIntegerField(default=0)  # порядок урока
    xp_reward = models.PositiveIntegerField(default=10)
    duration_minutes = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class LessonComment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.username} → Урок {self.lesson.id}"


class UserProgress(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    watched_seconds = models.PositiveIntegerField(default=0)
    video_duration_seconds = models.PositiveIntegerField(default=0)
    last_video_position = models.FloatField(default=0)
    watched_ranges = models.JSONField(default=list, blank=True)
    video_parts_progress = models.JSONField(default=dict, blank=True)
    watch_started_at = models.DateTimeField(null=True, blank=True)
    last_watch_update_at = models.DateTimeField(null=True, blank=True)
    code_submitted = models.TextField(blank=True)   # последний код ученика

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.username} — {self.lesson.title} ({'✓' if self.completed else '…'})"


class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=10)          # emoji или название иконки
    xp_required = models.PositiveIntegerField(default=0)
    lessons_required = models.PositiveIntegerField(default=0)
    streak_required = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')


class ForumPost(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='forum_posts')
    title = models.CharField(max_length=200)
    text = models.TextField()
    lesson = models.ForeignKey(Lesson, null=True, blank=True, on_delete=models.SET_NULL, related_name='forum_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    is_solved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ForumReply(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='forum_replies')
    text = models.TextField()
    is_best_answer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class Schedule(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    zoom_url = models.URLField(blank=True)
    date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.title} — {self.date.strftime('%d.%m.%Y %H:%M')}"


class AIMessage(models.Model):
    """История чата с ИИ-ассистентом"""
    ROLE_CHOICES = [('user', 'User'), ('assistant', 'Assistant')]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='ai_messages')
    lesson = models.ForeignKey(Lesson, null=True, blank=True, on_delete=models.SET_NULL, related_name='ai_messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} [{self.role}]: {self.content[:50]}"

# Добавь в конец models.py

class Quiz(models.Model):
    """Тест после урока"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    question = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct = models.CharField(max_length=1, choices=[
        ('a','A'), ('b','B'), ('c','C'), ('d','D')
    ])
    xp_reward = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"Тест: {self.lesson.title} — {self.question[:40]}"


class QuizResult(models.Model):
    """Результат теста ученика"""
    user   = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='quiz_results')
    quiz   = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    answer = models.CharField(max_length=1)
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'quiz')


class Homework(models.Model):
    """Домашнее задание"""
    STATUS = [
        ('pending',  'На проверке'),
        ('approved', 'Принято'),
        ('rejected', 'На доработку'),
    ]
    lesson   = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='homeworks')
    student  = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='homeworks')
    code     = models.TextField()
    comment  = models.TextField(blank=True)
    status   = models.CharField(max_length=10, choices=STATUS, default='pending')
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('lesson', 'student')

    def __str__(self):
        return f"{self.student.username} — {self.lesson.title} [{self.status}]"


class CodingTask(models.Model):
    """Проверяемая Python-задача, которую преподаватель прикрепляет к уроку."""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='coding_tasks')
    title_ru = models.CharField(max_length=200)
    title_kg = models.CharField(max_length=200, blank=True)
    description_ru = models.TextField()
    description_kg = models.TextField(blank=True)
    starter_code = models.TextField(default='# Напиши решение здесь\n')
    sample_input = models.TextField(blank=True)
    sample_output = models.TextField(blank=True)
    tests = models.JSONField(default=list)
    order = models.PositiveIntegerField(default=0)
    xp_reward = models.PositiveIntegerField(default=10)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['lesson__course_id', 'lesson__order', 'order', 'id']

    def __str__(self):
        return f'{self.lesson.title} — {self.title_ru}'


class CodingSubmission(models.Model):
    """Последняя попытка ученика и история факта успешного прохождения."""
    STATUS = [
        ('passed', 'Все тесты пройдены'),
        ('failed', 'Есть ошибки'),
    ]
    task = models.ForeignKey(CodingTask, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='coding_submissions')
    code = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS, default='failed')
    test_results = models.JSONField(default=list)
    checker_error = models.TextField(blank=True)
    attempts = models.PositiveIntegerField(default=0)
    passed_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('task', 'student')
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.student.username} — {self.task.title_ru} [{self.status}]'


class Notification(models.Model):
    """Уведомления"""
    TYPE = [
        ('hw_feedback', 'Обратная связь по ДЗ'),
        ('new_lesson',  'Новый урок'),
        ('achievement', 'Достижение'),
        ('system',      'Системное'),
    ]
    user       = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='notifications')
    type       = models.CharField(max_length=20, choices=TYPE)
    title      = models.CharField(max_length=200)
    text       = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
