#!/bin/bash

# УСТАРЕЛ: Используйте universal-install-update.sh
# Этот скрипт устарел и будет заменен на universal-install-update.sh

echo "[ВНИМАНИЕ] Этот скрипт устарел!"
echo "[ИНФО] Используйте новый универсальный скрипт:"
echo "  ./scripts/universal-install-update.sh"
echo
echo "[ИНФО] Перенаправляем на универсальный скрипт..."

# Перенаправляем на универсальный скрипт
exec ./scripts/universal-install-update.sh "$@"

# Скрипт принудительного обновления зависимостей (УСТАРЕЛ)
# Работает на Ubuntu и других Linux дистрибутивах

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
    echo -e "${YELLOW}[ВНИМАНИЕ]${NC} $1"
}

print_error() {
    echo -e "${RED}[ОШИБКА]${NC} $1"
}

# Проверяем платформу
check_platform() {
    if [[ "$(uname -s)" != "Linux" ]]; then
        print_error "Этот скрипт предназначен только для Linux (Ubuntu)"
        exit 1
    fi
    
    # Проверяем, что это Ubuntu
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        if [[ "$ID" == "ubuntu" ]]; then
            print_status "Обнаружена Ubuntu $VERSION"
        else
            print_warning "Обнаружен $PRETTY_NAME. Скрипт может работать, но тестировался только на Ubuntu"
        fi
    else
        print_warning "Не удалось определить дистрибутив Linux"
    fi
}

# Находим корневую директорию проекта
find_project_directory() {
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    if [ ! -f "$PROJECT_DIR/requirements.txt" ] && [ ! -f "$PROJECT_DIR/backend/requirements.txt" ]; then
        print_error "Не удалось найти корневую директорию проекта"
        exit 1
    fi
    
    print_status "Корневая директория проекта: $PROJECT_DIR"
}

# Принудительное обновление зависимостей Python
force_update_python_deps() {
    print_status "🔧 Принудительное обновление зависимостей Python..."
    
    # Определяем путь к venv
    VENV_DIR="$PROJECT_DIR/backend/venv"
    if [ ! -f "$VENV_DIR/bin/activate" ]; then
        if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
            VENV_DIR="$PROJECT_DIR/venv"
            print_status "Используем альтернативный venv: $VENV_DIR"
        else
            print_error "Виртуальное окружение Python не найдено"
            print_status "Создаем новое виртуальное окружение..."
            cd "$PROJECT_DIR/backend"
            python3 -m venv venv
            VENV_DIR="$PROJECT_DIR/backend/venv"
        fi
    fi
    
    # Активируем окружение
    print_status "Активируем виртуальное окружение..."
    source "$VENV_DIR/bin/activate"
    
    # Очищаем кэш pip
    print_status "Очищаем кэш pip..."
    pip cache purge 2>/dev/null || true
    
    # Обновляем pip, setuptools и wheel
    print_status "Обновляем pip, setuptools и wheel..."
    pip install -U pip setuptools wheel
    
    # Удаляем старый хеш файл
    REQUIREMENTS_HASH_FILE="$VENV_DIR/.requirements_hash"
    rm -f "$REQUIREMENTS_HASH_FILE"
    
    # Ищем и устанавливаем requirements
    REQ_PRIMARY="$PROJECT_DIR/requirements.txt"
    REQ_SECONDARY="$PROJECT_DIR/backend/requirements.txt"
    DEV_PRIMARY="$PROJECT_DIR/requirements-dev.txt"
    DEV_SECONDARY="$PROJECT_DIR/backend/requirements-dev.txt"
    
    if [ -f "$REQ_PRIMARY" ]; then
        print_status "Устанавливаем зависимости из $REQ_PRIMARY..."
        pip install -r "$REQ_PRIMARY" --upgrade --force-reinstall
        # Сохраняем новый хеш файла
        sha256sum "$REQ_PRIMARY" > "$REQUIREMENTS_HASH_FILE" 2>/dev/null || true
    elif [ -f "$REQ_SECONDARY" ]; then
        print_status "Устанавливаем зависимости из $REQ_SECONDARY..."
        pip install -r "$REQ_SECONDARY" --upgrade --force-reinstall
        # Сохраняем новый хеш файла
        sha256sum "$REQ_SECONDARY" > "$REQUIREMENTS_HASH_FILE" 2>/dev/null || true
    else
        print_error "requirements.txt не найден ни в backend/, ни в корне"
        exit 1
    fi
    
    if [ -f "$DEV_PRIMARY" ]; then
        print_status "Устанавливаем dev зависимости из $DEV_PRIMARY..."
        pip install -r "$DEV_PRIMARY" --upgrade --force-reinstall
    elif [ -f "$DEV_SECONDARY" ]; then
        print_status "Устанавливаем dev зависимости из $DEV_SECONDARY..."
        pip install -r "$DEV_SECONDARY" --upgrade --force-reinstall
    fi
    
    # Проверяем устаревшие пакеты
    print_status "Проверяем устаревшие пакеты..."
    pip list --outdated 2>/dev/null | head -10 || true
    
    print_success "Зависимости Python принудительно обновлены"
}

# Принудительное обновление зависимостей Node.js
force_update_nodejs_deps() {
    if [ -d "$PROJECT_DIR/frontend" ]; then
        print_status "🔧 Принудительное обновление зависимостей Node.js..."
        cd "$PROJECT_DIR/frontend"
        
        # Очищаем кэш npm
        print_status "Очищаем кэш npm..."
        npm cache clean --force 2>/dev/null || true
        
        # Удаляем node_modules и package-lock.json
        print_status "Удаляем старые зависимости..."
        rm -rf node_modules package-lock.json 2>/dev/null || true
        
        # Устанавливаем зависимости заново
        print_status "Устанавливаем зависимости Node.js..."
        npm install
        
        print_success "Зависимости Node.js принудительно обновлены"
    else
        print_warning "Директория frontend не найдена, пропускаем обновление Node.js зависимостей"
    fi
}

# Проверяем зависимости после обновления
check_dependencies() {
    print_status "🔍 Проверяем зависимости после обновления..."
    
    # Проверяем Python зависимости
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
        print_status "Проверяем Python зависимости..."
        pip check 2>/dev/null || print_warning "Обнаружены проблемы с Python зависимостями"
    fi
    
    # Проверяем Node.js зависимости
    if [ -d "$PROJECT_DIR/frontend" ]; then
        cd "$PROJECT_DIR/frontend"
        print_status "Проверяем Node.js зависимости..."
        npm audit --audit-level=moderate 2>/dev/null || print_warning "Обнаружены проблемы с Node.js зависимостями"
    fi
}

# Основная функция
main() {
    print_status "🚀 Принудительное обновление зависимостей WorkerNet Portal"
    echo
    
    check_platform
    find_project_directory
    
    print_warning "Этот скрипт принудительно обновит все зависимости Python и Node.js"
    print_warning "Это может занять несколько минут..."
    echo
    
    # Подтверждение от пользователя
    read -p "Продолжить? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Операция отменена пользователем"
        exit 0
    fi
    
    force_update_python_deps
    force_update_nodejs_deps
    check_dependencies
    
    echo
    print_success "🎉 Принудительное обновление зависимостей завершено!"
    print_status "Рекомендуется перезапустить сервисы для применения изменений"
}

# Запуск основной функции
main "$@"
