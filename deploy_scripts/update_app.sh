#!/usr/bin/env bash
#
# ITAdis CRM - Application Update Script
# Скрипт для обновления приложения после изменений в git
# Запускать от имени пользователя itadis
#

set -e

echo "======================================"
echo "ITAdis CRM - Application Update"
echo "======================================"

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

# Проверка пользователя
if [ "$EUID" -eq 0 ]; then 
    log_error "Не запускайте этот скрипт от root!"
    exit 1
fi

APP_DIR="/home/itadis/apps/ITAdisCRMBackend/backend"
VENV_DIR="$APP_DIR/venv"

cd "$APP_DIR"

# 1. Создание backup конфигурации
log_info "Создание backup .env файла..."
cp .env.production .env.production.backup

# 2. Pull изменений из git
log_info "Получение изменений из git..."
git fetch origin
git pull origin main

# 3. Активация venv
log_info "Активация виртуального окружения..."
source "$VENV_DIR/bin/activate"

# 4. Обновление зависимостей
log_info "Обновление зависимостей..."
pip install -r requirements.txt

# 5. Экспорт переменных
export $(cat .env.production | grep -v '^#' | xargs)

# 6. Миграции
log_info "Применение миграций..."
python manage.py migrate --noinput

# 7. Сбор статики
log_info "Сбор статических файлов..."
python manage.py collectstatic --noinput

# 8. Перезапуск сервиса
log_info "Перезапуск приложения..."
sudo systemctl restart itadis-crm

# 9. Проверка статуса
sleep 3
if sudo systemctl is-active --quiet itadis-crm; then
    log_info "✅ Приложение успешно обновлено и работает!"
else
    log_error "❌ Ошибка! Приложение не запустилось!"
    log_error "Проверьте логи: sudo journalctl -u itadis-crm -n 50"
    exit 1
fi

# 10. Показать последние логи
log_info ""
log_info "Последние 20 строк лога:"
sudo journalctl -u itadis-crm -n 20 --no-pager

log_info ""
log_info "======================================"
log_info "✅ Обновление завершено!"
log_info "======================================"
log_info ""
log_info "Проверьте сайт: https://itadiscrm.com.kg"
log_info "Для просмотра логов:"
log_info "  sudo journalctl -u itadis-crm -f"
log_info "  tail -f /home/itadis/apps/ITAdisCRMBackend/backend/logs/gunicorn-error.log"
