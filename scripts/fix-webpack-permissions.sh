#!/bin/bash

# Скрипт для исправления прав на выполнение для webpack и других npm исполняемых файлов

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

print_status "Исправляем права на выполнение для webpack и других npm исполняемых файлов..."

# Ищем каталог фронтенда
FRONTEND_DIR=""
CANDIDATES=(
    "./frontend"
    "../frontend"
    "../../frontend"
    "$HOME/portal-support-ERP-WorkerNet/frontend"
    "$HOME/workernet-portal/frontend"
)

for dir in "${CANDIDATES[@]}"; do
    if [ -f "$dir/package.json" ]; then
        FRONTEND_DIR="$dir"
        print_status "Найден фронтенд в: $FRONTEND_DIR"
        break
    fi
done

if [ -z "$FRONTEND_DIR" ]; then
    print_error "Каталог фронтенда не найден"
    print_status "Убедитесь, что вы находитесь в корне проекта или укажите путь к фронтенду"
    exit 1
fi

cd "$FRONTEND_DIR"

# Проверяем наличие node_modules
if [ ! -d "node_modules" ]; then
    print_warning "Каталог node_modules не найден. Устанавливаем зависимости..."
    npm install
fi

# Исправляем права на выполнение для всех исполняемых файлов в node_modules/.bin
if [ -d "node_modules/.bin" ]; then
    print_status "Исправляем права на выполнение для исполняемых файлов npm..."
    
    # Считаем количество файлов
    FILE_COUNT=$(find node_modules/.bin -type f | wc -l)
    print_status "Найдено $FILE_COUNT исполняемых файлов"
    
    # Исправляем права
    chmod +x node_modules/.bin/* 2>/dev/null || true
    
    # Проверяем webpack отдельно
    if [ -f "node_modules/.bin/webpack" ]; then
        if [ -x "node_modules/.bin/webpack" ]; then
            print_success "webpack имеет права на выполнение"
        else
            print_warning "webpack не имеет прав на выполнение, исправляем..."
            chmod +x node_modules/.bin/webpack
        fi
    else
        print_warning "webpack не найден в node_modules/.bin"
    fi
    
    print_success "Права на выполнение исправлены для всех исполняемых файлов npm"
else
    print_error "Каталог node_modules/.bin не найден"
    print_status "Убедитесь, что зависимости установлены: npm install"
    exit 1
fi

# Тестируем webpack
print_status "Тестируем webpack..."
if node_modules/.bin/webpack --version >/dev/null 2>&1; then
    WEBPACK_VERSION=$(node_modules/.bin/webpack --version)
    print_success "webpack работает! Версия: $WEBPACK_VERSION"
else
    print_error "webpack не работает. Проверьте установку зависимостей"
    exit 1
fi

print_success "Все права на выполнение исправлены успешно!"
print_status "Теперь можно запускать: npm run build"