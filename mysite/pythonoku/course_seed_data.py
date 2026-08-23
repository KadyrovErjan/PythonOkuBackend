COURSE_TITLE = 'Python программалоо'

COURSE_DESCRIPTION = (
    'Основы Python для первого занятия: типы данных, арифметика, сравнения, '
    'условные операторы, строки, методы строк, индексация и срезы.'
)


LESSONS = [
    {
        'title': 'Python программалоо курсу | 1-сабак, 1-бөлүм',
        'description': 'Типы данных: int, float, str, bool.',
        'youtube_url': 'https://youtu.be/3DrnjT8eNjk',
        'duration_minutes': 45,
        'xp_reward': 15,
        'content': '''PYTHON — КОНСПЕКТ УРОКА

1. Типы данных

int — целые числа
Примеры:
5
-10
745

float — дробные числа
Примеры:
3.14
-2.5
654.645

str — строки
Строки записываются в кавычках:
'hello'
"world"
'645'

bool — логический тип
Имеет только два значения:
True
False

Коротко:
• int нужен для целых чисел
• float нужен для дробных чисел
• str нужен для текста
• bool нужен для логики True / False
''',
        'quizzes': [
            {
                'question': 'Какой тип данных используется для целых чисел?',
                'option_a': 'str',
                'option_b': 'float',
                'option_c': 'int',
                'option_d': 'bool',
                'correct': 'c',
            },
            {
                'question': 'Какие значения может иметь тип bool?',
                'option_a': 'Yes и No',
                'option_b': 'True и False',
                'option_c': '1 и 2',
                'option_d': 'int и str',
                'correct': 'b',
            },
            {
                'question': 'Как правильно записать строку в Python?',
                'option_a': 'hello',
                'option_b': '123',
                'option_c': '"hello"',
                'option_d': 'True',
                'correct': 'c',
            },
        ],
    },
    {
        'title': 'Python программалоо курсу | 1-сабак, 2-бөлүм',
        'description': 'Арифметические операции в Python.',
        'youtube_url': 'https://youtu.be/WPz2LYSCoMU',
        'duration_minutes': 25,
        'xp_reward': 15,
        'content': '''PYTHON — КОНСПЕКТ УРОКА

2. Арифметические операции

Сложение: +
Пример:
3 + 4 = 7

Вычитание: -
Пример:
7 - 2 = 5

Умножение: *
Пример:
2 * 2 = 4

Деление: /
Пример:
8 / 2 = 4

Целочисленное деление: //
Пример:
9 // 2 = 4

Остаток: %
Пример:
9 % 2 = 1

Степень: **
Пример:
2 ** 3 = 8

Округление:
round(5.6)   # 6
''',
        'quizzes': [
            {
                'question': 'Что получится при 9 // 2?',
                'option_a': '4',
                'option_b': '4.5',
                'option_c': '5',
                'option_d': '1',
                'correct': 'a',
            },
            {
                'question': 'Что показывает оператор %?',
                'option_a': 'Степень',
                'option_b': 'Остаток от деления',
                'option_c': 'Целочисленное деление',
                'option_d': 'Округление',
                'correct': 'b',
            },
            {
                'question': 'Чему равно 2 ** 3?',
                'option_a': '5',
                'option_b': '6',
                'option_c': '8',
                'option_d': '9',
                'correct': 'c',
            },
        ],
    },
    {
        'title': 'Python программалоо курсу | 1-сабак, 3-бөлүм',
        'description': 'Операции сравнения: ==, !=, >, <, >=, <=.',
        'youtube_url': '',
        'duration_minutes': 18,
        'xp_reward': 15,
        'content': '''PYTHON — КОНСПЕКТ УРОКА

3. Операции сравнения

Оператор == означает равно.
Оператор != означает не равно.
Оператор > означает больше.
Оператор < означает меньше.
Оператор >= означает больше или равно.
Оператор <= означает меньше или равно.

Пример:
x = 5
print(x > 3)   # True

Сравнение возвращает логический результат:
True или False.
''',
        'quizzes': [
            {
                'question': 'Какой оператор означает “равно”?',
                'option_a': '=',
                'option_b': '==',
                'option_c': '!=',
                'option_d': '>=',
                'correct': 'b',
            },
            {
                'question': 'Что выведет print(5 > 3)?',
                'option_a': 'False',
                'option_b': '5',
                'option_c': 'True',
                'option_d': '3',
                'correct': 'c',
            },
            {
                'question': 'Какой оператор означает “не равно”?',
                'option_a': '!=',
                'option_b': '==',
                'option_c': '<=',
                'option_d': '>',
                'correct': 'a',
            },
        ],
    },
    {
        'title': 'Python программалоо курсу | 1-сабак, 4-бөлүм',
        'description': 'Условные операторы if / elif / else.',
        'youtube_url': '',
        'duration_minutes': 30,
        'xp_reward': 15,
        'content': '''PYTHON — КОНСПЕКТ УРОКА

4. Условные операторы (if / elif / else)

Структура:
if условие:
    код
elif условие:
    код
else:
    код

Пример 1:
number = int(input('Сан жаз: '))

if number > 0:
    print('+ сан')
elif number < 0:
    print('- сан')
else:
    print('0го барабар')

Пример 2:
age = int(input('Жашынды жаз: '))

if age > 18:
    print('18ден чон')
elif age < 18:
    print('18ден кичине')
else:
    print('18ге барабар')

Важно:
• else пишется без условия
• отступы обязательны
''',
        'quizzes': [
            {
                'question': 'Как правильно пишется else?',
                'option_a': 'else number > 0:',
                'option_b': 'else:',
                'option_c': 'else()',
                'option_d': 'else = True',
                'correct': 'b',
            },
            {
                'question': 'Для чего нужен elif?',
                'option_a': 'Для дополнительного условия',
                'option_b': 'Для вывода текста',
                'option_c': 'Для создания строки',
                'option_d': 'Для округления',
                'correct': 'a',
            },
            {
                'question': 'Что обязательно после строки if condition: ?',
                'option_a': 'Кавычки',
                'option_b': 'Отступ у кода внутри блока',
                'option_c': 'Оператор //',
                'option_d': 'Метод upper()',
                'correct': 'b',
            },
        ],
    },
    {
        'title': 'Python программалоо курсу | 1-сабак, 5-бөлүм',
        'description': 'Строки и основные методы строк.',
        'youtube_url': '',
        'duration_minutes': 28,
        'xp_reward': 15,
        'content': '''PYTHON — КОНСПЕКТ УРОКА

5. Строки и методы строк

Пример:
word = input('name: ')

print(word.upper())
print(word.capitalize())
print(len(word))

Основные методы:
• lower() — делает строку маленькими буквами
• upper() — делает строку большими буквами
• capitalize() — первая буква большая
• title() — каждое слово с большой буквы
• len() — длина строки
• count('a') — сколько раз встречается символ
• replace('a', 'b') — заменить символ
• split() — разделить строку
• join() — соединить строки

Пример проверки страны:
country = input('country: ').lower()

if country == 'кыргызстан':
    print('Салам')
elif country == 'россия':
    print('Привет')
elif country == 'америка':
    print('Hello')
else:
    print('Error')
''',
        'quizzes': [
            {
                'question': 'Что делает upper()?',
                'option_a': 'Делает строку маленькими буквами',
                'option_b': 'Делает строку большими буквами',
                'option_c': 'Считает длину строки',
                'option_d': 'Удаляет строку',
                'correct': 'b',
            },
            {
                'question': 'Как получить длину строки word?',
                'option_a': 'word.length',
                'option_b': 'count(word)',
                'option_c': 'len(word)',
                'option_d': 'word.size()',
                'correct': 'c',
            },
            {
                'question': 'Какой метод заменяет символы в строке?',
                'option_a': 'replace()',
                'option_b': 'split()',
                'option_c': 'join()',
                'option_d': 'round()',
                'correct': 'a',
            },
        ],
    },
    {
        'title': 'Python программалоо курсу | 1-сабак, 6-бөлүм',
        'description': 'Индексация, отрицательные индексы и срезы.',
        'youtube_url': '',
        'duration_minutes': 20,
        'xp_reward': 15,
        'content': '''PYTHON — КОНСПЕКТ УРОКА

6. Индексация (Index)

Что такое индекс?
Индекс — это номер позиции элемента в строке.
В Python индексация начинается с 0.

Пример:
Слово:  P  y  t  h  o  n
Индекс: 0  1  2  3  4  5

Получение символа по индексу:
word = "Python"

print(word[0])   # P
print(word[1])   # y
print(word[5])   # n

Отрицательная индексация:
-1 — последний символ
-2 — предпоследний

word = "Python"

print(word[-1])   # n
print(word[-2])   # o

Получение первой и последней буквы:
word = input('Соз жаз: ')

print("Биринчи тамга:", word[0])
print("Акыркы тамга:", word[-1])

Срезы (Slicing)
Формат:
строка[start:end]

Пример:
word = "Python"

print(word[0:3])   # Pyt
print(word[2:5])   # tho

Важно:
• start включается
• end не включается

Полный срез:
word = "Python"
print(word[:3])    # Pyt
print(word[2:])    # thon

Разворот строки:
word = "Python"
print(word[::-1])   # nohtyP
''',
        'quizzes': [
            {
                'question': 'С какого числа начинается индексация в Python?',
                'option_a': '0',
                'option_b': '1',
                'option_c': '-1',
                'option_d': '10',
                'correct': 'a',
            },
            {
                'question': 'Что означает индекс -1?',
                'option_a': 'Первый символ',
                'option_b': 'Последний символ',
                'option_c': 'Ошибка',
                'option_d': 'Длина строки',
                'correct': 'b',
            },
            {
                'question': 'Как развернуть строку word наоборот?',
                'option_a': 'word[0]',
                'option_b': 'word[::-1]',
                'option_c': 'word.upper()',
                'option_d': 'word[1:1]',
                'correct': 'b',
            },
        ],
    },
]
