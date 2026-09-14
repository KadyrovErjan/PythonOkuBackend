# 🚀 НАЧНИТЕ ОТСЮДА - ITadis CRM

## ✅ ВСЁ ГОТОВО К РАБОТЕ!

---

## 📌 ТЕКУЩИЙ СТАТУС

### ✅ Что уже сделано:
- [x] База данных очищена от старых данных
- [x] Создан владелец сайта (директор)
- [x] Backend сервер запущен
- [x] API работает и протестирован
- [x] Документация готова

### 🔑 Ваши данные для входа:
```
🌐 URL:      http://127.0.0.1:8000
👤 Login:    adambek
🔒 Password: adambek123_
🎭 Роль:     Директор (Владелец сайта)
```

---

## 🎯 ЧТО ВЫ МОЖЕТЕ ДЕЛАТЬ ПРЯМО СЕЙЧАС

### 1. Войти через API
```powershell
$body = @{login='adambek'; password='adambek123_'} | ConvertTo-Json
$r = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/auth/login/' -Method Post -Body $body -ContentType 'application/json'
Write-Host "Access Token:" $r.access
```

### 2. Войти в админ-панель
Откройте браузер: http://127.0.0.1:8000/admin

### 3. Создать первого работника
```powershell
# Сначала получите токен (см. шаг 1)
$token = $r.access
$headers = @{'Authorization' = "Bearer $token"}

# Создать кассира
$newUser = @{
    login = 'kassir1'
    password = 'kassir123'
    full_name = 'Айгуль Кассирова'
    role = 'cashier'
    is_active = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/users/' -Method Post -Headers $headers -Body $newUser -ContentType 'application/json'
```

---

## 📚 ДОКУМЕНТАЦИЯ

### 📖 Основные файлы:
1. **[QUICKSTART.md](QUICKSTART.md)** ⚡ - Быстрый старт за 2 минуты
2. **[API_CHEATSHEET.md](API_CHEATSHEET.md)** 📋 - Все API endpoints
3. **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)** 📖 - Полная инструкция
4. **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** 📂 - Структура проекта
5. **[COMPLETED_WORK.md](COMPLETED_WORK.md)** ✅ - Отчёт о работе

### 🌐 Online документация:
- **Swagger UI:** http://127.0.0.1:8000/api/schema/swagger-ui/
- **ReDoc:** http://127.0.0.1:8000/api/schema/redoc/

---

## 👥 СИСТЕМА РОЛЕЙ

### 🔴 Директор (Вы)
✅ Создание работников  
✅ Просмотр аналитики  
✅ Сбор денег со всех  
✅ Управление расходами  
✅ Полный доступ ко всему  

### 🟢 Бухгалтер (можете создать)
✅ Просмотр всех финансов  
✅ Управление расходами  
✅ Сбор денег с кассиров  
✅ Просмотр балансов  

### 🔵 Кассир (можете создать)
✅ Регистрация студентов  
✅ Прием платежей  
✅ Управление своими группами  
✅ Просмотр своих транзакций  

---

## 🔧 УПРАВЛЕНИЕ СЕРВЕРОМ

### Если сервер не запущен:
```powershell
cd backend
python manage.py runserver 8000
```

### Остановить сервер:
```
Ctrl + C в терминале
```

### Очистить БД и создать нового владельца:
```powershell
cd backend
python manage.py init_owner
```

---

## ⚡ БЫСТРЫЕ КОМАНДЫ

### Скопируйте и вставьте в PowerShell:

```powershell
# Войти как директор
$body = @{login='adambek'; password='adambek123_'} | ConvertTo-Json
$r = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/auth/login/' -Method Post -Body $body -ContentType 'application/json'
$token = $r.access
$headers = @{'Authorization' = "Bearer $token"}

# Проверить свой профиль
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/users/me/' -Headers $headers

# Создать кассира
$kassir = @{login='kassir1'; password='kassir123'; full_name='Айгуль Кассирова'; role='cashier'; is_active=$true} | ConvertTo-Json
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/users/' -Method Post -Headers $headers -Body $kassir -ContentType 'application/json'

# Создать бухгалтера
$accountant = @{login='accountant1'; password='accountant123'; full_name='Бегимай Бухгалтер'; role='accountant'; is_active=$true} | ConvertTo-Json
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/users/' -Method Post -Headers $headers -Body $accountant -ContentType 'application/json'

# Посмотреть всех работников
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/users/' -Headers $headers
```

---

## 🎓 СЛЕДУЮЩИЕ ШАГИ

### 1. Создайте работников
Используйте API или админ-панель для создания кассиров и бухгалтеров

### 2. Смените пароль
После первого входа измените пароль на более безопасный

### 3. Frontend (опционально)
Если нужен интерфейс, создайте React приложение в:
```
C:\Users\USER\Desktop\ITADISCRMFrontend
```

---

## ⚠️ ВАЖНО!

### Безопасность:
- ⚠️ Смените пароль директора после первого входа!
- ⚠️ Для production измените `SECRET_KEY` в `.env`
- ⚠️ Для production установите `DEBUG=False`

### Резервное копирование:
```powershell
# Создать backup БД
cd backend
python manage.py dumpdata > backup.json
```

---

## 🆘 ПОМОЩЬ

### Забыли пароль?
```powershell
cd backend
python manage.py init_owner
# Создаст нового владельца с паролем: director2025
```

### Сервер не запускается?
Проверьте, что PostgreSQL запущен и настройки в `backend/.env` правильные

### API не работает?
1. Проверьте, что сервер запущен: http://127.0.0.1:8000
2. Проверьте токен аутентификации
3. Посмотрите логи в `backend/logs/django.log`

---

## 📞 ПОЛЕЗНЫЕ ССЫЛКИ

- 🌐 **Backend API:** http://127.0.0.1:8000/api/v1/
- 🔧 **Admin Panel:** http://127.0.0.1:8000/admin
- 📖 **Swagger:** http://127.0.0.1:8000/api/schema/swagger-ui/
- 📚 **ReDoc:** http://127.0.0.1:8000/api/schema/redoc/

---

## 🎉 ВСЁ ГОТОВО!

**Backend полностью настроен и готов к работе!**

**Начните с [QUICKSTART.md](QUICKSTART.md) для быстрого старта! ⚡**

---

**Разработано для ITadis © 2026**
