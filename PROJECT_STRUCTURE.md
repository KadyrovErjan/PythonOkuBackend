# 📂 Структура проекта ITadis CRM

## 🎯 Разделение на Backend и Frontend

Проект разделен на две независимые части:

### 1️⃣ Backend (Django REST API)
📍 **Расположение:** `C:\Users\USER\Desktop\ITAdisCRMBackend\backend`

```
ITAdisCRMBackend/
├── backend/
│   ├── itadis_app/           # Основное приложение
│   │   ├── models.py         # Модели данных
│   │   ├── serializers.py    # Сериализаторы для API
│   │   ├── permissions.py    # Права доступа по ролям
│   │   ├── views/            # API endpoints
│   │   │   ├── auth.py       # Аутентификация
│   │   │   ├── users.py      # Управление пользователями
│   │   │   ├── groups.py     # Группы
│   │   │   ├── students.py   # Студенты
│   │   │   ├── transactions.py # Транзакции
│   │   │   ├── balances.py   # Балансы
│   │   │   ├── collections.py # Сборы
│   │   │   ├── expenses.py   # Расходы
│   │   │   └── analytics.py  # Аналитика
│   │   ├── services/         # Бизнес-логика
│   │   │   ├── finance.py    # Финансовые операции
│   │   │   ├── analytics.py  # Расчёт аналитики
│   │   │   └── audit.py      # Логирование
│   │   └── management/       # Django команды
│   │       └── commands/
│   │           └── init_owner.py  # Инициализация владельца
│   ├── mysite/               # Настройки проекта
│   │   ├── settings.py       # Конфигурация Django
│   │   ├── urls.py           # Главный роутинг
│   │   └── wsgi.py
│   ├── media/                # Загруженные файлы
│   ├── logs/                 # Логи приложения
│   ├── .env                  # Переменные окружения
│   ├── requirements.txt      # Python зависимости
│   ├── Dockerfile            # Docker для backend
│   └── docker-compose.yml    # Docker Compose
├── README.md                 # Основная документация
├── SETUP_INSTRUCTIONS.md     # Инструкция по настройке
├── API_CHEATSHEET.md         # Шпаргалка по API
└── PROJECT_STRUCTURE.md      # Этот файл
```

**Технологии:**
- Django 5.1.4
- Django REST Framework 3.15.2
- PostgreSQL 15
- JWT аутентификация
- Docker + Gunicorn + Nginx

**Запущено на:** http://127.0.0.1:8000

---

### 2️⃣ Frontend (React SPA)
📍 **Расположение:** `C:\Users\USER\Desktop\ITADISCRMFrontend` (нужно создать)

```
ITADISCRMFrontend/
├── src/
│   ├── components/           # React компоненты
│   │   ├── Auth/             # Компоненты аутентификации
│   │   ├── Dashboard/        # Дашборды по ролям
│   │   ├── Users/            # Управление пользователями
│   │   ├── Groups/           # Управление группами
│   │   ├── Students/         # Управление студентами
│   │   ├── Finance/          # Финансовые компоненты
│   │   ├── Analytics/        # Аналитика
│   │   └── Common/           # Общие компоненты
│   ├── pages/                # Страницы приложения
│   │   ├── LoginPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── UsersPage.jsx
│   │   ├── GroupsPage.jsx
│   │   ├── StudentsPage.jsx
│   │   ├── FinancePage.jsx
│   │   └── AnalyticsPage.jsx
│   ├── services/             # API сервисы
│   │   ├── api.js            # Axios конфигурация
│   │   ├── authService.js    # Аутентификация
│   │   ├── userService.js    # Пользователи
│   │   ├── groupService.js   # Группы
│   │   ├── studentService.js # Студенты
│   │   └── financeService.js # Финансы
│   ├── store/                # State management
│   │   └── authStore.js      # Zustand store для auth
│   ├── hooks/                # Custom React hooks
│   │   └── useAuth.js
│   ├── utils/                # Утилиты
│   │   ├── constants.js      # Константы
│   │   └── helpers.js        # Вспомогательные функции
│   ├── router/               # React Router настройки
│   │   └── index.jsx
│   ├── App.jsx               # Главный компонент
│   └── main.jsx              # Точка входа
├── public/                   # Статические файлы
├── .env                      # Переменные окружения
├── package.json              # Node.js зависимости
├── vite.config.js            # Vite конфигурация
└── tailwind.config.js        # Tailwind CSS

```

