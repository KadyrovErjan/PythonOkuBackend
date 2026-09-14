# 🚀 ITAdis CRM - Production Deployment Guide

> Полное руководство по деплою ITAdis CRM на production

**Домен:** itadiscrm.com.kg  
**Backend:** AWS EC2 + RDS PostgreSQL  
**Frontend:** Vercel  
**DNS:** Cloudflare  

---

## 📚 Документация

Этот репозиторий содержит все необходимые файлы и инструкции для деплоя:

### 📖 Основные гайды

1. **[AWS_DEPLOYMENT_GUIDE.md](./AWS_DEPLOYMENT_GUIDE.md)** 
   - Подробное руководство по деплою backend на AWS
   - Настройка RDS, EC2, Nginx, SSL
   - ~60 страниц с пошаговыми инструкциями

2. **[QUICK_DEPLOY_CHECKLIST.md](./QUICK_DEPLOY_CHECKLIST.md)**
   - Быстрый чеклист для деплоя
   - Все команды в одном месте
   - Время выполнения: ~90 минут

3. **[VERCEL_FRONTEND_GUIDE.md](./VERCEL_FRONTEND_GUIDE.md)**
   - Деплой frontend на Vercel
   - Подключение домена
   - Настройка переменных окружения

### 🛠️ Скрипты для автоматизации

В папке `deploy_scripts/`:

- **`setup_server.sh`** - Автоматическая установка ПО на EC2
- **`deploy_app.sh`** - Деплой Django приложения
- **`update_app.sh`** - Обновление приложения (git pull + restart)
- **`itadis-crm.service`** - Systemd unit файл для Gunicorn
- **`nginx_itadiscrm`** - Конфигурация Nginx

### 📄 Примеры конфигураций

- **`.env.production.example`** - Пример production переменных окружения
- **`docker-compose.yml`** - Docker compose для локальной разработки
- **`Dockerfile`** - Docker образ приложения

---

## 🏗️ Архитектура Production

```
                                   Internet
                                      |
                          ┌───────────┴───────────┐
                          │                       │
                    DNS (Cloudflare)              │
                          │                       │
               ┌──────────┴──────────┐            │
               │                     │            │
         itadiscrm.com.kg    api.itadiscrm.com.kg │
               │                     │            │
               │                     │            │
        ┌──────▼──────┐       ┌──────▼──────┐    │
        │   Vercel    │       │   AWS EC2   │    │
        │  (Frontend) │       │  (Backend)  │    │
        └─────────────┘       └──────┬──────┘    │
                                     │            │
                              ┌──────▼──────┐    │
                              │   AWS RDS   │    │
                              │ (PostgreSQL)│    │
                              └─────────────┘    │
                                                  │
                                           SSL (Let's Encrypt)
```

### Компоненты:

1. **Frontend (Vercel)**
   - Хостинг: Vercel
   - Домены: itadiscrm.com.kg, www.itadiscrm.com.kg
   - SSL: Автоматический (Vercel)
   - CDN: Встроенный Vercel CDN

2. **Backend (AWS EC2)**
   - Сервер: AWS EC2 (Ubuntu 22.04)
   - App Server: Gunicorn + Django
   - Web Server: Nginx
   - Домен: api.itadiscrm.com.kg
   - SSL: Let's Encrypt (Certbot)

3. **Database (AWS RDS)**
   - СУБД: PostgreSQL 15
   - Инстанс: db.t3.micro (или выше)
   - Backup: Автоматические снапшоты AWS
   - Доступ: Приватный (только с EC2)

4. **DNS & CDN (Cloudflare)**
   - DNS: Управление доменом
   - SSL/TLS: Full (strict) mode
   - Cache: Для статических файлов
   - DDoS protection: Встроенная защита

---

## ⚡ Быстрый старт

### Шаг 1: AWS Backend (~60 минут)

```bash
# 1. Создайте RDS PostgreSQL
# AWS Console → RDS → Create database

# 2. Создайте EC2 instance
# AWS Console → EC2 → Launch instance

# 3. Подключитесь к EC2
ssh -i "itadis-crm-key.pem" ubuntu@ваш-elastic-ip

# 4. Установите ПО (автоматически)
wget https://raw.githubusercontent.com/ваш-username/ITAdisCRMBackend/main/deploy_scripts/setup_server.sh
chmod +x setup_server.sh
sudo ./setup_server.sh

# 5. Клонируйте репозиторий
sudo su - itadis
mkdir -p ~/apps && cd ~/apps
git clone https://github.com/ваш-username/ITAdisCRMBackend.git
cd ITAdisCRMBackend/backend

# 6. Настройте .env
cp .env.production.example .env.production
nano .env.production  # Заполните данные

# 7. Запустите деплой
cd /home/itadis/apps/ITAdisCRMBackend
chmod +x deploy_scripts/*.sh
./deploy_scripts/deploy_app.sh

# 8. Настройте systemd и Nginx
exit  # выход из itadis
sudo cp /home/itadis/apps/ITAdisCRMBackend/deploy_scripts/itadis-crm.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start itadis-crm
sudo systemctl enable itadis-crm

sudo cp /home/itadis/apps/ITAdisCRMBackend/deploy_scripts/nginx_itadiscrm /etc/nginx/sites-available/itadiscrm
sudo ln -s /etc/nginx/sites-available/itadiscrm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 9. Получите SSL сертификат (после настройки DNS)
sudo certbot --nginx -d api.itadiscrm.com.kg
```

