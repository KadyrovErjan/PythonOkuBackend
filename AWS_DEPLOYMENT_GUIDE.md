# 🚀 AWS Deployment Guide для ITAdis CRM Backend

## 📋 Содержание
1. [Подготовка AWS окружения](#1-подготовка-aws-окружения)
2. [Настройка базы данных RDS (PostgreSQL)](#2-настройка-базы-данных-rds)
3. [Настройка EC2 инстанса](#3-настройка-ec2-инстанса)
4. [Деплой приложения](#4-деплой-приложения)
5. [Настройка Nginx](#5-настройка-nginx)
6. [Настройка SSL (Let's Encrypt)](#6-настройка-ssl)
7. [Настройка DNS (Cloudflare)](#7-настройка-dns)
8. [Финальная проверка](#8-финальная-проверка)

---

## 1. Подготовка AWS окружения

### 1.1 Создание AWS аккаунта
- Перейдите на https://aws.amazon.com/
- Создайте аккаунт или войдите в существующий

### 1.2 Регион AWS
Выберите регион ближе к Кыргызстану:
- `ap-south-1` (Mumbai, India) - рекомендуется
- `eu-central-1` (Frankfurt, Germany) - альтернатива

---

## 2. Настройка базы данных RDS (PostgreSQL)

### 2.1 Создание RDS инстанса
1. Откройте AWS Console → RDS
2. Нажмите "Create database"
3. Выберите:
   - **Engine**: PostgreSQL 15
   - **Template**: Free tier (для начала) или Production
   - **DB instance identifier**: `itadis-crm-db`
   - **Master username**: `itadis_admin`
   - **Master password**: (создайте надежный пароль, сохраните!)
   - **DB instance class**: `db.t3.micro` (Free tier) или `db.t3.small`
   - **Storage**: 20 GB SSD
   - **Public access**: No (безопаснее)
   - **VPC security group**: Создайте новую "itadis-db-sg"

### 2.2 Настройка Security Group для RDS
1. После создания RDS → Security Groups
2. Найдите "itadis-db-sg"
3. Inbound rules → Edit:
   - **Type**: PostgreSQL
   - **Protocol**: TCP
   - **Port**: 5432
   - **Source**: Custom (позже добавим Security Group EC2)

### 2.3 Сохраните данные подключения
```
DB_HOST=itadis-crm-db.xxxxxxxxxx.ap-south-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=postgres (создадим нашу БД позже)
DB_USER=itadis_admin
DB_PASSWORD=ваш_пароль
```

---

## 3. Настройка EC2 инстанса

### 3.1 Создание EC2 инстанса
1. AWS Console → EC2 → Launch Instance
2. Настройки:
   - **Name**: `itadis-crm-backend`
   - **AMI**: Ubuntu 22.04 LTS
   - **Instance type**: `t2.micro` (Free tier) или `t2.small`
   - **Key pair**: Создайте новую пару ключей `itadis-crm-key` и скачайте `.pem` файл
   - **Network settings**:
     - VPC: Default VPC
     - Auto-assign public IP: Enable
     - Security group: Создайте "itadis-web-sg"

### 3.2 Настройка Security Group для EC2 (itadis-web-sg)
Inbound rules:
- **SSH**: Port 22, Source: My IP (ваш IP)
- **HTTP**: Port 80, Source: 0.0.0.0/0
- **HTTPS**: Port 443, Source: 0.0.0.0/0
- **Custom TCP**: Port 8000, Source: 0.0.0.0/0 (временно для тестирования)

### 3.3 Свяжите RDS и EC2 Security Groups
1. Вернитесь к RDS Security Group (itadis-db-sg)
2. Edit Inbound rules:
   - **Type**: PostgreSQL
   - **Port**: 5432
   - **Source**: Security Group → выберите `itadis-web-sg` (EC2 security group)

### 3.4 Elastic IP (статический IP)
1. EC2 → Elastic IPs → Allocate Elastic IP address
2. Associate с вашим EC2 инстансом `itadis-crm-backend`
3. **Сохраните этот IP** - он понадобится для DNS!

---

## 4. Деплой приложения

### 4.1 Подключение к EC2
```bash
# Windows (PowerShell)
ssh -i "C:\путь\к\itadis-crm-key.pem" ubuntu@ваш-elastic-ip

# Или используйте PuTTY с конвертированным .ppk ключом
```

### 4.2 Установка необходимого ПО на EC2

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python 3.12
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev

# Установка PostgreSQL client
sudo apt install -y postgresql-client

# Установка Nginx
sudo apt install -y nginx

# Установка Certbot для SSL
sudo apt install -y certbot python3-certbot-nginx

# Установка Git
sudo apt install -y git

# Установка дополнительных пакетов
sudo apt install -y gcc build-essential libpq-dev curl
```

### 4.3 Создание пользователя для приложения

```bash
# Создание пользователя
sudo useradd -m -s /bin/bash itadis
sudo passwd itadis  # Установите пароль

# Добавление в sudo группу (опционально)
sudo usermod -aG sudo itadis

# Переключение на пользователя
sudo su - itadis
```

### 4.4 Клонирование репозитория

```bash
# Создание директории для проекта
mkdir -p /home/itadis/apps
cd /home/itadis/apps

# Клонирование репозитория
git clone https://github.com/ваш-username/ITAdisCRMBackend.git
cd ITAdisCRMBackend/backend
```

### 4.5 Создание виртуального окружения

```bash
# Создание venv
python3.12 -m venv venv

# Активация
source venv/bin/activate

# Обновление pip
pip install --upgrade pip

# Установка зависимостей
pip install -r requirements.txt

# Установка gunicorn
pip install gunicorn
```

### 4.6 Настройка .env файла

```bash
# Создание production .env
nano .env.production
```

Содержимое `.env.production`:
```env
# Django Settings
SECRET_KEY=сгенерируйте_новый_секретный_ключ_здесь
DEBUG=False
ALLOWED_HOSTS=itadiscrm.com.kg,www.itadiscrm.com.kg,api.itadiscrm.com.kg,ваш-elastic-ip

# Database Configuration (PostgreSQL RDS)
DB_NAME=itadis_db
DB_USER=itadis_admin
DB_PASSWORD=ваш_пароль_от_rds
DB_HOST=itadis-crm-db.xxxxxxxxxx.ap-south-1.rds.amazonaws.com
DB_PORT=5432

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://itadiscrm.com.kg,https://www.itadiscrm.com.kg

# Redis (если используете)
REDIS_URL=redis://localhost:6379/0
```

**Генерация SECRET_KEY:**
```bash
python3.12 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4.7 Подготовка базы данных

```bash
# Подключение к RDS и создание БД
psql -h itadis-crm-db.xxxxxxxxxx.ap-south-1.rds.amazonaws.com -U itadis_admin -d postgres

# В psql консоли:
CREATE DATABASE itadis_db;
CREATE USER itadis_user WITH PASSWORD 'ваш_пароль';
GRANT ALL PRIVILEGES ON DATABASE itadis_db TO itadis_user;
\q
```

### 4.8 Миграции и статические файлы

```bash
# Активируйте venv если не активен
source venv/bin/activate

# Экспорт переменных из .env.production
export $(cat .env.production | xargs)

# Миграции
python manage.py migrate

# Сбор статики
python manage.py collectstatic --noinput

# Создание суперпользователя
python manage.py createsuperuser

# Инициализация owner (если есть)
python manage.py init_owner
```

### 4.9 Тестовый запуск

```bash
# Запуск с gunicorn
gunicorn mysite.wsgi:application --bind 0.0.0.0:8000 --workers 4

# Проверка в браузере:
# http://ваш-elastic-ip:8000/admin/
```

Если все работает, нажмите `Ctrl+C` и переходите к следующему шагу.

---

## 5. Настройка Nginx

### 5.1 Создание systemd сервиса для Gunicorn

```bash
# Выйдите из пользователя itadis
exit

# Создайте systemd unit файл
sudo nano /etc/systemd/system/itadis-crm.service
```

Содержимое файла:
```ini
[Unit]
Description=ITAdis CRM Gunicorn Daemon
After=network.target

[Service]
User=itadis
Group=itadis
WorkingDirectory=/home/itadis/apps/ITAdisCRMBackend/backend
EnvironmentFile=/home/itadis/apps/ITAdisCRMBackend/backend/.env.production
ExecStart=/home/itadis/apps/ITAdisCRMBackend/backend/venv/bin/gunicorn \
          --workers 4 \
          --bind unix:/home/itadis/apps/ITAdisCRMBackend/backend/itadis.sock \
          --timeout 120 \
          --access-logfile /home/itadis/apps/ITAdisCRMBackend/backend/logs/gunicorn-access.log \
          --error-logfile /home/itadis/apps/ITAdisCRMBackend/backend/logs/gunicorn-error.log \
          mysite.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Запуск сервиса
sudo systemctl start itadis-crm
sudo systemctl enable itadis-crm
sudo systemctl status itadis-crm
```

### 5.2 Настройка Nginx

```bash
# Создание конфигурации Nginx
sudo nano /etc/nginx/sites-available/itadiscrm
```

Содержимое файла:
```nginx
upstream itadis_app {
    server unix:/home/itadis/apps/ITAdisCRMBackend/backend/itadis.sock fail_timeout=0;
}

server {
    listen 80;
    server_name itadiscrm.com.kg www.itadiscrm.com.kg api.itadiscrm.com.kg;
    
    client_max_body_size 10M;
    
    # Логи
    access_log /var/log/nginx/itadiscrm-access.log;
    error_log /var/log/nginx/itadiscrm-error.log;
    
    # Статические файлы
    location /static/ {
        alias /home/itadis/apps/ITAdisCRMBackend/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Медиа файлы
    location /media/ {
        alias /home/itadis/apps/ITAdisCRMBackend/backend/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # Проксирование к Django
    location / {
        proxy_pass http://itadis_app;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        proxy_redirect off;
        proxy_buffering off;
        
        # Таймауты
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

```bash
# Активация конфигурации
sudo ln -s /etc/nginx/sites-available/itadiscrm /etc/nginx/sites-enabled/

# Удаление дефолтной конфигурации
sudo rm /etc/nginx/sites-enabled/default

# Проверка конфигурации
sudo nginx -t

# Перезапуск Nginx
sudo systemctl restart nginx
```

### 5.3 Настройка прав доступа

```bash
# Права для socket файла
sudo usermod -aG itadis www-data

# Права для статических и медиа файлов
sudo chmod 755 /home/itadis/apps/ITAdisCRMBackend/backend/staticfiles
sudo chmod 755 /home/itadis/apps/ITAdisCRMBackend/backend/media
```

---

## 6. Настройка SSL (Let's Encrypt)

### 6.1 Получение SSL сертификата

**⚠️ ВАЖНО**: Перед этим шагом убедитесь, что DNS настроен (см. шаг 7)!

```bash
# Получение сертификата для всех доменов
sudo certbot --nginx -d itadiscrm.com.kg -d www.itadiscrm.com.kg -d api.itadiscrm.com.kg

# Следуйте инструкциям:
# 1. Введите email для уведомлений
# 2. Согласитесь с Terms of Service
# 3. Выберите "2" для redirect HTTP -> HTTPS
```

### 6.2 Проверка автообновления сертификата

```bash
# Тест автообновления
sudo certbot renew --dry-run

# Certbot автоматически создаст cron job для обновления
```

---

## 7. Настройка DNS (Cloudflare)

### 7.1 Добавление домена в Cloudflare
1. Войдите в Cloudflare: https://dash.cloudflare.com/
2. Add a Site → введите `itadiscrm.com.kg`
3. Выберите план (Free)
4. Cloudflare покажет nameservers

### 7.2 Изменение NS записей у регистратора
1. Войдите в панель регистратора домена (где купили itadiscrm.com.kg)
2. Найдите раздел "DNS" или "Nameservers"
3. Замените NS записи на те, что дал Cloudflare:
   ```
   NS1: christian.ns.cloudflare.com
   NS2: ulla.ns.cloudflare.com
   ```
   (Ваши NS серверы могут отличаться!)
4. Сохраните изменения

⏰ **Ожидание**: DNS изменения могут занять от 1 часа до 24 часов

### 7.3 Настройка DNS записей в Cloudflare

После того как домен активируется в Cloudflare:

1. Cloudflare Dashboard → вашдомен → DNS → Records
2. Добавьте следующие записи:

| Type  | Name | Content                | Proxy Status | TTL  |
|-------|------|------------------------|--------------|------|
| A     | @    | ваш-elastic-ip         | Proxied (🧡) | Auto |
| A     | www  | ваш-elastic-ip         | Proxied (🧡) | Auto |
| A     | api  | ваш-elastic-ip         | Proxied (🧡) | Auto |

**Пример:**
- Type: `A`
- Name: `@`
- IPv4 address: `13.127.45.123` (ваш Elastic IP)
- Proxy status: Proxied (оранжевое облачко)
- TTL: Auto

### 7.4 Настройка SSL/TLS в Cloudflare
1. Cloudflare Dashboard → SSL/TLS
2. Выберите режим: **Full (strict)**
3. Edge Certificates → Always Use HTTPS: **On**
4. Automatic HTTPS Rewrites: **On**

### 7.5 Дополнительные настройки Cloudflare (опционально)

#### Page Rules для оптимизации
1. Rules → Page Rules → Create Page Rule

**Правило для статических файлов:**
- URL: `*itadiscrm.com.kg/static/*`
- Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month
  - Browser Cache TTL: 1 month

**Правило для медиа файлов:**
- URL: `*itadiscrm.com.kg/media/*`
- Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 week

---

## 8. Финальная проверка

### 8.1 Проверка работоспособности

```bash
# Проверка статуса сервисов
sudo systemctl status itadis-crm
sudo systemctl status nginx

# Проверка логов
tail -f /home/itadis/apps/ITAdisCRMBackend/backend/logs/django.log
tail -f /home/itadis/apps/ITAdisCRMBackend/backend/logs/gunicorn-error.log
sudo tail -f /var/log/nginx/itadiscrm-error.log
```

### 8.2 Тестирование в браузере

1. **Admin panel**: https://itadiscrm.com.kg/admin/
2. **API**: https://api.itadiscrm.com.kg/api/v1/
3. **Swagger**: https://api.itadiscrm.com.kg/api/schema/swagger-ui/

### 8.3 Проверка SSL

```bash
# Через curl
curl -I https://itadiscrm.com.kg

# Или проверка на сайте
# https://www.ssllabs.com/ssltest/
```

### 8.4 Тестирование API

```bash
# Тест доступности
curl https://api.itadiscrm.com.kg/api/v1/

# Тест авторизации
curl -X POST https://api.itadiscrm.com.kg/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "ваш_пароль"}'
```

---

## 🔄 Обновление приложения (CI/CD)

### Ручное обновление

```bash
# Подключение к серверу
ssh -i itadis-crm-key.pem ubuntu@ваш-elastic-ip

# Переключение на пользователя itadis
sudo su - itadis

# Переход в директорию проекта
cd /home/itadis/apps/ITAdisCRMBackend/backend

# Активация venv
source venv/bin/activate

# Получение изменений
git pull origin main

# Установка новых зависимостей (если есть)
pip install -r requirements.txt

# Миграции
python manage.py migrate

# Сбор статики
python manage.py collectstatic --noinput

# Перезапуск приложения
exit  # выход из пользователя itadis
sudo systemctl restart itadis-crm

# Проверка статуса
sudo systemctl status itadis-crm
```

---

## 🛠️ Troubleshooting

### Проблема: Сервис не запускается

```bash
# Проверка логов systemd
sudo journalctl -u itadis-crm -n 50

# Проверка логов gunicorn
tail -100 /home/itadis/apps/ITAdisCRMBackend/backend/logs/gunicorn-error.log

# Проверка прав на socket
ls -la /home/itadis/apps/ITAdisCRMBackend/backend/itadis.sock
```

### Проблема: 502 Bad Gateway

```bash
# Проверка работы gunicorn
sudo systemctl status itadis-crm

# Проверка socket файла
ls -la /home/itadis/apps/ITAdisCRMBackend/backend/itadis.sock

# Проверка Nginx error log
sudo tail -50 /var/log/nginx/itadiscrm-error.log

# Перезапуск сервисов
sudo systemctl restart itadis-crm
sudo systemctl restart nginx
```

### Проблема: Статические файлы не загружаются

```bash
# Проверка прав доступа
ls -la /home/itadis/apps/ITAdisCRMBackend/backend/staticfiles/

# Повторный сбор статики
sudo su - itadis
cd /home/itadis/apps/ITAdisCRMBackend/backend
source venv/bin/activate
python manage.py collectstatic --noinput --clear
```

### Проблема: Не подключается к базе данных

```bash
# Проверка доступности RDS
telnet itadis-crm-db.xxxxxxxxxx.ap-south-1.rds.amazonaws.com 5432

# Проверка Security Group
# AWS Console → RDS → Security Groups → Inbound rules

# Проверка переменных окружения
cat /home/itadis/apps/ITAdisCRMBackend/backend/.env.production
```

---

## 📊 Мониторинг

### Настройка базового мониторинга

```bash
# Установка htop для мониторинга ресурсов
sudo apt install -y htop

# Мониторинг в реальном времени
htop

# Использование диска
df -h

# Использование памяти
free -h

# Проверка активных соединений
sudo netstat -tuln | grep :80
sudo netstat -tuln | grep :443
```

---

## 🎯 Следующие шаги

1. ✅ Backend развернут на AWS
2. ⏭️ Настройка Frontend на Vercel (следующий документ)
3. ⏭️ Настройка CI/CD (GitHub Actions)
4. ⏭️ Настройка резервного копирования RDS
5. ⏭️ Настройка CloudWatch мониторинга

---

## 📝 Полезные команды

```bash
# Перезапуск всех сервисов
sudo systemctl restart itadis-crm nginx

# Просмотр всех логов
tail -f /home/itadis/apps/ITAdisCRMBackend/backend/logs/*.log

# Проверка использования портов
sudo ss -tulpn | grep LISTEN

# Очистка логов (осторожно!)
sudo truncate -s 0 /var/log/nginx/*.log
```

---

**Удачи с деплоем! 🚀**
