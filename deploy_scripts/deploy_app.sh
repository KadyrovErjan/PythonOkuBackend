#!/usr/bin/env bash
#
# ITAdis CRM - Application Deployment Script
# Запускать от имени пользователя itadis
#

set -e  # Exit on error

echo "======================================"
echo "ITAdis CRM - Application Deployment"
echo "======================================"

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка, что скрипт НЕ запущен от root
if [ "$EUID" -eq 0 ]; then 
    log_error "Не запускайте этот скрипт от root!"
    log_error "Используйте: sudo su - itadis && cd /home/itadis/apps/ITAdisCRMBackend && ./deploy_scripts/deploy_app.sh"
    exit 1
fi

# Переменные
APP_DIR="/home/itadis/apps/ITAdisCRMBackend/backend"
VENV_DIR="$APP_DIR/venv"
ENV_FILE="$APP_DIR/.env.production"

# Проверка существования директории
if [ ! -d "$APP_DIR" ]; then
    log_error "Директория $APP_DIR не найдена!"
    log_error "Клонируйте репозиторий сначала:"
    log_error "  cd /home/itadis/apps"
    log_error "  git clone https://github.com/ваш-username/ITAdisCRMBackend.git"
    exit 1
fi

cd "$APP_DIR"

# 1. Создание виртуального окружения
if [ ! -d "$VENV_DIR" ]; then
    log_info "Создание виртуального окружения..."
    python3.12 -m venv venv
else
    log_warn "Виртуальное окружение уже существует"
fi

# 2. Активация виртуального окружения
log_info "Активация виртуального окружения..."
source "$VENV_DIR/bin/activate"

# 3. Обновление pip
log_info "Обновление pip..."
pip install --upgrade pip

# 4. Установка зависимостей
log_info "Установка зависимостей..."
pip install -r requirements.txt
pip install gunicorn

# 5. Проверка .env файла
if [ ! -f "$ENV_FILE" ]; then
    log_error ".env.production файл не найден!"
    log_error "Создайте его на основе .env.production.example"
    exit 1
fi

# 6. Экспорт переменных окружения
log_info "Загрузка переменных окружения..."
export $(cat "$ENV_FILE" | grep -v '^#' | xargs)

# 7. Проверка подключения к БД
log_info "Проверка подключения к базе данных..."
python manage.py check --database default || {
    log_error "Не удалось подключиться к базе данных!"
    log_error "Проверьте настройки в .env.production"
    exit 1
}

# 8. Миграции
log_info "Применение миграций..."
python manage.py migrate --noinput

# 9. Сбор статических файлов
log_info "Сбор статических файлов..."
python manage.py collectstatic --noinput

# 10. Создание необходимых директорий
log_info "Создание директорий для логов и медиа..."
mkdir -p "$APP_DIR/logs"
mkdir -p "$APP_DIR/media/avatars"
chmod 755 "$APP_DIR/media"
chmod 755 "$APP_DIR/media/avatars"

# 11. Тестовый запуск
log_info "Тестовый запуск приложения..."
log_info "Запуск gunicorn на порту 8000 для проверки..."
timeout 5 gunicorn mysite.wsgi:application --bind 0.0.0.0:8000 --workers 1 || true

log_info ""
log_info "======================================"
log_info "✅ Деплой приложения завершен!"
log_info "======================================"
log_info ""
log_info "Следующие шаги:"
log_info "1. Создайте суперпользователя:"
log_info "   python manage.py createsuperuser"
log_info ""
log_info "2. Инициализируйте owner (если нужно):"
log_info "   python manage.py init_owner"
log_info ""
log_info "3. Настройте systemd сервис (от sudo):"
log_info "   exit  # выход из itadis"
log_info "   sudo cp ITAdisCRMBackend/deploy_scripts/itadis-crm.service /etc/systemd/system/"
log_info "   sudo systemctl daemon-reload"
log_info "   sudo systemctl start itadis-crm"
log_info "   sudo systemctl enable itadis-crm"
log_info ""
log_info "4. Настройте Nginx (от sudo):"
log_info "   sudo cp ITAdisCRMBackend/deploy_scripts/nginx_itadiscrm /etc/nginx/sites-available/itadiscrm"
log_info "   sudo ln -s /etc/nginx/sites-available/itadiscrm /etc/nginx/sites-enabled/"
log_info "   sudo nginx -t"
log_info "   sudo systemctl restart nginx"
