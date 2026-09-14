# ⚡ Быстрый старт - ITadis CRM

## 🎯 За 2 минуты до первого работника!

---

## 1️⃣ Войти в систему

### Данные владельца:
```
Login:    adambek
Password: adambek123_
```

### Через PowerShell:
```powershell
# Войти и получить токен
$body = @{login='adambek'; password='adambek123_'} | ConvertTo-Json
$r = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/auth/login/' -Method Post -Body $body -ContentType 'application/json'
$token = $r.access
$headers = @{'Authorization' = "Bearer $token"}

# Проверить свой профиль
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/users/me/' -Headers $headers
```

---

## 2️⃣ Создать первого кассира

```powershell
$kassir = @{
    login = 'kassir1'
    password = 'kassir123'
    full_name = 'Айгуль Кассирова'
    role = 'cashier'
    is_active = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/users/' -Method Post -Headers $headers -Body $kassir -ContentType 'application/json'
```

**Готово!** Теперь кассир может войти:
- Login: `kassir1`
- Password: `kassir123`

---

## 3️⃣ Создать бухгалтера

```powershell
$accountant = @{
    login = 'accountant1'
    password = 'accountant123'
    full_name = 'Бегимай Бухгалтер'
    role = 'accountant'
    is_active = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/users/' -Method Post -Headers $headers -Body $accountant -ContentType 'application/json'
```

**Готово!** Бухгалтер может войти:
- Login: `accountant1`
- Password: `accountant123`

---

## 4️⃣ Посмотреть всех работников

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/users/' -Headers $headers
```

---

## 🎨 Или через админ-панель

1. Откройте: http://127.0.0.1:8000/admin
2. Войдите: `adambek` / `adambek123_`
3. Перейдите в "Пользователи"
4. Нажмите "Добавить пользователя"
5. Заполните форму и сохраните

---

## 🚀 Полезные ссылки

- **API:** http://127.0.0.1:8000/api/v1/
- **Admin:** http://127.0.0.1:8000/admin
- **Swagger:** http://127.0.0.1:8000/api/schema/swagger-ui/
- **Документация:** [API_CHEATSHEET.md](API_CHEATSHEET.md)

---

## 💡 Роли в системе

### 🔴 Директор
- Создает работников
- Видит аналитику
- Собирает деньги со всех
- Полный доступ

### 🟢 Бухгалтер
- Видит все финансы
- Создает расходы
- Собирает деньги с кассиров
- Видит балансы

### 🔵 Кассир
- Регистрирует студентов
- Принимает платежи
- Управляет своими группами
- Видит свои транзакции

---

## ⚠️ Важно!

После создания работников **измените пароли** на более безопасные!

```powershell
# Войти как работник
$body = @{login='kassir1'; password='kassir123'} | ConvertTo-Json
$r = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/auth/login/' -Method Post -Body $body -ContentType 'application/json'
$token = $r.access
$headers = @{'Authorization' = "Bearer $token"}

# Сменить пароль
$pwd = @{
    old_password = 'kassir123'
    new_password = 'new_secure_password'
} | ConvertTo-Json

Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/users/me/change-password/' -Method Patch -Headers $headers -Body $pwd -ContentType 'application/json'
```

---

**Готово! Теперь можно работать! 🎉**
