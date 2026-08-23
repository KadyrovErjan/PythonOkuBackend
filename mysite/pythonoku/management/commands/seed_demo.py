from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from pythonoku.models import (
    Achievement,
    CodingSubmission,
    CodingTask,
    Course,
    ForumPost,
    ForumReply,
    Homework,
    Lesson,
    Notification,
    Quiz,
    Schedule,
    UserAchievement,
    UserProfile,
    UserProgress,
)


DEMO_PASSWORD = 'Demo12345!'


class Command(BaseCommand):
    help = 'Создаёт демонстрационные данные PythonOku для локального просмотра.'
    requires_system_checks = []

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Demo-данные разрешено создавать только при DEBUG=True.')

        teacher = self.upsert_user(
            'demo_teacher', 'teacher@demo.pythonoku.local',
            xp=0, streak=0, is_admin=True,
        )
        student = self.upsert_user(
            'demo_student', 'student@demo.pythonoku.local',
            xp=215, streak=7, is_admin=False,
        )
        anna = self.upsert_user(
            'anna_demo', 'anna@demo.pythonoku.local',
            xp=340, streak=12, is_admin=False,
        )
        timur = self.upsert_user(
            'timur_demo', 'timur@demo.pythonoku.local',
            xp=260, streak=5, is_admin=False,
        )
        alina = self.upsert_user(
            'alina_demo', 'alina@demo.pythonoku.local',
            xp=120, streak=3, is_admin=False,
        )

        courses = self.create_courses()
        lessons = [lesson for course_lessons in courses.values() for lesson in course_lessons]
        self.create_progress(student, anna, timur, alina, lessons)
        self.create_achievements(student, anna)
        self.create_homeworks(student, anna, timur, lessons)
        self.create_schedule()
        self.create_forum(teacher, student, anna, lessons)
        self.create_notifications(teacher, student)
        self.create_quizzes(lessons)
        first_published_lesson = Lesson.objects.filter(
            is_published=True,
            course__is_published=True,
        ).order_by('course_id', 'order', 'id').first() or lessons[0]
        self.create_coding_tasks(first_published_lesson, student, anna, timur)

        self.stdout.write(self.style.SUCCESS('Demo-данные PythonOku готовы.'))
        self.stdout.write('')
        self.stdout.write('Преподаватель: demo_teacher / Demo12345!')
        self.stdout.write('Ученик:         demo_student / Demo12345!')
        self.stdout.write('')
        self.stdout.write(f'Создано курсов: {Course.objects.filter(title__in=courses).count()}')
        self.stdout.write(f'Demo-учеников: 4')

    def upsert_user(self, username, email, *, xp, streak, is_admin):
        user, _ = UserProfile.objects.get_or_create(username=username)
        user.email = email
        user.xp = xp
        user.streak = streak
        user.last_activity = timezone.localdate() if streak else None
        user.is_admin = is_admin
        user.is_active = True
        user.bio = (
            'Преподаватель PythonOku. Помогаю превращать знания в практику.'
            if is_admin else
            'Изучаю Python, решаю задачи и собираю первый настоящий проект.'
        )
        user.set_password(DEMO_PASSWORD)
        user.save()
        return user

    def create_courses(self):
        course_specs = [
            {
                'title': 'Python с нуля',
                'description': 'Спокойный старт: синтаксис, переменные, условия и первые программы.',
                'lessons': [
                    ('Первая программа', 'Познакомимся с Python и напишем первый print().', 15, 10),
                    ('Переменные и типы данных', 'Научимся хранить текст, числа и логические значения.', 22, 15),
                    ('Условия if / elif / else', 'Добавим программам логику и принятие решений.', 25, 20),
                    ('Циклы for и while', 'Автоматизируем повторяющиеся действия.', 28, 20),
                ],
            },
            {
                'title': 'Коллекции и данные',
                'description': 'Списки, словари и удобная работа с наборами данных.',
                'lessons': [
                    ('Списки на практике', 'Добавление, удаление, срезы и полезные методы.', 24, 20),
                    ('Словари и множества', 'Структурируем данные и быстро находим нужное.', 26, 20),
                    ('Мини-проект: каталог книг', 'Соберём консольное приложение из изученных тем.', 40, 35),
                ],
            },
            {
                'title': 'Функции и архитектура',
                'description': 'Пишем понятный переиспользуемый код и собираем проект по частям.',
                'lessons': [
                    ('Свои функции', 'Аргументы, return и область видимости переменных.', 27, 25),
                    ('Модули и пакеты', 'Разделяем большой проект на удобные файлы.', 30, 25),
                    ('Финальный проект', 'Применяем всё изученное в итоговой работе.', 55, 50),
                ],
            },
        ]

        result = {}
        for course_spec in course_specs:
            course, _ = Course.objects.update_or_create(
                title=course_spec['title'],
                defaults={
                    'description': course_spec['description'],
                    'is_published': True,
                },
            )
            course_lessons = []
            for order, (title, description, duration, xp) in enumerate(course_spec['lessons'], 1):
                lesson, _ = Lesson.objects.update_or_create(
                    course=course,
                    title=title,
                    defaults={
                        'description': description,
                        'content': self.lesson_content(title),
                        'order': order,
                        'duration_minutes': duration,
                        'xp_reward': xp,
                        'is_published': True,
                    },
                )
                course_lessons.append(lesson)
            result[course.title] = course_lessons
        return result

    @staticmethod
    def lesson_content(title):
        return (
            f'# {title}\n\n'
            'В этом уроке теория сразу закрепляется небольшими примерами.\n\n'
            '```python\n'
            'message = "Шаг за шагом — к уверенному Python"\n'
            'print(message)\n'
            '```\n\n'
            'После урока выполни тест и отправь решение на проверку.'
        )

    @staticmethod
    def create_progress(student, anna, timur, alina, lessons):
        plans = {
            student: (5, 4),
            anna: (9, 8),
            timur: (7, 6),
            alina: (4, 3),
        }
        now = timezone.now()
        for user, (started, completed) in plans.items():
            UserProgress.objects.filter(user=user).delete()
            for index, lesson in enumerate(lessons[:started]):
                is_completed = index < completed
                UserProgress.objects.create(
                    user=user,
                    lesson=lesson,
                    completed=is_completed,
                    completed_at=now - timedelta(days=started - index) if is_completed else None,
                    code_submitted='print("Задание выполнено")' if is_completed else '',
                )

    @staticmethod
    def create_achievements(student, anna):
        specs = [
            ('Первый шаг', 'Завершён первый урок', '🚀', 10, 1, 0),
            ('В хорошем ритме', 'Три урока уже позади', '⚡', 50, 3, 0),
            ('Неделя Python', 'Серия занятий — 7 дней', '🔥', 100, 0, 7),
        ]
        achievements = []
        for name, description, icon, xp, lesson_count, streak in specs:
            achievement, _ = Achievement.objects.update_or_create(
                name=name,
                defaults={
                    'description': description,
                    'icon': icon,
                    'xp_required': xp,
                    'lessons_required': lesson_count,
                    'streak_required': streak,
                },
            )
            achievements.append(achievement)

        UserAchievement.objects.filter(user__in=[student, anna]).delete()
        for achievement in achievements:
            UserAchievement.objects.create(user=student, achievement=achievement)
            UserAchievement.objects.create(user=anna, achievement=achievement)

    @staticmethod
    def create_homeworks(student, anna, timur, lessons):
        Homework.objects.filter(student__in=[student, anna, timur]).delete()
        Homework.objects.create(
            student=student,
            lesson=lessons[4],
            code='books = ["Clean Code", "Python Tricks"]\nfor book in books:\n    print(book)',
            comment='Сделал вывод всех книг. Жду обратную связь!',
            status='pending',
        )
        Homework.objects.create(
            student=anna,
            lesson=lessons[3],
            code='for number in range(1, 11):\n    print(number ** 2)',
            status='approved',
            feedback='Отличное решение: коротко, понятно и без лишнего кода.',
            reviewed_at=timezone.now() - timedelta(days=1),
        )
        Homework.objects.create(
            student=timur,
            lesson=lessons[5],
            code='profile = {"name": "Timur", "level": 6}\nprint(profile)',
            comment='Добавил словарь профиля.',
            status='pending',
        )

    @staticmethod
    def create_schedule():
        demo_titles = [
            'Live-разбор: условия и циклы',
            'Практикум по коллекциям',
            'Открытая защита мини-проектов',
            'Разбор первой программы',
        ]
        Schedule.objects.filter(title__in=demo_titles).delete()
        now = timezone.now()
        specs = [
            (demo_titles[0], 'Разберём частые ошибки и решим задачу вместе.', 1, 18, 60),
            (demo_titles[1], 'Списки и словари на реальном небольшом примере.', 3, 17, 75),
            (demo_titles[2], 'Ученики покажут проекты и получат обратную связь.', 7, 19, 90),
            (demo_titles[3], 'Запись прошедшего вводного занятия.', -2, 18, 55),
        ]
        for title, description, day_offset, hour, duration in specs:
            event_date = (now + timedelta(days=day_offset)).replace(
                hour=hour, minute=0, second=0, microsecond=0,
            )
            Schedule.objects.create(
                title=title,
                description=description,
                zoom_url='https://meet.google.com/abc-defg-hij',
                date=event_date,
                duration_minutes=duration,
            )

    @staticmethod
    def create_forum(teacher, student, anna, lessons):
        demo_titles = [
            'Как выбрать между for и while?',
            'Покажите ваши первые мини-проекты',
        ]
        ForumPost.objects.filter(title__in=demo_titles).delete()
        first = ForumPost.objects.create(
            author=student,
            lesson=lessons[3],
            title=demo_titles[0],
            text='Понимаю оба цикла, но пока не всегда понимаю, какой выбрать.',
            views=24,
            is_solved=True,
        )
        ForumReply.objects.create(
            post=first,
            author=teacher,
            text='Если заранее известно количество повторений — начни с for. '
                 'Если остановка зависит от условия — чаще подойдёт while.',
            is_best_answer=True,
        )
        second = ForumPost.objects.create(
            author=anna,
            lesson=lessons[6],
            title=demo_titles[1],
            text='Я собрала каталог книг. Какие проекты сделали вы?',
            views=41,
        )
        ForumReply.objects.create(
            post=second,
            author=student,
            text='Я делаю трекер учебных задач — пока в консоли.',
        )

    @staticmethod
    def create_notifications(teacher, student):
        Notification.objects.filter(user__in=[teacher, student]).delete()
        Notification.objects.create(
            user=student,
            type='new_lesson',
            title='Открыт новый урок',
            text='В курсе «Коллекции и данные» появился мини-проект.',
            is_read=False,
        )
        Notification.objects.create(
            user=student,
            type='achievement',
            title='Новая серия занятий',
            text='Ты занимаешься уже 7 дней подряд. Отличный ритм!',
            is_read=False,
        )
        Notification.objects.create(
            user=teacher,
            type='system',
            title='Работы ждут проверки',
            text='Два ученика отправили домашние задания.',
            is_read=False,
        )

    @staticmethod
    def create_quizzes(lessons):
        questions = [
            (lessons[0], 'Какая функция выводит текст в консоль?', 'input()', 'print()', 'len()', 'type()', 'b'),
            (lessons[1], 'Какое имя переменной корректно?', '2name', 'user-name', 'user_name', 'class', 'c'),
            (lessons[3], 'Что создаёт range(3)?', '0, 1, 2', '1, 2, 3', '0, 1, 2, 3', 'Только 3', 'a'),
        ]
        for lesson, question, a, b, c, d, correct in questions:
            Quiz.objects.update_or_create(
                lesson=lesson,
                question=question,
                defaults={
                    'option_a': a,
                    'option_b': b,
                    'option_c': c,
                    'option_d': d,
                    'correct': correct,
                    'xp_reward': 5,
                },
            )

    @staticmethod
    def create_coding_tasks(lesson, student, anna, timur):
        """20 двуязычных задач с открытыми примерами и скрытыми тестами."""
        yes_no = {
            'yes': ['Да', 'Ооба', 'True', 'true', 'YES', 'Yes'],
            'no': ['Нет', 'Жок', 'False', 'false', 'NO', 'No'],
        }
        specs = [
            {
                'lesson': lesson, 'title_ru': 'Знак числа', 'title_kg': 'Сандын белгиси',
                'description_ru': 'Пользователь вводит число. Определи, положительное оно или отрицательное.',
                'description_kg': 'Колдонуучу сан киргизет. Сан оңбу же терсби аныкта.',
                'sample_input': '8', 'sample_output': 'Положительное',
                'tests': [
                    {'input': '8', 'expected': ['Положительное', 'Оң'], 'hidden': False},
                    {'input': '-13', 'expected': ['Отрицательное', 'Терс'], 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Деление на 5', 'title_kg': '5ке бөлүү',
                'description_ru': 'Введи число. Если оно делится на 5 — выведи «Делится», иначе «Не делится».',
                'description_kg': 'Сан 5ке бөлүнөбү текшер. Бөлүнсө «Бөлүнөт», болбосо «Бөлүнбөйт».',
                'sample_input': '25', 'sample_output': 'Делится',
                'tests': [
                    {'input': '25', 'expected': ['Делится', 'Бөлүнөт'], 'hidden': False},
                    {'input': '17', 'expected': ['Не делится', 'Бөлүнбөйт'], 'hidden': True},
                    {'input': '-10', 'expected': ['Делится', 'Бөлүнөт'], 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Большее из двух', 'title_kg': 'Эки сандын чоңу',
                'description_ru': 'Введи два числа. Выведи большее из них.',
                'description_kg': 'Эки сан киргиз. Чоң санды чыгар.',
                'sample_input': '7\n12', 'sample_output': '12',
                'tests': [
                    {'input': '7\n12', 'expected': '12', 'hidden': False},
                    {'input': '-3\n-8', 'expected': '-3', 'hidden': True},
                    {'input': '5\n5', 'expected': '5', 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Минимум из трёх', 'title_kg': 'Үч сандын кичинеси',
                'description_ru': 'Введи три числа. Найди наименьшее.',
                'description_kg': 'Үч сан киргиз. Эң кичине санды тап.',
                'sample_input': '9\n2\n6', 'sample_output': '2',
                'tests': [
                    {'input': '9\n2\n6', 'expected': '2', 'hidden': False},
                    {'input': '-1\n-9\n3', 'expected': '-9', 'hidden': True},
                    {'input': '4\n4\n4', 'expected': '4', 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Проверка возраста', 'title_kg': 'Жашты текшерүү',
                'description_ru': 'Введи возраст. Если он меньше 18 — выведи «Несовершеннолетний», иначе «Совершеннолетний».',
                'description_kg': 'Жашты киргиз. 18ден кичине болсо «Жаш», болбосо «Чоң».',
                'sample_input': '16', 'sample_output': 'Несовершеннолетний',
                'tests': [
                    {'input': '16', 'expected': ['Несовершеннолетний', 'Жаш'], 'hidden': False},
                    {'input': '18', 'expected': ['Совершеннолетний', 'Чоң', 'Чон'], 'hidden': True},
                    {'input': '35', 'expected': ['Совершеннолетний', 'Чоң', 'Чон'], 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Длина слова', 'title_kg': 'Сөздүн узундугу',
                'description_ru': 'Введи слово. Выведи его длину.',
                'description_kg': 'Сөз киргиз. Узундугун чыгар.',
                'sample_input': 'python', 'sample_output': '6',
                'tests': [
                    {'input': 'python', 'expected': '6', 'hidden': False},
                    {'input': 'салам', 'expected': '5', 'hidden': True},
                    {'input': 'код', 'expected': '3', 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Первая и последняя буква', 'title_kg': 'Биринчи жана акыркы тамга',
                'description_ru': 'Введи слово. Выведи первую и последнюю букву через пробел.',
                'description_kg': 'Сөз киргиз. Биринчи жана акыркы тамганы боштук аркылуу чыгар.',
                'sample_input': 'Python', 'sample_output': 'P n',
                'tests': [
                    {'input': 'Python', 'expected': 'P n', 'hidden': False},
                    {'input': 'салам', 'expected': 'с м', 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Палиндром', 'title_kg': 'Палиндром',
                'description_ru': 'Проверь слово. Выведи «Палиндром» или «Не палиндром».',
                'description_kg': 'Сөз палиндромбу текшер. «Палиндром» же «Палиндром эмес» деп чыгар.',
                'sample_input': 'топот', 'sample_output': 'Палиндром',
                'tests': [
                    {'input': 'топот', 'expected': ['Палиндром', 'Ооба', 'Да', 'True'], 'hidden': False},
                    {'input': 'python', 'expected': ['Не палиндром', 'Палиндром эмес', 'Жок', 'Нет', 'False'], 'hidden': True},
                    {'input': 'level', 'expected': ['Палиндром', 'Ооба', 'Да', 'True'], 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Имя в верхнем регистре', 'title_kg': 'Атты чоң тамга менен жазуу',
                'description_ru': 'Введи имя. Выведи его полностью в верхнем регистре.',
                'description_kg': 'Ат киргиз. Бардык тамгаларды чоң кылып чыгар.',
                'sample_input': 'Amin', 'sample_output': 'AMIN',
                'tests': [
                    {'input': 'Amin', 'expected': 'AMIN', 'hidden': False},
                    {'input': 'айжан', 'expected': 'АЙЖАН', 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Сколько букв a', 'title_kg': 'a тамгасын эсептөө',
                'description_ru': 'Введи строку. Посчитай, сколько раз встречается строчная буква «a».',
                'description_kg': 'Текст киргиз. Кичине «a» тамгасы канча жолу кездешет эсепте.',
                'sample_input': 'banana', 'sample_output': '3',
                'tests': [
                    {'input': 'banana', 'expected': '3', 'hidden': False},
                    {'input': 'Python', 'expected': '0', 'hidden': True},
                    {'input': 'abracadabra', 'expected': '5', 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Сравнение слов', 'title_kg': 'Сөздөрдү салыштыруу',
                'description_ru': 'Введи два слова. Сравни их без учёта регистра. Выведи «Одинаковые» или «Разные».',
                'description_kg': 'Эки сөз киргиз. Чоң-кичине тамгаларды эске албай салыштыр. «Бирдей» же «Ар башка» деп чыгар.',
                'sample_input': 'Python\nPYTHON', 'sample_output': 'Одинаковые',
                'tests': [
                    {'input': 'Python\nPYTHON', 'expected': ['Одинаковые', 'Бирдей', 'True'], 'hidden': False},
                    {'input': 'код\nкот', 'expected': ['Разные', 'Ар башка', 'False'], 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Приветствие по стране', 'title_kg': 'Өлкө боюнча саламдашуу',
                'description_ru': 'Введи страну. Кыргызстан — «Салам», Россия — «Привет», иначе — «Hello».',
                'description_kg': 'Өлкө киргиз. Кыргызстан болсо «Салам», Россия болсо «Привет», болбосо «Hello».',
                'sample_input': 'Кыргызстан', 'sample_output': 'Салам',
                'tests': [
                    {'input': 'Кыргызстан', 'expected': 'Салам', 'hidden': False},
                    {'input': 'Россия', 'expected': 'Привет', 'hidden': True},
                    {'input': 'Казахстан', 'expected': 'Hello', 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Чётное и больше 10', 'title_kg': 'Жуп жана 10дон чоң',
                'description_ru': 'Введи число. Если оно чётное и больше 10 — выведи «OK». Иначе ничего не выводи.',
                'description_kg': 'Сан киргиз. Сан жуп жана 10дон чоң болсо «OK» чыгар. Болбосо эч нерсе чыгарба.',
                'sample_input': '12', 'sample_output': 'OK',
                'tests': [
                    {'input': '12', 'expected': 'OK', 'hidden': False},
                    {'input': '9', 'expected': '', 'hidden': True},
                    {'input': '13', 'expected': '', 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Допустимый диапазон', 'title_kg': 'Туура диапазон',
                'description_ru': 'Введи число. Если оно меньше 0 или больше 100 — выведи «Ошибка». Иначе ничего не выводи.',
                'description_kg': 'Сан киргиз. Сан 0дон кичине же 100дөн чоң болсо «Ката» чыгар. Болбосо эч нерсе чыгарба.',
                'sample_input': '120', 'sample_output': 'Ошибка',
                'tests': [
                    {'input': '120', 'expected': ['Ошибка', 'Ката'], 'hidden': False},
                    {'input': '-1', 'expected': ['Ошибка', 'Ката'], 'hidden': True},
                    {'input': '50', 'expected': '', 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Замена букв', 'title_kg': 'Тамгаларды алмаштыруу',
                'description_ru': 'Введи слово. Замени все строчные буквы «a» на «o».',
                'description_kg': 'Сөз киргиз. Бардык кичине «a» тамгаларын «o» га алмаштыр.',
                'sample_input': 'banana', 'sample_output': 'bonono',
                'tests': [
                    {'input': 'banana', 'expected': 'bonono', 'hidden': False},
                    {'input': 'abracadabra', 'expected': 'obrocodobro', 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Разделение предложения', 'title_kg': 'Сүйлөмдү сөздөргө бөлүү',
                'description_ru': 'Введи предложение. Раздели его на слова с помощью split и выведи получившийся список.',
                'description_kg': 'Сүйлөм киргиз. Аны split менен сөздөргө бөлүп, тизмени чыгар.',
                'sample_input': 'Я учу Python', 'sample_output': "['Я', 'учу', 'Python']",
                'tests': [
                    {'input': 'Я учу Python', 'expected': "['Я', 'учу', 'Python']", 'hidden': False},
                    {'input': 'Салам дүйнө', 'expected': "['Салам', 'дүйнө']", 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Квадрат числа', 'title_kg': 'Сандын квадраты',
                'description_ru': 'Введи число. Выведи квадрат этого числа.',
                'description_kg': 'Сан киргиз. Анын квадратын чыгар.',
                'sample_input': '7', 'sample_output': '49',
                'tests': [
                    {'input': '7', 'expected': '49', 'hidden': False},
                    {'input': '-4', 'expected': '16', 'hidden': True},
                    {'input': '0', 'expected': '0', 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Деление на 3 и 4', 'title_kg': '3кө жана 4кө бөлүү',
                'description_ru': 'Введи число. Если оно делится одновременно на 3 и 4, выведи «Да», иначе «Нет».',
                'description_kg': 'Сан киргиз. 3кө жана 4кө бир убакта бөлүнсө «Ооба», болбосо «Жок» чыгар.',
                'sample_input': '24', 'sample_output': 'Да',
                'tests': [
                    {'input': '24', 'expected': yes_no['yes'], 'hidden': False},
                    {'input': '18', 'expected': yes_no['no'], 'hidden': True},
                    {'input': '12', 'expected': yes_no['yes'], 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Слово наоборот', 'title_kg': 'Сөздү тескери чыгаруу',
                'description_ru': 'Введи слово. Выведи его в обратном порядке.',
                'description_kg': 'Сөз киргиз. Тескерисинче чыгарып бер.',
                'sample_input': 'python', 'sample_output': 'nohtyp',
                'tests': [
                    {'input': 'python', 'expected': 'nohtyp', 'hidden': False},
                    {'input': 'салам', 'expected': 'малас', 'hidden': True},
                ],
            },
            {
                'lesson': lesson, 'title_ru': 'Целочисленное деление', 'title_kg': 'Бүтүн бөлүү жана калдык',
                'description_ru': 'Введи два числа. Выведи результат целочисленного деления и остаток через пробел.',
                'description_kg': 'Эки сан киргиз. Бүтүн бөлүүнү (//) жана калдыкты (%) боштук аркылуу чыгар.',
                'sample_input': '17\n5', 'sample_output': '3 2',
                'tests': [
                    {'input': '17\n5', 'expected': '3 2', 'hidden': False},
                    {'input': '20\n4', 'expected': '5 0', 'hidden': True},
                    {'input': '9\n2', 'expected': '4 1', 'hidden': True},
                ],
            },
        ]

        demo_titles = [item['title_ru'] for item in specs]
        old_tasks = CodingTask.objects.filter(title_ru__in=demo_titles)
        CodingSubmission.objects.filter(task__in=old_tasks).delete()
        old_tasks.delete()

        starter = '# Прочитай данные через input()\n# Напиши решение и выведи ответ через print()\n\n'
        created_tasks = []
        for order, spec in enumerate(specs, 1):
            created_tasks.append(CodingTask.objects.create(
                **spec,
                starter_code=starter,
                order=order,
                xp_reward=10,
                is_published=True,
            ))

        now = timezone.now()
        CodingSubmission.objects.create(
            task=created_tasks[0], student=student,
            code=(
                'number = int(input())\n'
                'if number > 0:\n'
                '    print("Положительное")\n'
                'else:\n'
                '    print("Отрицательное")'
            ),
            status='passed', attempts=2, passed_at=now - timedelta(hours=3),
            test_results=[
                {'number': 1, 'passed': True, 'hidden': False, 'input': '8', 'expected': 'Положительное', 'actual': 'Положительное', 'error': ''},
                {'number': 2, 'passed': True, 'hidden': True, 'input': None, 'expected': None, 'actual': None, 'error': ''},
            ],
        )
        CodingSubmission.objects.create(
            task=created_tasks[1], student=anna,
            code=(
                'number = int(input())\n'
                'if number % 5 == 0:\n'
                '    print("Делится")\n'
                'else:\n'
                '    print("Не делится")'
            ),
            status='passed', attempts=1, passed_at=now - timedelta(hours=1),
            test_results=[
                {'number': 1, 'passed': True, 'hidden': False, 'input': '25', 'expected': 'Делится', 'actual': 'Делится', 'error': ''},
                {'number': 2, 'passed': True, 'hidden': True, 'input': None, 'expected': None, 'actual': None, 'error': ''},
                {'number': 3, 'passed': True, 'hidden': True, 'input': None, 'expected': None, 'actual': None, 'error': ''},
            ],
        )
        CodingSubmission.objects.create(
            task=created_tasks[2], student=timur,
            code='first = int(input())\nsecond = int(input())\nprint(first)',
            status='failed', attempts=3,
            test_results=[
                {'number': 1, 'passed': False, 'hidden': False, 'input': '7\n12', 'expected': '12', 'actual': '7', 'error': ''},
                {'number': 2, 'passed': True, 'hidden': True, 'input': None, 'expected': None, 'actual': None, 'error': ''},
                {'number': 3, 'passed': True, 'hidden': True, 'input': None, 'expected': None, 'actual': None, 'error': ''},
            ],
        )
