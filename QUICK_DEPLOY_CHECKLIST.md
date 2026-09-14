# ⚡ Quick Deploy Checklist - ITAdis CRM Backend на AWS

## 📋 Prerequisite (Подготовка)

- [ ] AWS аккаунт создан
- [ ] Домен itadiscrm.com.kg куплен
- [ ] Cloudflare аккаунт создан
- [ ] SSH ключ сгенерирован

---

## 🗄️ Шаг 1: AWS RDS (База данных) - 10 минут

1. **AWS Console → RDS → Create database**
   ```
   - Engine: PostgreSQL 15
   - Template: Free tier / Production
   - DB identifier: itadis-crm-db
   - Master username: itadis_admin
   - Master password: [создайте и сохраните!]
   - Instance: db.t3.micro
   - Storage: 20 GB
   - Public access: No
   - Security group: itadis-db-sg
   ```

2. **Сохраните endpoint:**
   ```
   itadis-crm-db.xxxxxxxxxx.ap-south-1.rds.amazonaws.com
   ```

---

## 🖥️ Шаг 2: AWS EC2 (Сервер) - 15 минут

1. **EC2 → Launch Instance**
   ```
   - Name: itadis-crm-backend
   - AMI: Ubuntu 22.04 LTS
   - Instance type: t2.micro / t2.small
   - Key pair: itadis-crm-key [создайте и скачайте .pem]
   - Security group: itadis-web-sg
     * SSH (22): My IP
     * HTTP (80): 0.0.0.0/0
     * HTTPS (443): 0.0.0.0/0
   ```

2. **Elastic IP**
   - EC2 → Elastic IPs → Allocate
   - Associate с вашим EC2
   - **Сохраните IP:** `13.127.XX.XX`

3. **Связать RDS и EC2**
   - RDS Security Group (itadis-db-sg)
   - Inbound: PostgreSQL (5432) → Source: itadis-web-sg

---

## 🔧 Шаг 3: Настройка сервера - 20 минут

### 3.1 Подключение к EC2

```bash
ssh -i "itadis-crm-key.pem" ubuntu@ваш-elastic-ip
```

### 3.2 Установка ПО (автоматически)

```bash
# Скачать setup скрипт
wget https://raw.githubusercontent.com/ваш-username/ITAdisCRMBackend/main/deploy_scripts/setup_server.sh

# Сделать исполняемым
chmod +x setup_server.sh

# Запустить
sudo ./setup_server.sh
```

**Или вручную:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install -y python3.12 python3.12-venv python3.12-dev
sudo apt install -y postgresql-client nginx certbot python3-certbot-nginx git
sudo apt install -y gcc build-essential libpq-dev curl htop

# Создать пользователя
sudo useradd -m -s /bin/bash itadis
sudo passwd itadis
```

---

## 📦 Шаг 4: Деплой приложения - 15 минут

### 4.1 Клонирование репозитория

```bash
# Переключиться на itadis
sudo su - itadis

# Клонировать
mkdir -p ~/apps && cd ~/apps
git clone https://github.com/ваш-username/ITAdisCRMBackend.git
cd ITAdisCRMBackend/backend
```

### 4.2 Настройка окружения

```bash
# Создать .env.production
cp .env.production.example .env.production
nano .env.production
```

**Заполните:**
```env
SECRET_KEY=сгенерируйте_новый
DEBUG=False
ALLOWED_HOSTS=itadiscrm.com.kg,www.itadiscrm.com.kg,api.itadiscrm.com.kg,ваш-elastic-ip
DB_HOST=itadis-crm-db.xxxxx.ap-south-1.rds.amazonaws.com
DB_NAME=itadis_db
DB_USER=itadis_admin
DB_PASSWORD=ваш_пароль_rds
CORS_ALLOWED_ORIGINS=https://itadiscrm.com.kg,https://www.itadiscrm.com.kg
```

**Генерация SECRET_KEY:**
```bash
python3.12 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4.3 Подготовка БД

```bash
# Подключиться к RDS
psql -h itadis-crm-db.xxxxx.ap-south-1.rds.amazonaws.com -U itadis_admin -d postgres

# Создать БД (в psql)
CREATE DATABASE itadis_db;
\q
```

### 4.4 Запуск деплой скрипта

```bash
cd /home/itadis/apps/ITAdisCRMBackend
chmod +x deploy_scripts/*.sh
./deploy_scripts/deploy_app.sh
```

### 4.5 Создание суперюзера

```bash
source venv/bin/activate
export $(cat .env.production | xargs)
python manage.py createsuperuser
python manage.py init_owner  # если нужно
```

---

## 🚀 Шаг 5: Systemd + Nginx - 10 минут

### 5.1 Systemd сервис

```bash
# Выйти из itadis
exit

# Копировать и запустить сервис
sudo cp /home/itadis/apps/ITAdisCRMBackend/deploy_scripts/itadis-crm.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start itadis-crm
sudo systemctl enable itadis-crm
sudo systemctl status itadis-crm  # Проверка
```

### 5.2 Nginx

