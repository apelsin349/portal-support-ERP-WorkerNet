#!/bin/bash

# Скрипт для исправления проблем с npm зависимостями
# Удаляет старые lock файлы и пересоздает их

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

# Переход в корень проекта
cd "$(dirname "$0")/.." || exit 1

print_status "Исправление проблем с npm зависимостями..."

# Проверяем наличие Node.js
if ! command -v node >/dev/null 2>&1; then
    print_error "Node.js не найден. Установите Node.js 18+ и повторите попытку."
    exit 1
fi

print_status "Версия Node.js: $(node -v)"
print_status "Версия npm: $(npm -v)"

# Очищаем npm кэш
print_status "Очищаем npm кэш..."
npm cache clean --force >/dev/null 2>&1 || true

# Настраиваем npm для работы без прокси
print_status "Настраиваем npm..."
npm config set registry https://registry.npmjs.org/ >/dev/null 2>&1 || true
npm config delete proxy >/dev/null 2>&1 || true
npm config delete https-proxy >/dev/null 2>&1 || true
npm config set strict-ssl true >/dev/null 2>&1 || true

# Обрабатываем frontend
if [ -d "frontend" ]; then
    print_status "Обрабатываем frontend..."
    cd frontend
    
    # Удаляем старые lock файлы
    if [ -f "package-lock.json" ]; then
        print_status "Удаляем старый package-lock.json..."
        rm -f package-lock.json
    fi
    
    if [ -d "node_modules" ]; then
        print_status "Удаляем node_modules..."
        rm -rf node_modules
    fi
    
    # Устанавливаем зависимости
    print_status "Устанавливаем зависимости frontend..."
    if npm install --no-optional --no-audit --no-fund; then
        print_success "Зависимости frontend установлены успешно!"
    else
        print_warning "Не удалось установить зависимости frontend. Продолжаем..."
    fi
    
    cd ..
else
    print_warning "Каталог frontend не найден"
fi

# Обрабатываем корневой package.json (если есть)
if [ -f "package.json" ]; then
    print_status "Обрабатываем корневой package.json..."
    
    # Удаляем старые lock файлы
    if [ -f "package-lock.json" ]; then
        print_status "Удаляем старый корневой package-lock.json..."
        rm -f package-lock.json
    fi
    
    if [ -d "node_modules" ]; then
        print_status "Удаляем корневые node_modules..."
        rm -rf node_modules
    fi
    
    # Устанавливаем зависимости
    print_status "Устанавливаем корневые зависимости..."
    if npm install --no-optional --no-audit --no-fund; then
        print_success "Корневые зависимости установлены успешно!"
    else
        print_warning "Не удалось установить корневые зависимости. Продолжаем..."
    fi
fi

print_success "Исправление npm зависимостей завершено!"
print_status "Теперь можно запустить установку заново."
