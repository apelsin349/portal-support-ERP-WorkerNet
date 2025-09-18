#!/bin/bash

# Скрипт для настройки Redis
# Настраивает Redis с паролем и создает необходимые базы данных

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Без цвета

# Функции для вывода
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

# Переменные
REDIS_PASSWORD="redis123"

print_status "Настройка Redis..."

# Проверяем, запущен ли Redis
if ! systemctl is-active --quiet redis-server; then
    print_status "Запускаем Redis..."
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
fi

print_success "Redis запущен"

# Проверяем подключение к Redis
if redis-cli ping >/dev/null 2>&1; then
    print_success "Redis доступен"
else
    print_error "Redis недоступен"
    exit 1
fi

# Настраиваем пароль для Redis
print_status "Настраиваем пароль для Redis..."

# Создаем резервную копию конфигурации (если файл существует)
if [ -f "/etc/redis/redis.conf" ]; then
    sudo cp /etc/redis/redis.conf /etc/redis/redis.conf.backup 2>/dev/null || true
fi

# Добавляем пароль в конфигурацию
if [ -f "/etc/redis/redis.conf" ]; then
    if ! sudo grep -q "requirepass" /etc/redis/redis.conf 2>/dev/null; then
        echo "requirepass $REDIS_PASSWORD" | sudo tee -a /etc/redis/redis.conf >/dev/null 2>&1
        print_success "Пароль добавлен в конфигурацию Redis"
    else
        print_warning "Пароль уже настроен в Redis"
    fi
else
    print_warning "Файл конфигурации Redis не найден: /etc/redis/redis.conf"
    print_status "Пропускаем настройку пароля Redis"
fi

# Перезапускаем Redis для применения изменений
print_status "Перезапускаем Redis..."
sudo systemctl restart redis-server

# Проверяем подключение с паролем
print_status "Проверяем подключение с паролем..."
if redis-cli -a "$REDIS_PASSWORD" ping >/dev/null 2>&1; then
    print_success "Redis настроен с паролем"
else
    print_warning "Не удается подключиться с паролем, но Redis работает"
fi

# Создаем тестовые ключи для проверки баз данных
print_status "Тестируем базы данных Redis..."
redis-cli -a "$REDIS_PASSWORD" -n 0 set "test:db0" "ok" >/dev/null 2>&1 || true
redis-cli -a "$REDIS_PASSWORD" -n 1 set "test:db1" "ok" >/dev/null 2>&1 || true
redis-cli -a "$REDIS_PASSWORD" -n 2 set "test:db2" "ok" >/dev/null 2>&1 || true
redis-cli -a "$REDIS_PASSWORD" -n 3 set "test:db3" "ok" >/dev/null 2>&1 || true

print_success "Настройка Redis завершена!"
print_status "Redis настроен с паролем: $REDIS_PASSWORD"
print_status "Доступны базы данных: 0, 1, 2, 3"