**Технологии (планируемые):**
- React 18
- Vite
- React Router v6
- TanStack Query (React Query)
- Zustand (state management)
- Tailwind CSS
- Axios

**Будет запущен на:** http://localhost:5173 (Vite dev server)

---

## 🔗 Связь между Backend и Frontend

### API Communication
Frontend общается с Backend через REST API:

```
Frontend (React)  ←→  Backend (Django REST)
localhost:5173         localhost:8000/api/v1/
```

### CORS настройки
В `backend/.env` настроены разрешенные домены:
```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Аутентификация
1. Frontend отправляет логин/пароль на `/api/v1/auth/login/`
2. Backend возвращает JWT токены (access + refresh)
3. Frontend сохраняет токены в localStorage/sessionStorage
4. Все запросы отправляются с заголовком: `Authorization: Bearer <token>`
5. При истечении access токена используется refresh токен

---

## 👥 Разделение по ролям

### Директор (director)
**Backend:**
- Полный доступ к API
- Создание/управление пользователями
- Доступ к аналитике
- Сбор денег
- Управление расходами

**Frontend (страницы):**
- Dashboard с общей статистикой
- Управление работниками
- Аналитика (графики, отчёты)
- Все финансовые операции
- Просмотр всех данных

### Бухгалтер (accountant)
**Backend:**
- Просмотр всех финансов
- Создание расходов
- Сбор денег с кассиров
- Просмотр балансов

**Frontend (страницы):**
- Dashboard с финансами
- Балансы всех сотрудников
- Расходы
- Сборы денег
- Транзакции (все)

### Кассир (cashier)
**Backend:**
- Регистрация студентов
- Прием платежей
- Управление своими группами
- Просмотр своих транзакций

**Frontend (страницы):**
- Dashboard со своими группами
- Свои группы
- Свои студенты
- Регистрация студентов
- Прием платежей
- Свой баланс

---

## 🚀 Запуск проекта

### Backend
```powershell
cd C:\Users\USER\Desktop\ITAdisCRMBackend\backend
python manage.py runserver 8000
```

### Frontend (когда будет создан)
```powershell
cd C:\Users\USER\Desktop\ITADISCRMFrontend
npm install
npm run dev
```

---

## 📋 Текущий статус

### ✅ Готово
- [x] Backend полностью настроен
- [x] База данных инициализирована
- [x] Создан владелец сайта (директор)
- [x] API endpoints готовы
- [x] Документация API
- [x] JWT аутентификация
- [x] Разделение прав по ролям
- [x] Backend запущен и работает

### 📝 В планах
- [ ] Создать структуру Frontend проекта
- [ ] Настроить React + Vite
- [ ] Создать компоненты аутентификации
- [ ] Настроить роутинг
- [ ] Создать API сервисы
- [ ] Создать дашборды для каждой роли
- [ ] Добавить формы для работы с данными
- [ ] Стилизация с Tailwind CSS

---

## 🔐 Владелец сайта

**Текущий владелец:**
```
Login:    director
Password: director2025
Роль:     Директор
```

**Возможности:**
- Доступ к админ-панели: http://127.0.0.1:8000/admin
- Создание работников через API
- Полный доступ к системе
- Просмотр аналитики

---

## 📞 API Endpoints (краткая справка)

```
🔐 Аутентификация:
POST   /api/v1/auth/login/
POST   /api/v1/auth/refresh/
POST   /api/v1/auth/logout/

👥 Пользователи (директор):
GET    /api/v1/users/
POST   /api/v1/users/
GET    /api/v1/users/me/

📚 Группы:
GET    /api/v1/groups/
POST   /api/v1/groups/

👨‍🎓 Студенты:
GET    /api/v1/students/
POST   /api/v1/students/register/
POST   /api/v1/students/{id}/payments/

💰 Финансы:
GET    /api/v1/balances/
POST   /api/v1/collections/
POST   /api/v1/expenses/

📊 Аналитика (директор):
GET    /api/v1/analytics/summary/
GET    /api/v1/analytics/monthly/
```

---

## 🛠️ Полезные команды

### Очистка и инициализация БД
```powershell
cd backend
python manage.py init_owner
```

### Создание миграций
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Доступ к Django shell
```powershell
python manage.py shell
```

---

**Разработано для ITadis © 2026**