### Шаг 2: Cloudflare DNS (~15 минут)

1. Добавьте домен в Cloudflare
2. Измените NS у регистратора домена
3. Добавьте DNS записи:
   - `A @ → ваш-elastic-ip` (Proxied)
   - `A www → ваш-elastic-ip` (Proxied) 
   - `A api → ваш-elastic-ip` (Proxied)
4. SSL/TLS → Full (strict)

### Шаг 3: Vercel Frontend (~15 минут)

1. Зайдите на https://vercel.com/
2. Import Git Repository (ваш frontend репозиторий)
3. Настройте:
   - Framework: Vite / Next.js
   - Build Command: `npm run build`
   - Environment Variables: `VITE_API_URL=https://api.itadiscrm.com.kg`
4. Deploy
5. Settings → Domains → Add: `itadiscrm.com.kg`
6. Настройте DNS в Cloudflare (CNAME → vercel)

---

## 🔐 Безопасность

### Backend (Django)

✅ **Реализовано:**
- JWT аутентификация (access + refresh tokens)
- HTTPS only (SSL/TLS)
- CORS настроен для конкретных доменов
- Rate limiting (100 req/hour для анонимов, 1000/hour для users)
- Secure cookies (CSRF, Session)
- Argon2 password hashing
- SQL injection защита (Django ORM)
- XSS защита (Django templates)

### Инфраструктура

✅ **Реализовано:**
- RDS приватный доступ (только с EC2)
- EC2 Security Groups (только 22, 80, 443 порты)
- Cloudflare DDoS protection
- Let's Encrypt SSL certificates
- Nginx rate limiting

### Рекомендации

⚠️ **TODO:**
- [ ] Настроить AWS CloudWatch мониторинг
- [ ] Включить AWS RDS автоматические бекапы
- [ ] Настроить AWS CloudTrail для аудита
- [ ] Добавить fail2ban для защиты SSH
- [ ] Настроить AWS WAF (Web Application Firewall)

---

## 📊 Мониторинг

### Backend Logs

```bash
# Django application logs
tail -f /home/itadis/apps/ITAdisCRMBackend/backend/logs/django.log

# Gunicorn logs
sudo journalctl -u itadis-crm -f

# Nginx access logs
sudo tail -f /var/log/nginx/itadiscrm-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/itadiscrm-error.log
```

### System Monitoring

```bash
# CPU и память
htop

# Диск
df -h

# Активные соединения
sudo ss -tulpn | grep LISTEN

# Статус сервисов
sudo systemctl status itadis-crm nginx
```

### Vercel Analytics

- Vercel Dashboard → ваш проект → Analytics
- Core Web Vitals
- География пользователей
- Популярные страницы

---

## 🔄 Обновление приложения

### Backend (AWS)

```bash
# Подключиться к серверу
ssh -i itadis-crm-key.pem ubuntu@ваш-elastic-ip

# Запустить update скрипт
sudo su - itadis
cd /home/itadis/apps/ITAdisCRMBackend
./deploy_scripts/update_app.sh
```

Скрипт автоматически:
1. Получит изменения из git
2. Установит новые зависимости
3. Применит миграции
4. Соберет статику
5. Перезапустит сервис

### Frontend (Vercel)

Vercel автоматически деплоит при:
- Push в main/master → Production
- Push в другие ветки → Preview
- Pull Request → Preview с комментарием

**Ручной деплой:**
```bash
# Установить Vercel CLI
npm i -g vercel

# Деплой
vercel --prod
```

---

## 🐛 Troubleshooting

### Backend не отвечает (502 Bad Gateway)

```bash
# 1. Проверить статус Gunicorn
sudo systemctl status itadis-crm

# 2. Проверить логи
sudo journalctl -u itadis-crm -n 50

# 3. Проверить socket
ls -la /home/itadis/apps/ITAdisCRMBackend/backend/itadis.sock

# 4. Перезапустить сервисы
sudo systemctl restart itadis-crm
sudo systemctl restart nginx
```

### Не подключается к БД

```bash
# 1. Проверить подключение к RDS
telnet itadis-crm-db.xxxxx.rds.amazonaws.com 5432

# 2. Проверить Security Groups в AWS
# RDS SG → Inbound rules → PostgreSQL от EC2 SG

# 3. Проверить .env файл
cat /home/itadis/apps/ITAdisCRMBackend/backend/.env.production
```

### CORS ошибки на Frontend

