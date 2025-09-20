#!/bin/bash

# Скрипт для исправления проблемы с SECRET_KEY
# Использование: ./scripts/fix-secret-key.sh

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[ИНФО]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[УСПЕХ]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[ПРЕДУПРЕЖДЕНИЕ]${NC} $1"
}

print_error() {
    echo -e "${RED}[ОШИБКА]${NC} $1"
}

# Функция для экранирования специальных символов для sed
esc() { 
    printf '%s' "$1" | sed -e 's/[|/\\&]/\\&/g' 
}

print_status "Исправляем проблему с SECRET_KEY..."

# Переходим в корневую директорию проекта
cd "$(dirname "$0")/.."

# Проверяем, существует ли файл .env
if [ ! -f ".env" ]; then
    print_error "Файл .env не найден!"
    if [ -f "env.example" ]; then
        print_status "Создаем .env из env.example..."
        cp env.example .env
    else
        print_error "env.example также не найден!"
        exit 1
    fi
fi

# Генерируем новые секреты
print_status "Генерируем новые секреты..."
SECRET_KEY=$(openssl rand -base64 32 2>/dev/null || head -c 32 /dev/urandom | base64)
JWT_SECRET=$(openssl rand -base64 32 2>/dev/null || head -c 32 /dev/urandom | base64)

# Принудительно устанавливаем SECRET_KEY
print_status "Устанавливаем SECRET_KEY..."
if grep -q "^SECRET_KEY=" .env; then
    sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$(esc "$SECRET_KEY")|" .env
else
    echo "SECRET_KEY=$(esc "$SECRET_KEY")" >> .env
fi

# Принудительно устанавливаем JWT_SECRET_KEY
print_status "Устанавливаем JWT_SECRET_KEY..."
if grep -q "^JWT_SECRET_KEY=" .env; then
    sed -i "s|^JWT_SECRET_KEY=.*|JWT_SECRET_KEY=$(esc "$JWT_SECRET")|" .env
else
    echo "JWT_SECRET_KEY=$(esc "$JWT_SECRET")" >> .env
fi

# Копируем .env в backend/
print_status "Копируем .env в backend/..."
if [ -d backend ]; then
    cp -f .env backend/.env
    print_success ".env скопирован в backend/"
else
    print_warning "Папка backend/ не найдена"
fi

# Проверяем, что SECRET_KEY установлен
if grep -q "^SECRET_KEY=" .env && ! grep -q "^SECRET_KEY=$" .env && ! grep -q "your-secret-key-here" .env; then
    print_success "SECRET_KEY успешно установлен"
else
    print_error "Не удалось установить SECRET_KEY"
    exit 1
fi

print_success "Проблема с SECRET_KEY исправлена!"
print_status "Теперь можно запускать миграции: python manage.py migrate"

