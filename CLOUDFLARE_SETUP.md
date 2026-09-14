# ☁️ Настройка Cloudflare для ITAdis CRM

> Подробная инструкция по настройке DNS и SSL через Cloudflare

---

## 📋 Содержание

1. [Регистрация в Cloudflare](#1-регистрация-в-cloudflare)
2. [Добавление домена](#2-добавление-домена)
3. [Изменение NS записей у регистратора](#3-изменение-ns-записей-у-регистратора)
4. [Настройка DNS записей](#4-настройка-dns-записей)
5. [Настройка SSL/TLS](#5-настройка-ssltls)
6. [Дополнительные настройки](#6-дополнительные-настройки)
7. [Проверка](#7-проверка)

---

## 1. Регистрация в Cloudflare

### 1.1 Создание аккаунта

1. Перейдите на https://dash.cloudflare.com/sign-up
2. Введите ваш email и пароль
3. Подтвердите email через письмо

### 1.2 Первый вход

После регистрации вы попадете на Dashboard:
```
https://dash.cloudflare.com/
```

---

## 2. Добавление домена

### 2.1 Add a Site

1. На Dashboard нажмите **"Add a Site"**
2. Введите ваш домен: `itadiscrm.com.kg`
3. Нажмите **"Add site"**

### 2.2 Выбор плана

1. Выберите план **Free** ($0/month)
2. Нажмите **"Continue"**

### 2.3 DNS Records Scan

Cloudflare автоматически просканирует ваши существующие DNS записи.

1. Подождите завершения сканирования
2. Нажмите **"Continue"**

---

## 3. Изменение NS записей у регистратора

### 3.1 Получение Nameservers от Cloudflare

После добавления домена Cloudflare покажет 2 nameserver'а:

**Пример (ваши будут отличаться):**
```
christian.ns.cloudflare.com
ulla.ns.cloudflare.com
```

**Важно:** Скопируйте эти значения!

### 3.2 Изменение у регистратора

Для домена `itadiscrm.com.kg` (регистратор в Кыргызстане):

#### Вариант A: Через Kyrgyzstan Domain Registrar

1. Войдите в панель регистратора домена (где купили домен)
   - Обычно это https://domain.kg/ или https://cctld.kg/
   - Или ваш конкретный регистратор

2. Найдите раздел:
   - "DNS Management" или
   - "Nameservers" или
   - "Name Servers" или
   - "NS Records"

3. Измените существующие NS записи на:
   ```
   NS1: christian.ns.cloudflare.com
   NS2: ulla.ns.cloudflare.com
   ```
   (Замените на ваши NS от Cloudflare!)

4. Сохраните изменения

#### Пример для популярных регистраторов:

**domain.kg:**
```
Личный кабинет → Мои домены → itadiscrm.com.kg → DNS → NS серверы
```

**cctld.kg:**
```
Account → Domains → itadiscrm.com.kg → Management → Nameservers
```

### 3.3 Ожидание активации

⏰ **Важно:** DNS изменения занимают от 1 часа до 24 часов!

Cloudflare будет проверять статус каждые несколько минут.

Вы получите email когда домен станет активным:
```
Subject: Cloudflare: itadiscrm.com.kg is now active on Cloudflare
```

### 3.4 Проверка активации

В Cloudflare Dashboard проверьте статус:
- ✅ **Active** - домен работает
- 🟡 **Pending** - ожидание изменения NS
- ❌ **Moved** - домен перенесен

---

## 4. Настройка DNS записей

### 4.1 Открытие DNS Management

1. **Cloudflare Dashboard** → ваш домен (`itadiscrm.com.kg`)
2. Боковое меню → **DNS** → **Records**

### 4.2 Добавление A Records для Backend и Frontend

#### Запись 1: Корневой домен (@)

Нажмите **"Add record"**:

| Field | Value |
|-------|-------|
| Type | `A` |
| Name | `@` |
| IPv4 address | `ваш-elastic-ip` (например: 13.127.45.123) |
| Proxy status | 🧡 Proxied (оранжевое облачко) |
| TTL | Auto |

Нажмите **"Save"**

#### Запись 2: www поддомен

Нажмите **"Add record"**:

| Field | Value |
|-------|-------|
| Type | `A` |
| Name | `www` |
| IPv4 address | `ваш-elastic-ip` |
| Proxy status | 🧡 Proxied |
| TTL | Auto |

Нажмите **"Save"**

#### Запись 3: API поддомен

Нажмите **"Add record"**:

| Field | Value |
|-------|-------|
| Type | `A` |
| Name | `api` |
| IPv4 address | `ваш-elastic-ip` |
| Proxy status | 🧡 Proxied |
| TTL | Auto |

Нажмите **"Save"**

### 4.3 Итоговые DNS записи

После добавления у вас должно быть минимум 3 записи:

| Type | Name | Content | Proxy Status | TTL |
|------|------|---------|--------------|-----|
| A | @ | 13.127.45.123 | 🧡 Proxied | Auto |
| A | www | 13.127.45.123 | 🧡 Proxied | Auto |
| A | api | 13.127.45.123 | 🧡 Proxied | Auto |

### 4.4 Понимание Proxy Status

**🧡 Proxied (оранжевое облачко):**
- Трафик идет через Cloudflare CDN
- Защита от DDoS
- Кеширование статических файлов
- SSL от Cloudflare

**⚪ DNS only (серое облачко):**
- Прямое подключение к серверу
- Без защиты Cloudflare
- Нужно для некоторых сервисов (например, Vercel CNAME)

**Для нашего случая используем Proxied!**

---

## 5. Настройка SSL/TLS

### 5.1 SSL/TLS Encryption Mode

1. **Cloudflare Dashboard** → ваш домен
2. Боковое меню → **SSL/TLS**
3. Вкладка **Overview**

Выберите режим:
```
🔒 Full (strict) - Рекомендуется
```

**Описание режимов:**

| Режим | Описание |
|-------|----------|
| Off | ❌ Без SSL |
| Flexible | ⚠️ SSL только Cloudflare ↔ Браузер |
| Full | ✅ SSL везде, но без проверки сертификата |
| **Full (strict)** | ✅✅ SSL везде + проверка валидного сертификата |

**Важно:** Для Full (strict) нужен валидный SSL на сервере (Let's Encrypt)!

### 5.2 Edge Certificates

Вкладка **Edge Certificates**:

#### Включите:

- ✅ **Always Use HTTPS** - ON
  - Автоматический редирект HTTP → HTTPS

- ✅ **Automatic HTTPS Rewrites** - ON
  - Автоматическая замена HTTP ссылок на HTTPS

- ✅ **Minimum TLS Version** - TLS 1.2 (или 1.3)

- ✅ **Opportunistic Encryption** - ON

- ✅ **TLS 1.3** - ON (если доступно)

#### Опционально:

- ⚪ **HTTP Strict Transport Security (HSTS)** - можно включить после проверки

### 5.3 Проверка SSL Certificate

После активации домена Cloudflare автоматически выпустит SSL сертификат:

1. **SSL/TLS** → **Edge Certificates**
2. Найдите раздел **Edge Certificates**
3. Должен быть сертификат для:
   ```
   *.itadiscrm.com.kg
   itadiscrm.com.kg
   ```

Статус: **Active** ✅

---

## 6. Дополнительные настройки

### 6.1 Caching (Кеширование)

**Cloudflare Dashboard** → **Caching** → **Configuration**

#### Базовые настройки:

- **Caching Level**: Standard
- **Browser Cache TTL**: Respect Existing Headers
- **Crawler Hints**: ON

#### Создание Page Rules для оптимизации:

**Rules** → **Page Rules** → **Create Page Rule**

**Правило 1: Кеш для статики**
```
URL Pattern: *itadiscrm.com.kg/static/*

Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month
  - Browser Cache TTL: 1 month
```

**Правило 2: Кеш для медиа**
```
URL Pattern: *itadiscrm.com.kg/media/*

Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 week
  - Browser Cache TTL: 1 week
```

**Правило 3: Без кеша для API**
```
URL Pattern: *api.itadiscrm.com.kg/api/*

Settings:
  - Cache Level: Bypass
```

**Лимиты:** Free план = 3 Page Rules

### 6.2 Speed (Оптимизация скорости)

**Cloudflare Dashboard** → **Speed** → **Optimization**

Включите:
- ✅ **Auto Minify**
  - [x] JavaScript
  - [x] CSS
  - [x] HTML
  
- ✅ **Brotli** - ON

- ✅ **Rocket Loader** - OFF (может ломать некоторые JS)

- ✅ **Early Hints** - ON

### 6.3 Security (Безопасность)

**Cloudflare Dashboard** → **Security**

#### Security Level
```
Medium - рекомендуется
```

#### Bot Fight Mode (Free plan)
```
✅ ON - защита от ботов
```

#### Challenge Passage
```
30 minutes
```

### 6.4 Firewall Rules (опционально)

Для более продвинутой защиты:

**Security** → **WAF** → **Firewall rules**

Создайте правила, например:
- Блокировка определенных стран
- Ограничение запросов с определенных IP
- Защита админ-панели

**Пример правила защиты /admin:**
```
Field: URI Path
Operator: contains
Value: /admin

Action: Challenge (CAPTCHA)
```

---

## 7. Проверка

### 7.1 DNS Propagation

Проверьте, что DNS изменения распространились:

**Онлайн инструменты:**
- https://dnschecker.org/
- https://www.whatsmydns.net/

Введите: `itadiscrm.com.kg`

Должны видеть ваш Elastic IP или Cloudflare IP (если Proxied).

### 7.2 SSL Certificate

Проверьте SSL:

**Браузер:**
1. Откройте https://itadiscrm.com.kg
2. Кликните на замок 🔒 в адресной строке
3. Сертификат должен быть от Cloudflare

**Онлайн тест:**
- https://www.ssllabs.com/ssltest/
- Введите: `itadiscrm.com.kg`
- Должен быть рейтинг A или A+

**Команда:**
```bash
curl -I https://itadiscrm.com.kg

# Должен вернуть HTTP/2 200 с headers от Cloudflare
```

### 7.3 Проверка всех доменов

Проверьте в браузере:

- ✅ https://itadiscrm.com.kg
- ✅ https://www.itadiscrm.com.kg
- ✅ https://api.itadiscrm.com.kg

Все должны работать с валидным SSL!

### 7.4 Analytics

**Cloudflare Dashboard** → **Analytics & Logs** → **Traffic**

Через некоторое время увидите:
- Requests (количество запросов)
- Bandwidth (трафик)
- Threats blocked (заблокированные угрозы)
- Status codes

---

## 🎯 Итоговая конфигурация

### DNS Records
```
Type  Name    Content           Proxy    TTL
A     @       13.127.45.123     Proxied  Auto
A     www     13.127.45.123     Proxied  Auto
A     api     13.127.45.123     Proxied  Auto
```

### SSL/TLS
```
Mode: Full (strict)
Always Use HTTPS: ON
Auto HTTPS Rewrites: ON
Min TLS: 1.2
```

### Page Rules
```
1. *itadiscrm.com.kg/static/* → Cache Everything
2. *itadiscrm.com.kg/media/*  → Cache Everything
3. *api.itadiscrm.com.kg/api/* → Bypass Cache
```

### Security
```
Level: Medium
Bot Fight Mode: ON
```

---

## 🐛 Troubleshooting

### DNS не резолвится

**Проблема:** `nslookup itadiscrm.com.kg` не возвращает IP

**Решение:**
1. Проверьте, что NS записи изменены у регистратора
2. Подождите 24 часа для propagation
3. Очистите DNS кеш:
   ```bash
   # Windows
   ipconfig /flushdns
   
   # Linux
   sudo systemd-resolve --flush-caches
   
   # Mac
   sudo dscacheutil -flushcache
   ```

### SSL ошибка "Certificate Invalid"

**Проблема:** Браузер показывает ошибку сертификата

**Решение:**
1. Убедитесь, что на сервере установлен Let's Encrypt
2. В Cloudflare: SSL/TLS mode = Full (strict)
3. Проверьте, что домен активен (не Pending)
4. Подождите 5-10 минут после активации

### 502 Bad Gateway от Cloudflare

**Проблема:** Cloudflare не может подключиться к серверу

**Решение:**
1. Проверьте, что сервер доступен:
   ```bash
   curl http://ваш-elastic-ip
   ```
2. Проверьте Security Groups в AWS (порты 80, 443 открыты)
3. Проверьте статус Nginx:
   ```bash
   sudo systemctl status nginx
   ```

### Домен не активируется

**Проблема:** Cloudflare показывает "Pending"

**Решение:**
1. Перепроверьте NS записи у регистратора
2. Нажмите "Check nameservers" в Cloudflare
3. Свяжитесь с регистратором домена
4. Подождите до 24 часов

---

## 📚 Полезные ссылки

- **Cloudflare Documentation**: https://developers.cloudflare.com/
- **DNS Management**: https://developers.cloudflare.com/dns/
- **SSL/TLS**: https://developers.cloudflare.com/ssl/
- **Page Rules**: https://developers.cloudflare.com/rules/page-rules/
- **Support**: https://support.cloudflare.com/

---

## ✅ Checklist

- [ ] Аккаунт Cloudflare создан
- [ ] Домен добавлен в Cloudflare
- [ ] NS записи изменены у регистратора
- [ ] Домен активирован (статус Active)
- [ ] DNS A records добавлены (@, www, api)
- [ ] SSL/TLS режим: Full (strict)
- [ ] Always Use HTTPS включен
- [ ] Page Rules созданы (опционально)
- [ ] Проверка DNS через dnschecker.org
- [ ] Проверка SSL через ssllabs.com
- [ ] Все домены работают в браузере

---

**Готово! Cloudflare настроен! ☁️✅**

Теперь ваш сайт защищен, ускорен и имеет бесплатный SSL! 🚀
