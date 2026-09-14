# 🛠️ Полезные команды для ITAdis CRM Production

## 📂 Содержание
- [AWS EC2 - Backend](#aws-ec2---backend)
- [Database - PostgreSQL](#database---postgresql)
- [Nginx](#nginx)
- [SSL/Certbot](#sslcertbot)
- [System Monitoring](#system-monitoring)
- [Git Commands](#git-commands)
- [Vercel CLI](#vercel-cli)
- [DNS/Cloudflare](#dnscloudflare)

---

## AWS EC2 - Backend

### Подключение к серверу

```bash
# SSH подключение
ssh -i "itadis-crm-key.pem" ubuntu@ваш-elastic-ip

# Если ошибка прав доступа на ключ (Windows)
icacls itadis-crm-key.pem /inheritance:r
icacls itadis-crm-key.pem /grant:r "%username%:R"

# Переключение на пользователя itadis
sudo su - itadis
```

### Django Management Commands

```bash
# Активация виртуального окружения
cd /home/itadis/apps/ITAdisCRMBackend/backend
source venv/bin/activate

# Экспорт переменных окружения
export $(cat .env.production | xargs)

# Миграции
python manage.py migrate
python manage.py makemigrations
python manage.py showmigrations

# Статические файлы
python manage.py collectstatic --noinput
python manage.py collectstatic --noinput --clear  # С очисткой

# Создание суперпользователя
python manage.py createsuperuser

# Инициализация owner
python manage.py init_owner

# Сброс данных (ОСТОРОЖНО!)
python manage.py reset_data

# Проверка проекта
python manage.py check
python manage.py check --database default

# Django shell
python manage.py shell

# Генерация SECRET_KEY
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Gunicorn Service

```bash
# Статус сервиса
sudo systemctl status itadis-crm

# Запуск
sudo systemctl start itadis-crm

# Остановка
sudo systemctl stop itadis-crm

# Перезапуск
sudo systemctl restart itadis-crm

# Включить автозапуск
sudo systemctl enable itadis-crm

# Отключить автозапуск
sudo systemctl disable itadis-crm

# Просмотр логов
sudo journalctl -u itadis-crm -n 50              # Последние 50 строк
sudo journalctl -u itadis-crm -f                 # Live logs
sudo journalctl -u itadis-crm --since today      # За сегодня
sudo journalctl -u itadis-crm --since "1 hour ago"  # За последний час

# Reload systemd после изменения .service файла
sudo systemctl daemon-reload
```

### Application Logs

```bash
# Django logs
tail -f /home/itadis/apps/ITAdisCRMBackend/backend/logs/django.log
tail -n 100 /home/itadis/apps/ITAdisCRMBackend/backend/logs/django.log

# Gunicorn access logs
tail -f /home/itadis/apps/ITAdisCRMBackend/backend/logs/gunicorn-access.log

# Gunicorn error logs
tail -f /home/itadis/apps/ITAdisCRMBackend/backend/logs/gunicorn-error.log

# Очистка логов (ОСТОРОЖНО!)
sudo truncate -s 0 /home/itadis/apps/ITAdisCRMBackend/backend/logs/*.log
```

### Deployment & Updates

```bash
# Обновление из Git
cd /home/itadis/apps/ITAdisCRMBackend
git pull origin main

# Полное обновление (автоматический скрипт)
sudo su - itadis
cd /home/itadis/apps/ITAdisCRMBackend
./deploy_scripts/update_app.sh

# Ручное обновление
cd /home/itadis/apps/ITAdisCRMBackend/backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
exit
sudo systemctl restart itadis-crm
```

---

## Database - PostgreSQL

### Подключение к RDS

```bash
# Подключение через psql
psql -h itadis-crm-db.xxxxxxxxxx.ap-south-1.rds.amazonaws.com -U itadis_admin -d itadis_db

# Подключение с паролем из переменной
PGPASSWORD=ваш_пароль psql -h itadis-crm-db.xxxxx.rds.amazonaws.com -U itadis_admin -d itadis_db
```

### Полезные SQL команды

```sql
-- Список всех таблиц
\dt

-- Описание таблицы
\d+ itadis_app_user

-- Список баз данных
\l

-- Подключение к другой БД
\c другая_база

-- Список пользователей
\du

-- Выход
\q

-- Размер базы данных
SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database;

-- Размер всех таблиц
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Количество записей в таблицах
SELECT schemaname,tablename,n_live_tup 
FROM pg_stat_user_tables 
ORDER BY n_live_tup DESC;

-- Активные соединения
SELECT * FROM pg_stat_activity;

-- Убить зависшие соединения (ОСТОРОЖНО!)
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'itadis_db' AND pid <> pg_backend_pid();
```

### Backup & Restore

```bash
# Создание backup
pg_dump -h itadis-crm-db.xxxxx.rds.amazonaws.com -U itadis_admin -d itadis_db > backup_$(date +%Y%m%d).sql

# Создание backup только схемы
pg_dump -h itadis-crm-db.xxxxx.rds.amazonaws.com -U itadis_admin -d itadis_db --schema-only > schema.sql

# Создание backup только данных
pg_dump -h itadis-crm-db.xxxxx.rds.amazonaws.com -U itadis_admin -d itadis_db --data-only > data.sql

# Восстановление из backup
psql -h itadis-crm-db.xxxxx.rds.amazonaws.com -U itadis_admin -d itadis_db < backup.sql

# Backup с сжатием
pg_dump -h itadis-crm-db.xxxxx.rds.amazonaws.com -U itadis_admin -d itadis_db | gzip > backup_$(date +%Y%m%d).sql.gz

# Восстановление из сжатого backup
gunzip -c backup.sql.gz | psql -h itadis-crm-db.xxxxx.rds.amazonaws.com -U itadis_admin -d itadis_db
```

---

## Nginx

### Основные команды

```bash
# Проверка конфигурации
sudo nginx -t

# Перезапуск
sudo systemctl restart nginx

# Перезагрузка конфигурации (без остановки)
sudo systemctl reload nginx

# Статус
sudo systemctl status nginx

# Остановка
sudo systemctl stop nginx

# Запуск
sudo systemctl start nginx
```

### Логи

```bash
# Access logs
sudo tail -f /var/log/nginx/itadiscrm-access.log
sudo tail -n 100 /var/log/nginx/itadiscrm-access.log

# Error logs
sudo tail -f /var/log/nginx/itadiscrm-error.log

# Все Nginx логи
sudo tail -f /var/log/nginx/*.log

# Очистка логов (ОСТОРОЖНО!)
sudo truncate -s 0 /var/log/nginx/*.log

# Ротация логов
sudo logrotate -f /etc/logrotate.d/nginx
```

### Конфигурация

```bash
# Редактирование конфигурации
sudo nano /etc/nginx/sites-available/itadiscrm

# Проверка синтаксиса
sudo nginx -t

# Просмотр активных сайтов
ls -la /etc/nginx/sites-enabled/

# Отключение сайта
sudo rm /etc/nginx/sites-enabled/itadiscrm

# Включение сайта
sudo ln -s /etc/nginx/sites-available/itadiscrm /etc/nginx/sites-enabled/

# Проверка версии
nginx -v

# Проверка compiled модулей
nginx -V
```

---

## SSL/Certbot

### Получение сертификата

```bash
# Получить новый сертификат
sudo certbot --nginx -d api.itadiscrm.com.kg

# Получить для нескольких доменов
sudo certbot --nginx -d itadiscrm.com.kg -d www.itadiscrm.com.kg -d api.itadiscrm.com.kg

# Только получить сертификат без настройки Nginx
sudo certbot certonly --nginx -d api.itadiscrm.com.kg

# Интерактивное получение
sudo certbot --nginx
```

### Управление сертификатами

```bash
# Список всех сертификатов
sudo certbot certificates

# Обновление сертификатов
sudo certbot renew

# Тест обновления (dry run)
sudo certbot renew --dry-run

# Принудительное обновление
sudo certbot renew --force-renewal

# Удаление сертификата
sudo certbot delete --cert-name itadiscrm.com.kg

# Отзыв сертификата
sudo certbot revoke --cert-path /etc/letsencrypt/live/itadiscrm.com.kg/cert.pem
```

### Проверка SSL

```bash
# Проверка сертификата через curl
curl -vI https://api.itadiscrm.com.kg

# Проверка срока действия
echo | openssl s_client -servername api.itadiscrm.com.kg -connect api.itadiscrm.com.kg:443 2>/dev/null | openssl x509 -noout -dates

# Детальная информация о сертификате
echo | openssl s_client -servername api.itadiscrm.com.kg -connect api.itadiscrm.com.kg:443 2>/dev/null | openssl x509 -noout -text
```

---

## System Monitoring

### CPU и Memory

```bash
# Интерактивный мониторинг
htop

# Использование CPU
top -bn1 | head -5

# Использование памяти
free -h

# Детальная информация о памяти
cat /proc/meminfo

# Использование swap
swapon --show
```

### Disk

```bash
# Использование дисков
df -h

# Использование по директориям
du -sh /home/itadis/apps/*
du -sh /var/log/*

# Топ 10 самых больших файлов
sudo du -a / | sort -n -r | head -n 10

# Топ 10 больших директорий
sudo du -h / | sort -rh | head -10

# Inodes
df -i
```

### Network

```bash
# Активные соединения
sudo ss -tulpn

# Только HTTP/HTTPS
sudo ss -tulpn | grep -E ':(80|443)'

# Количество соединений по портам
sudo netstat -an | grep ESTABLISHED | awk '{print $4}' | cut -d: -f2 | sort | uniq -c | sort -rn

# Проверка открытых портов
sudo lsof -i -P -n | grep LISTEN

# Тест подключения
curl -I https://api.itadiscrm.com.kg
telnet api.itadiscrm.com.kg 443
```

### Processes

```bash
# Все процессы Python
ps aux | grep python

# Все процессы gunicorn
ps aux | grep gunicorn

# Убить процесс по PID
sudo kill -9 <PID>

# Убить все процессы gunicorn (ОСТОРОЖНО!)
sudo pkill -9 gunicorn

# Количество запущенных процессов
ps aux | wc -l
```

### System Info

```bash
# Версия ОС
lsb_release -a
cat /etc/os-release

# Uptime
uptime

# Дата и время
date
timedatectl

# Пользователи в системе
who
w

# История команд
history

# Системные логи
sudo journalctl -n 50
sudo journalctl -f
```

---

## Git Commands

### Основные команды

```bash
# Клонирование
git clone https://github.com/username/ITAdisCRMBackend.git

# Статус
git status

# Получение изменений
git fetch origin
git pull origin main

# Коммит и push
git add .
git commit -m "Your message"
git push origin main

# Создание новой ветки
git checkout -b feature/new-feature

# Переключение веток
git checkout main

# История коммитов
git log --oneline
git log --graph --oneline --all

# Откат изменений (ОСТОРОЖНО!)
git reset --hard HEAD
git reset --hard origin/main

# Откат конкретного файла
git checkout -- filename

# Просмотр изменений
git diff
git diff filename
```

### GitHub SSH

```bash
# Генерация SSH ключа
ssh-keygen -t ed25519 -C "your_email@example.com"

# Копирование публичного ключа
cat ~/.ssh/id_ed25519.pub

# Тест подключения к GitHub
ssh -T git@github.com

# Изменение remote на SSH
git remote set-url origin git@github.com:username/ITAdisCRMBackend.git

# Просмотр remote
git remote -v
```

---

## Vercel CLI

### Установка

```bash
# Установка Vercel CLI
npm i -g vercel

# Логин
vercel login

# Версия
vercel --version
```

### Деплой

```bash
# Инициализация проекта
vercel

# Production деплой
vercel --prod

# Preview деплой
vercel

# Просмотр логов
vercel logs

# Список деплоев
vercel ls

# Информация о проекте
vercel inspect
```

### Environment Variables

```bash
# Добавить переменную окружения
vercel env add VITE_API_URL production

# Список переменных
vercel env ls

# Удалить переменную
vercel env rm VITE_API_URL production
```

### Domains

```bash
# Список доменов
vercel domains ls

# Добавить домен
vercel domains add itadiscrm.com.kg

# Удалить домен
vercel domains rm itadiscrm.com.kg
```

---

## DNS/Cloudflare

### DNS проверка

```bash
# nslookup
nslookup itadiscrm.com.kg
nslookup api.itadiscrm.com.kg

# dig
dig itadiscrm.com.kg
dig api.itadiscrm.com.kg +short

# Проверка всех DNS записей
dig itadiscrm.com.kg ANY

# Проверка NS записей
dig itadiscrm.com.kg NS

# Проверка через конкретный DNS сервер
dig @8.8.8.8 itadiscrm.com.kg

# Проверка MX записей
dig itadiscrm.com.kg MX

# Trace DNS propagation
dig +trace itadiscrm.com.kg
```

### Cloudflare CLI (wrangler)

```bash
# Установка
npm install -g wrangler

# Логин
wrangler login

# Список доменов
wrangler pages deployment list

# Очистка кеша
# (делается через Dashboard)
```

---

## Полезные алиасы

Добавьте в `~/.bashrc` или `~/.bash_aliases`:

```bash
# Django shortcuts
alias dj='python manage.py'
alias djrun='python manage.py runserver'
alias djmig='python manage.py migrate'
alias djmake='python manage.py makemigrations'
alias djshell='python manage.py shell'
alias djtest='python manage.py test'

# Service shortcuts
alias itadis-status='sudo systemctl status itadis-crm'
alias itadis-restart='sudo systemctl restart itadis-crm'
alias itadis-logs='sudo journalctl -u itadis-crm -f'

# Nginx shortcuts
alias nginx-test='sudo nginx -t'
alias nginx-restart='sudo systemctl restart nginx'
alias nginx-logs='sudo tail -f /var/log/nginx/itadiscrm-error.log'

# Logs
alias app-logs='tail -f /home/itadis/apps/ITAdisCRMBackend/backend/logs/django.log'

# Git shortcuts
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline'
```

Применить изменения:
```bash
source ~/.bashrc
```

---

## Шпаргалка systemd

```bash
# Управление сервисами
sudo systemctl start SERVICE     # Запустить
sudo systemctl stop SERVICE      # Остановить
sudo systemctl restart SERVICE   # Перезапустить
sudo systemctl reload SERVICE    # Перезагрузить конфиг
sudo systemctl status SERVICE    # Статус
sudo systemctl enable SERVICE    # Автозапуск
sudo systemctl disable SERVICE   # Отключить автозапуск

# Логи
sudo journalctl -u SERVICE                    # Все логи
sudo journalctl -u SERVICE -f                 # Live
sudo journalctl -u SERVICE -n 50              # Последние 50
sudo journalctl -u SERVICE --since today      # За сегодня
sudo journalctl -u SERVICE --since "1 hour ago"  # За час

# Управление systemd
sudo systemctl daemon-reload     # Перезагрузить все unit файлы
sudo systemctl list-units        # Список всех units
sudo systemctl list-timers       # Список таймеров
```

---

## Emergency Commands (Экстренные ситуации)

### Сервер не отвечает

```bash
# 1. Проверить статус всех сервисов
sudo systemctl status itadis-crm nginx

# 2. Перезапустить все
sudo systemctl restart itadis-crm nginx

# 3. Проверить логи
sudo journalctl -u itadis-crm -n 100
sudo tail -n 100 /var/log/nginx/itadiscrm-error.log

# 4. Проверить память/CPU
free -h
top
```

### База данных недоступна

```bash
# 1. Проверить подключение
telnet itadis-crm-db.xxxxx.rds.amazonaws.com 5432

# 2. Проверить Security Groups в AWS Console

# 3. Проверить .env файл
cat /home/itadis/apps/ITAdisCRMBackend/backend/.env.production

# 4. Тест из Django shell
python manage.py check --database default
```

### Диск заполнен

```bash
# 1. Проверить использование
df -h

# 2. Найти большие файлы
sudo du -h / | sort -rh | head -20

# 3. Очистить логи
sudo truncate -s 0 /var/log/nginx/*.log
sudo truncate -s 0 /home/itadis/apps/ITAdisCRMBackend/backend/logs/*.log
sudo journalctl --vacuum-time=7d

# 4. Очистить apt cache
sudo apt-get clean
sudo apt-get autoremove
```

---

**Сохраните этот файл для быстрого доступа к командам! 🚀**
