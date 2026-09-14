#!/usr/bin/env bash
#
# ITAdis CRM - Server Setup Script
# Этот скрипт устанавливает все необходимое ПО на Ubuntu EC2 instance
#

set -e  # Exit on error

echo "======================================"
echo "ITAdis CRM - Server Setup"
echo "======================================"

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для логирования
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Проверка, что скрипт запущен с sudo/root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root or with sudo"
    exit 1
fi

# 1. Обновление системы
log_info "Обновление системы..."
apt update && apt upgrade -y

# 2. Установка Python 3.12
log_info "Установка Python 3.12..."
apt install -y software-properties-common
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y python3.12 python3.12-venv python3.12-dev python3-pip

# 3. Установка PostgreSQL client
log_info "Установка PostgreSQL client..."
apt install -y postgresql-client

# 4. Установка Nginx
log_info "Установка Nginx..."
apt install -y nginx

# 5. Установка Certbot для SSL
log_info "Установка Certbot..."
apt install -y certbot python3-certbot-nginx

# 6. Установка Git
log_info "Установка Git..."
apt install -y git

# 7. Установка дополнительных пакетов
log_info "Установка дополнительных пакетов..."
apt install -y gcc build-essential libpq-dev curl htop

# 8. Создание пользователя для приложения
log_info "Создание пользователя itadis..."
if id "itadis" &>/dev/null; then
    log_warn "Пользователь itadis уже существует"
else
    useradd -m -s /bin/bash itadis
    echo "itadis:itadis123" | chpasswd
    log_info "Пользователь itadis создан (пароль: itadis123 - ИЗМЕНИТЕ ЕГО!)"
fi

# 9. Создание директорий
log_info "Создание директорий..."
mkdir -p /home/itadis/apps
chown -R itadis:itadis /home/itadis/apps

# 10. Настройка firewall (UFW)
log_info "Настройка firewall..."
ufw --force enable
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw reload

log_info "======================================"
log_info "✅ Server setup completed!"
log_info "======================================"
log_info ""
log_info "Следующие шаги:"
log_info "1. Переключитесь на пользователя itadis: sudo su - itadis"
log_info "2. Клонируйте репозиторий в /home/itadis/apps/"
log_info "3. Настройте .env.production файл"
log_info "4. Запустите deploy_app.sh"
log_info ""
log_warn "⚠️  НЕ ЗАБУДЬТЕ изменить пароль пользователя itadis!"
log_warn "    sudo passwd itadis"