```bash
# 1. Добавить Vercel домен в backend settings.py
CORS_ALLOWED_ORIGINS = [
    "https://itadiscrm.com.kg",
    "https://www.itadiscrm.com.kg",
    "https://your-app.vercel.app",  # Добавить
]

# 2. Перезапустить backend
sudo systemctl restart itadis-crm
```

### Статические файлы не загружаются

```bash
# 1. Пересобрать статику
sudo su - itadis
cd /home/itadis/apps/ITAdisCRMBackend/backend
source venv/bin/activate
python manage.py collectstatic --noinput --clear

# 2. Проверить права
chmod 755 staticfiles/
chmod 755 media/
```

---

## 📈 Масштабирование

### Вертикальное (больше ресурсов)

**EC2:**
- t2.micro → t2.small → t2.medium
- AWS Console → EC2 → Instance → Actions → Instance Settings → Change Instance Type

**RDS:**
- db.t3.micro → db.t3.small → db.t3.medium
- AWS Console → RDS → Modify

### Горизонтальное (больше серверов)

**Load Balancer:**
1. Создайте Application Load Balancer (ALB)
2. Создайте несколько EC2 инстансов
3. Добавьте в Target Group
4. Настройте Auto Scaling

**Read Replicas для RDS:**
1. AWS Console → RDS → Actions → Create read replica
2. Настройте Django для использования read replica

---

## 💰 Стоимость (примерная)

### AWS (в месяц)

| Сервис | Тип | Стоимость |
|--------|-----|-----------|
| EC2 t2.micro | Free tier / ~$10 | $0-10 |
| RDS db.t3.micro | Free tier / ~$15 | $0-15 |
| Elastic IP | Если не используется | $0-3 |
| Data transfer | ~100 GB | $0-10 |
| **Итого** | | **$0-40** |

### Vercel

| План | Стоимость | Лимиты |
|------|-----------|---------|
| Hobby (Free) | $0 | 100GB bandwidth, 100 build hours |
| Pro | $20/мес | 1TB bandwidth, unlimited builds |

### Cloudflare

| План | Стоимость |
|------|-----------|
| Free | $0 |
| Pro | $20/мес (опционально) |

### Домен

| Регистратор | Стоимость/год |
|-------------|---------------|
| .com.kg | ~1500-3000 сом |

**Итого:** $0-60/месяц для старта

---

## 📞 Поддержка

### Полезные ссылки

- **Django Documentation**: https://docs.djangoproject.com/
- **AWS Documentation**: https://docs.aws.amazon.com/
- **Vercel Documentation**: https://vercel.com/docs
- **Cloudflare Documentation**: https://developers.cloudflare.com/
- **Nginx Documentation**: https://nginx.org/en/docs/

### Команда разработки

- **Backend**: Django + Django REST Framework
- **Frontend**: React / Next.js + Vite
- **Database**: PostgreSQL
- **Hosting**: AWS + Vercel

---

## ✅ Checklist финальной проверки

### Backend
- [ ] API доступен по https://api.itadiscrm.com.kg
- [ ] Admin panel работает
- [ ] Swagger UI доступен
- [ ] База данных подключена
- [ ] Миграции применены
- [ ] Статические файлы загружаются
- [ ] SSL сертификат валиден
- [ ] Логи пишутся корректно

### Frontend
- [ ] Сайт доступен по https://itadiscrm.com.kg
- [ ] Редирект с www работает
- [ ] API запросы успешны
- [ ] Логин работает
- [ ] Все страницы загружаются
- [ ] SSL сертификат валиден

### DNS
- [ ] Домены резолвятся корректно
- [ ] Cloudflare настроен
- [ ] SSL/TLS режим: Full (strict)
- [ ] DNSSEC включен (опционально)

### Безопасность
- [ ] DEBUG=False на production
- [ ] SECRET_KEY уникальный
- [ ] CORS настроен правильно
- [ ] Rate limiting включен
- [ ] RDS приватный доступ
- [ ] SSH доступ ограничен
- [ ] Сложные пароли установлены

---

## 🎉 Поздравляем!

Если все пункты выполнены - **ваш проект успешно развернут на production!** 🚀

### Ваши ссылки:

- 🌐 **Frontend**: https://itadiscrm.com.kg
- 🔌 **API**: https://api.itadiscrm.com.kg/api/v1/
- 🔐 **Admin**: https://api.itadiscrm.com.kg/admin/
- 📚 **Swagger**: https://api.itadiscrm.com.kg/api/schema/swagger-ui/

---

## 📝 Следующие шаги

1. ✅ Backend на AWS - **ГОТОВО!**
2. ✅ Frontend на Vercel - **ГОТОВО!**
3. ⏭️ CI/CD через GitHub Actions
4. ⏭️ Настройка мониторинга (CloudWatch, Sentry)
5. ⏭️ Автоматические бекапы
6. ⏭️ Тестирование нагрузки
7. ⏭️ Документация API

**Удачи в развитии проекта! 🚀**
