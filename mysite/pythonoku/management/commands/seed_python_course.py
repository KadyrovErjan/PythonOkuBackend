from django.core.management.base import BaseCommand
from django.db import transaction

from pythonoku.course_seed_data import COURSE_DESCRIPTION, COURSE_TITLE, LESSONS
from pythonoku.models import Course, Lesson, Quiz


class Command(BaseCommand):
    help = 'Создаёт или обновляет курс Python программалоо с уроками и тестами.'
    requires_system_checks = []

    @transaction.atomic
    def handle(self, *args, **options):
        course, _ = Course.objects.update_or_create(
            title=COURSE_TITLE,
            defaults={
                'description': COURSE_DESCRIPTION,
                'is_published': True,
            },
        )

        created_lessons = []
        quizzes_count = 0

        for order, lesson_data in enumerate(LESSONS, start=1):
            lesson, _ = Lesson.objects.update_or_create(
                course=course,
                title=lesson_data['title'],
                defaults={
                    'description': lesson_data['description'],
                    'youtube_url': lesson_data.get('youtube_url', ''),
                    'content': lesson_data['content'],
                    'order': order,
                    'xp_reward': lesson_data.get('xp_reward', 15),
                    'duration_minutes': lesson_data.get('duration_minutes', 0),
                    'is_published': True,
                },
            )
            created_lessons.append(lesson)

            for quiz_data in lesson_data['quizzes']:
                Quiz.objects.update_or_create(
                    lesson=lesson,
                    question=quiz_data['question'],
                    defaults={
                        'option_a': quiz_data['option_a'],
                        'option_b': quiz_data['option_b'],
                        'option_c': quiz_data['option_c'],
                        'option_d': quiz_data['option_d'],
                        'correct': quiz_data['correct'],
                        'xp_reward': 5,
                    },
                )
                quizzes_count += 1

        self.stdout.write(self.style.SUCCESS('Курс Python программалоо загружен.'))
        self.stdout.write(f'Курс: {course.title}')
        self.stdout.write(f'Уроков: {len(created_lessons)}')
        self.stdout.write(f'Тестовых вопросов: {quizzes_count}')
