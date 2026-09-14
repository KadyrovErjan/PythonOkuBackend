# 🎨 Frontend Deployment на Vercel - ITAdis CRM

## 📋 Содержание
1. [Подготовка Frontend проекта](#1-подготовка-frontend-проекта)
2. [Создание аккаунта на Vercel](#2-создание-аккаунта-на-vercel)
3. [Деплой на Vercel](#3-деплой-на-vercel)
4. [Настройка переменных окружения](#4-настройка-переменных-окружения)
5. [Подключение домена](#5-подключение-домена)
6. [Финальная проверка](#6-финальная-проверка)

---

## 1. Подготовка Frontend проекта

### 1.1 Структура проекта

Frontend проект должен быть готов к деплою на Vercel. Типичная структура:

```
frontend/
├── public/
├── src/
│   ├── components/
│   ├── pages/
│   ├── api/
│   │   └── config.js  # Конфигурация API
│   └── App.jsx
├── package.json
├── vite.config.js / next.config.js
└── .env.example
```

### 1.2 Настройка API endpoint

Создайте файл конфигурации API (если его нет):

**`src/config/api.js`**
```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE_URL = `${API_URL}/api/v1`;

export const config = {
  apiUrl: API_URL,
  apiBaseUrl: API_BASE_URL,
  endpoints: {
    auth: {
      login: `${API_BASE_URL}/auth/login/`,
      logout: `${API_BASE_URL}/auth/logout/`,
      refresh: `${API_BASE_URL}/auth/token/refresh/`,
      me: `${API_BASE_URL}/auth/me/`,
    },
    students: `${API_BASE_URL}/students/`,
    groups: `${API_BASE_URL}/groups/`,
    transactions: `${API_BASE_URL}/transactions/`,
    // ... другие endpoints
  },
};

export default config;
```

### 1.3 Создайте .env.example

**`.env.example`**
```env
# API Configuration
VITE_API_URL=https://api.itadiscrm.com.kg

# Application Settings
VITE_APP_NAME=ITAdis CRM
VITE_APP_VERSION=1.0.0
```

### 1.4 Обновите package.json

Убедитесь, что есть build скрипт:

```json
{
  "name": "itadis-crm-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0"
  }
}
```

### 1.5 Проверка локально

```bash
# Установка зависимостей
npm install

# Локальная сборка
npm run build

# Проверка сборки
npm run preview
```

---

## 2. Создание аккаунта на Vercel

### 2.1 Регистрация

1. Перейдите на https://vercel.com/
2. Нажмите **Sign Up**
3. Выберите **Continue with GitHub** (рекомендуется)
4. Авторизуйте Vercel для доступа к GitHub

### 2.2 Подключение GitHub репозитория

1. Убедитесь, что ваш frontend код залит на GitHub
2. Репозиторий может быть:
   - Публичным
   - Приватным (Vercel имеет доступ через OAuth)

---

## 3. Деплой на Vercel

### 3.1 Импорт проекта

1. **Vercel Dashboard** → **Add New** → **Project**
2. Выберите **Import Git Repository**
3. Найдите ваш frontend репозиторий (например: `ITAdisCRMFrontend`)
4. Нажмите **Import**

### 3.2 Настройка проекта

**Configure Project:**

1. **Project Name**: `itadis-crm-frontend` (или любое другое)
2. **Framework Preset**: 
   - Vite → выберите `Vite`
   - Next.js → автоопределится
   - React → выберите `Create React App`
3. **Root Directory**: 
   - Если frontend в корне: `.`
   - Если в подпапке: `frontend`
4. **Build Command**: 
   ```bash
   npm run build
   ```
   (обычно автоопределяется)
5. **Output Directory**: 
   - Vite: `dist`
   - Next.js: `.next`
   - CRA: `build`
6. **Install Command**: 
   ```bash
   npm install
   ```

### 3.3 Деплой

Нажмите **Deploy** и ждите ~2-3 минуты.

Vercel автоматически:
- Установит зависимости
- Соберет проект
- Задеплоит на свой домен (например: `itadis-crm-frontend.vercel.app`)

---

## 4. Настройка переменных окружения

### 4.1 Добавление Environment Variables

1. **Vercel Dashboard** → ваш проект → **Settings** → **Environment Variables**

2. Добавьте переменные:

| Key | Value | Environments |
|-----|-------|--------------|
| `VITE_API_URL` | `https://api.itadiscrm.com.kg` | Production, Preview, Development |
| `VITE_APP_NAME` | `ITAdis CRM` | All |
| `VITE_APP_VERSION` | `1.0.0` | All |

3. Нажмите **Save**

### 4.2 Redeploy после изменений

После добавления переменных:
1. **Deployments** → последний деплой → **⋮** (меню) → **Redeploy**
2. Или просто сделайте новый push в GitHub (автоматический редеплой)

---

## 5. Подключение домена

### 5.1 Добавление домена в Vercel

1. **Vercel Dashboard** → ваш проект → **Settings** → **Domains**
2. Нажмите **Add**
3. Введите домены:
   - `itadiscrm.com.kg`
   - `www.itadiscrm.com.kg`
4. Нажмите **Add**

### 5.2 Настройка DNS в Cloudflare

Vercel покажет, какие DNS записи нужно добавить.

**Вариант 1: CNAME (рекомендуется)**

В Cloudflare Dashboard → DNS → Records:

| Type  | Name | Target                              | Proxy Status |
|-------|------|-------------------------------------|--------------|
| CNAME | www  | cname.vercel-dns.com                | DNS only (⚪) |

**Важно:** Для работы CNAME с Vercel отключите Cloudflare Proxy (серое облачко)!

**Вариант 2: A Records**

Если нужны A записи, Vercel покажет IP адреса:

| Type | Name | Content      | Proxy Status |
|------|------|--------------|--------------|
| A    | @    | 76.76.21.21  | DNS only (⚪) |
| A    | www  | 76.76.21.21  | DNS only (⚪) |

(IP могут отличаться, смотрите в Vercel)

### 5.3 Настройка корневого домена (@)

Для корневого домена (`itadiscrm.com.kg` без www):

**Cloudflare CNAME Flattening:**

1. Cloudflare поддерживает CNAME на корневом домене
2. Добавьте в Cloudflare:

| Type  | Name | Target                | Proxy Status |
|-------|------|-----------------------|--------------|
| CNAME | @    | cname.vercel-dns.com  | DNS only (⚪) |

**Или используйте A Records** (см. Vercel Dashboard для IP)

### 5.4 Проверка домена

После настройки DNS (~10-30 минут):
1. Vercel автоматически проверит DNS
2. Получит SSL сертификат (Let's Encrypt)
3. Статус изменится на **Valid** ✅

---

## 6. Финальная проверка

### 6.1 Тестирование доменов

Откройте в браузере:
- ✅ https://itadiscrm.com.kg
- ✅ https://www.itadiscrm.com.kg

### 6.2 Проверка API подключения

1. Откройте DevTools (F12) → Console
2. Проверьте, что запросы идут к `https://api.itadiscrm.com.kg`
3. Попробуйте логин

### 6.3 Проверка SSL

Должен быть автоматический SSL от Vercel:
```bash
curl -I https://itadiscrm.com.kg
```

Ответ должен содержать:
```
HTTP/2 200
server: Vercel
...
```

### 6.4 Тестирование функционала

- [ ] Логин работает
- [ ] API запросы успешны
- [ ] Данные загружаются
- [ ] Статические файлы загружаются

---

## 🔄 Автоматический деплой (CI/CD)

### Vercel автоматически деплоит при:

1. **Push в main/master** → Production деплой на ваш домен
2. **Push в другие ветки** → Preview деплой с уникальной ссылкой
3. **Pull Request** → Preview деплой + комментарий в PR

### Настройка Git Integration

**Vercel Dashboard** → ваш проект → **Settings** → **Git**

- **Production Branch**: `main` (или `master`)
- **Auto-deploy branches**: All branches (для preview)
- **Ignored Build Step**: можно настроить условия деплоя

---

## 📊 Мониторинг

### Analytics

**Vercel Dashboard** → ваш проект → **Analytics**

Vercel предоставляет:
- Количество посещений
- Производительность (Core Web Vitals)
- География пользователей
- Самые популярные страницы

### Logs

**Vercel Dashboard** → ваш проект → **Deployments** → выберите деплой → **Function Logs**

---

## 🐛 Troubleshooting

### Проблема: API запросы не работают (CORS)

**Решение:**

1. Проверьте backend `settings.py`:
   ```python
   CORS_ALLOWED_ORIGINS = [
       "https://itadiscrm.com.kg",
       "https://www.itadiscrm.com.kg",
       "https://itadis-crm-frontend.vercel.app",  # Добавьте Vercel домен
   ]
   ```

2. Или разрешите все домены (не рекомендуется для production):
   ```python
   CORS_ALLOW_ALL_ORIGINS = True
   ```

3. Перезапустите backend:
   ```bash
   sudo systemctl restart itadis-crm
   ```

### Проблема: Environment Variables не работают

**Решение:**

1. Проверьте, что переменные добавлены для **Production**
2. Redeploy проекта
3. Очистите кеш браузера (Ctrl+Shift+R)

### Проблема: Домен не подключается

**Решение:**

1. Проверьте DNS:
   ```bash
   nslookup itadiscrm.com.kg
   ```

2. Убедитесь, что Cloudflare Proxy **отключен** (серое облачко)
3. Подождите 10-30 минут для распространения DNS
4. В Vercel проверьте статус домена (должен быть Valid)

### Проблема: Build Failed

**Решение:**

1. Проверьте логи деплоя в Vercel
2. Убедитесь, что локально `npm run build` работает
3. Проверьте версии Node.js:
   - В `package.json` добавьте:
     ```json
     "engines": {
       "node": "18.x"
     }
     ```

---

## 🎯 Оптимизация

### 1. Настройка кеширования

**`vercel.json`** (создайте в корне frontend проекта):

```json
{
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    },
    {
      "source": "/(.*).js",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    },
    {
      "source": "/(.*).css",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

### 2. Redirects

Для редиректа с www на без www (или наоборот):

```json
{
  "redirects": [
    {
      "source": "/:path*",
      "has": [
        {
          "type": "host",
          "value": "www.itadiscrm.com.kg"
        }
      ],
      "destination": "https://itadiscrm.com.kg/:path*",
      "permanent": true
    }
  ]
}
```

### 3. Image Optimization

Vercel автоматически оптимизирует изображения через:
```jsx
import Image from 'next/image';  // Для Next.js

<Image 
  src="/logo.png" 
  alt="Logo" 
  width={200} 
  height={100}
/>
```

---

## 📝 Полезные ссылки

- **Vercel Documentation**: https://vercel.com/docs
- **Vercel CLI**: https://vercel.com/docs/cli
- **Next.js on Vercel**: https://vercel.com/docs/frameworks/nextjs
- **Vite on Vercel**: https://vercel.com/docs/frameworks/vite

---

## 🎉 Итог

✅ Frontend задеплоен на Vercel  
✅ Домен подключен  
✅ SSL настроен автоматически  
✅ API подключено к backend на AWS  
✅ Автоматический деплой через Git  

**Проект доступен глобально!** 🚀

- Frontend: https://itadiscrm.com.kg
- Backend API: https://api.itadiscrm.com.kg
- Admin: https://api.itadiscrm.com.kg/admin/
- Swagger: https://api.itadiscrm.com.kg/api/schema/swagger-ui/

---

**Следующие шаги:**
1. ✅ Backend на AWS - **ГОТОВО!**
2. ✅ Frontend на Vercel - **ГОТОВО!**
3. ⏭️ Настройка CI/CD (GitHub Actions)
4. ⏭️ Мониторинг и аналитика
5. ⏭️ Backup и восстановление
