#!/bin/bash

# Скрипт для исправления ALLOWED_HOSTS на сервере
# Использует IP-адрес сервера для доступа к Django

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Без цвета

print_status() {
    echo -e "${BLUE}[ИНФО]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[УСПЕХ]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[ВНИМАНИЕ]${NC} $1"
}

print_error() {
    echo -e "${RED}[ОШИБКА]${NC} $1"
}

# Определяем IP-адрес сервера
SERVER_IP=$(hostname -I | awk '{print $1}' | head -1)

if [ -z "$SERVER_IP" ]; then
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")
fi

print_status "Определен IP-адрес сервера: $SERVER_IP"

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    print_error "Файл .env не найден!"
    print_status "Создаем .env из env.example..."
    cp env.example .env
fi

# Создаем резервную копию .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

print_status "Создана резервная копия .env"

# Обновляем DOMAIN_OR_IP
sed -i "s|^DOMAIN_OR_IP=.*|DOMAIN_OR_IP=$SERVER_IP|" .env

# Обновляем ALLOWED_HOSTS
sed -i "s|^ALLOWED_HOSTS=.*|ALLOWED_HOSTS=$SERVER_IP,127.0.0.1,0.0.0.0,localhost|" .env

# Обновляем CORS_ALLOWED_ORIGINS
sed -i "s|^CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=http://$SERVER_IP:3000,http://127.0.0.1:3000,http://localhost:3000|" .env

# Обновляем CSRF_TRUSTED_ORIGINS
sed -i "s|^CSRF_TRUSTED_ORIGINS=.*|CSRF_TRUSTED_ORIGINS=http://$SERVER_IP:3000,http://127.0.0.1:3000,http://localhost:3000|" .env

print_success "Обновлен файл .env с IP-адресом сервера: $SERVER_IP"

# Копируем .env в backend/ если нужно
if [ -d "backend" ]; then
    cp .env backend/.env
    print_status "Скопирован .env в backend/"
fi

# Перезапускаем сервисы
print_status "Перезапускаем сервисы..."

if systemctl is-active --quiet workernet-backend; then
    sudo systemctl restart workernet-backend
    print_success "Сервис workernet-backend перезапущен"
else
    print_warning "Сервис workernet-backend не запущен"
fi

if systemctl is-active --quiet workernet-frontend; then
    sudo systemctl restart workernet-frontend
    print_success "Сервис workernet-frontend перезапущен"
else
    print_warning "Сервис workernet-frontend не запущен"
fi

# Проверяем статус сервисов
print_status "Проверяем статус сервисов..."
sleep 3

if systemctl is-active --quiet workernet-backend; then
    print_success "✅ workernet-backend работает"
else
    print_error "❌ workernet-backend не работает"
fi

if systemctl is-active --quiet workernet-frontend; then
    print_success "✅ workernet-frontend работает"
else
    print_error "❌ workernet-frontend не работает"
fi

echo
print_success "Исправление ALLOWED_HOSTS завершено!"
echo
print_status "Теперь WorkerNet Portal доступен по адресам:"
echo "   Frontend: http://$SERVER_IP:3000"
echo "   API: http://$SERVER_IP:8000"
echo "   Админ-панель: http://$SERVER_IP:8000/admin"
echo
print_status "Логин: admin | Пароль: admin123"