```bash
# Копировать конфиг
sudo cp /home/itadis/apps/ITAdisCRMBackend/deploy_scripts/nginx_itadiscrm /etc/nginx/sites-available/itadiscrm

# Активировать
sudo ln -s /etc/nginx/sites-available/itadiscrm /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Удалить дефолт

# Права доступа
sudo usermod -aG itadis www-data

# Тест и перезапуск
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🌐 Шаг 6: DNS (Cloudflare) - 10 минут

### 6.1 Добавить домен в Cloudflare

1. https://dash.cloudflare.com/ → Add Site
2. Введите: `itadiscrm.com.kg`
3. План: Free
4. Скопируйте NS серверы (например):
   ```
   christian.ns.cloudflare.com
   ulla.ns.cloudflare.com
   ```

### 6.2 Изменить NS у регистратора

1. Панель регистратора домена
2. DNS/Nameservers → замените на NS из Cloudflare
3. Сохраните
4. ⏰ Ждите 1-24 часа

### 6.3 Добавить DNS записи в Cloudflare

| Type | Name | Content          | Proxy  |
|------|------|------------------|--------|
| A    | @    | ваш-elastic-ip   | ✅ On  |
| A    | www  | ваш-elastic-ip   | ✅ On  |
| A    | api  | ваш-elastic-ip   | ✅ On  |

### 6.4 SSL/TLS настройки Cloudflare

- SSL/TLS → **Full (strict)**
- Edge Certificates → Always Use HTTPS: **On**
- Automatic HTTPS Rewrites: **On**

---

## 🔒 Шаг 7: SSL сертификат - 5 минут

**⚠️ ВАЖНО:** Сначала дождитесь, пока DNS заработает!

```bash
# Проверка DNS
nslookup itadiscrm.com.kg

# Получение сертификата
sudo certbot --nginx -d itadiscrm.com.kg -d www.itadiscrm.com.kg -d api.itadiscrm.com.kg

# Следуйте инструкциям:
# 1. Email
# 2. Agree to Terms
# 3. Выберите "2" для redirect HTTP -> HTTPS

# Тест автообновления
sudo certbot renew --dry-run
```

---

## ✅ Шаг 8: Проверка - 5 минут

### 8.1 Проверка сервисов

```bash
sudo systemctl status itadis-crm
sudo systemctl status nginx
```

### 8.2 Проверка в браузере

- ✅ https://itadiscrm.com.kg/admin/
- ✅ https://api.itadiscrm.com.kg/api/v1/
- ✅ https://api.itadiscrm.com.kg/api/schema/swagger-ui/

### 8.3 Тест API

```bash
curl -I https://api.itadiscrm.com.kg/api/v1/

curl -X POST https://api.itadiscrm.com.kg/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "ваш_пароль"}'
```

### 8.4 Проверка логов

```bash
# Django logs
tail -f /home/itadis/apps/ITAdisCRMBackend/backend/logs/django.log

# Gunicorn logs
sudo journalctl -u itadis-crm -f

# Nginx logs
sudo tail -f /var/log/nginx/itadiscrm-error.log
```

---

## 🔄 Обновление приложения (в будущем)

```bash
# Подключиться к серверу
ssh -i itadis-crm-key.pem ubuntu@ваш-elastic-ip

# Запустить update скрипт
sudo su - itadis
cd /home/itadis/apps/ITAdisCRMBackend
./deploy_scripts/update_app.sh
```

---

## 📊 Полезные команды

```bash
# Просмотр статуса
sudo systemctl status itadis-crm nginx

# Перезапуск
sudo systemctl restart itadis-crm
sudo systemctl restart nginx

# Логи
sudo journalctl -u itadis-crm -n 50        # Последние 50 строк
sudo journalctl -u itadis-crm -f           # Live логи
tail -f /home/itadis/apps/ITAdisCRMBackend/backend/logs/*.log

# Мониторинг ресурсов
htop
df -h
free -h

# Проверка портов
sudo ss -tulpn | grep LISTEN
```

---

## 🐛 Troubleshooting

### 502 Bad Gateway

```bash
# Проверить gunicorn
sudo systemctl status itadis-crm
sudo journalctl -u itadis-crm -n 50

# Проверить socket
ls -la /home/itadis/apps/ITAdisCRMBackend/backend/itadis.sock

# Перезапустить
sudo systemctl restart itadis-crm nginx
```

### Не подключается к БД

```bash
# Проверить подключение
telnet itadis-crm-db.xxxxx.rds.amazonaws.com 5432

# Проверить Security Groups в AWS Console
# RDS SG должна разрешать соединения от EC2 SG
```

### Статика не загружается

```bash
# Пересобрать статику
sudo su - itadis
cd /home/itadis/apps/ITAdisCRMBackend/backend
source venv/bin/activate
python manage.py collectstatic --noinput --clear

# Проверить права
ls -la staticfiles/
chmod 755 staticfiles/
```

---

## 🎯 Итого: ~90 минут

- ✅ RDS настроен
- ✅ EC2 настроен
- ✅ Приложение задеплоено
- ✅ Nginx работает
- ✅ SSL настроен
- ✅ DNS работает
- ✅ Backend доступен глобально!

---

## 📝 Следующие шаги

1. ✅ Backend на AWS - **ГОТОВО!**
2. ⏭️ Frontend на Vercel
3. ⏭️ CI/CD (GitHub Actions)
4. ⏭️ Мониторинг (CloudWatch)
5. ⏭️ Backup (RDS snapshots)

---

**Готово! Backend развернут на production! 🚀**

Домены работают:
- https://itadiscrm.com.kg
- https://www.itadiscrm.com.kg  
- https://api.itadiscrm.com.kg
