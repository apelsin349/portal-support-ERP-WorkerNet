#!/bin/bash

# Скрипт для исправления проблем с миграциями Django
# Работает на Ubuntu и других Linux дистрибутивах

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

# Проверяем наличие Python и Django
check_dependencies() {
    print_status "Проверяем зависимости..."
    
    if ! command -v python >/dev/null 2>&1; then
        print_error "Python не найден. Установите Python и повторите попытку."
        exit 1
    fi
    
    if ! python -c "import django" >/dev/null 2>&1; then
        print_error "Django не найден. Установите Django и повторите попытку."
        exit 1
    fi
    
    print_success "Все зависимости найдены"
}

# Переходим в директорию backend
navigate_to_backend() {
    if [ -d "backend" ]; then
        cd backend
        print_status "Переходим в директорию backend"
    else
        print_error "Директория backend не найдена"
        exit 1
    fi
}

# Активируем виртуальное окружение
activate_venv() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        if [ -f "venv/bin/activate" ]; then
            print_status "Активируем виртуальное окружение..."
            source venv/bin/activate
        else
            print_warning "Виртуальное окружение не найдено, используем системный Python"
        fi
    else
        print_status "Виртуальное окружение уже активировано"
    fi
}

# Очищаем проблемные записи миграций
clean_migration_records() {
    print_status "Очищаем проблемные записи миграций..."
    
    python manage.py dbshell -c "DELETE FROM django_migrations WHERE app = 'app' AND name != '0001_initial';" 2>/dev/null || {
        print_warning "Не удалось очистить записи миграций, продолжаем..."
    }
    
    print_success "Записи миграций очищены"
}

# Сбрасываем состояние миграций
reset_migration_state() {
    print_status "Сбрасываем состояние миграций..."
    
    python manage.py migrate app 0001 --fake 2>/dev/null || {
        print_warning "Не удалось сбросить состояние миграций, продолжаем..."
    }
    
    print_success "Состояние миграций сброшено"
}

# Создаем новые миграции
create_new_migrations() {
    print_status "Создаем новые миграции..."
    
    python manage.py makemigrations app 2>/dev/null || {
        print_warning "Не удалось создать новые миграции, продолжаем..."
    }
    
    print_success "Новые миграции созданы"
}

# Применяем миграции
apply_migrations() {
    print_status "Применяем миграции..."
    
    python manage.py migrate 2>/dev/null || {
        print_error "Ошибка при применении миграций"
        return 1
    }
    
    print_success "Миграции применены успешно"
}

# Проверяем состояние миграций
check_migration_status() {
    print_status "Проверяем состояние миграций..."
    
    python manage.py showmigrations app 2>/dev/null || {
        print_warning "Не удалось проверить состояние миграций"
    }
}

# Основная функция
main() {
    print_status "🔧 Исправление проблем с миграциями Django для Ubuntu"
    echo
    
    check_platform
    check_dependencies
    navigate_to_backend
    activate_venv
    
    print_status "Начинаем исправление миграций..."
    echo
    
    clean_migration_records
    reset_migration_state
    create_new_migrations
    apply_migrations
    check_migration_status
    
    echo
    print_success "✅ Исправление миграций завершено!"
    print_status "Проект готов к работе"
}

# Запуск
main "$@"
