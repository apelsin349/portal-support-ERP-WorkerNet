#!/bin/bash

# Скрипт для проверки и исправления базы данных
# Использует функции из universal-install-update.sh

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

# Проверка и исправление базы данных
check_and_fix_database() {
    print_status "Проверяем и исправляем базу данных..."
    
    DB_USER="workernet"
    DB_PASSWORD="workernet123"
    DB_NAME="workernet"
    
    # Проверяем подключение
    if PGPASSWORD="$DB_PASSWORD" psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; then
        print_success "База данных работает корректно"
        return 0
    fi
    
    print_warning "Проблема с базой данных, исправляем..."
    
    # Удаляем и пересоздаем пользователя и базу данных
    # Проверяем, существует ли пользователь
    if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
        print_status "Пользователь $DB_USER существует, удаляем..."
        
        # Завершаем все активные сессии пользователя
        sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE usename = '$DB_USER';" 2>/dev/null || true
        sleep 1
        
        # Удаляем все объекты, принадлежащие пользователю
        sudo -u postgres psql -c "REASSIGN OWNED BY $DB_USER TO postgres;" 2>/dev/null || true
        sudo -u postgres psql -c "DROP OWNED BY $DB_USER;" 2>/dev/null || true
        
        # Удаляем пользователя
        sudo -u postgres psql -c "DROP USER $DB_USER;" 2>/dev/null || true
        sleep 2
    fi
    
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null || true
    
    # Создаем пользователя заново
    if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
        sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD' CREATEDB SUPERUSER;"
    else
        print_warning "Пользователь $DB_USER все еще существует, обновляем пароль..."
        sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD' CREATEDB SUPERUSER;"
    fi
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    
    # Проверяем снова
    if PGPASSWORD="$DB_PASSWORD" psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; then
        print_success "База данных исправлена!"
        return 0
    else
        print_error "Не удалось исправить базу данных"
        return 1
    fi
}

# Проверка Django подключения
check_django_connection() {
    print_status "Проверяем Django подключение..."
    
    if [ ! -d "backend" ]; then
        print_error "Каталог backend не найден"
        return 1
    fi
    
    cd backend
    
    if [ ! -f "venv/bin/activate" ]; then
        print_error "Виртуальное окружение не найдено"
        return 1
    fi
    
    source venv/bin/activate
    
    # Создаем .env файл если его нет
    if [ ! -f ".env" ]; then
        print_status "Создаем файл .env..."
        cat > .env << EOF
SECRET_KEY=workernet-secret-key-2024-development-only
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DATABASE_URL=postgresql://workernet:workernet123@localhost:5432/workernet
REDIS_URL=redis://:redis123@localhost:6379/0
JWT_SECRET_KEY=workernet-jwt-secret-key-2024-development-only
EOF
    fi
    
    if python manage.py check --database default >/dev/null 2>&1; then
        print_success "Django может подключиться к базе данных"
        return 0
    else
        print_error "Django не может подключиться к базе данных"
        return 1
    fi
}

# Основная функция
main() {
    print_status "Проверка и исправление базы данных WorkerNet Portal..."
    echo
    
    # Проверяем PostgreSQL
    if ! systemctl is-active --quiet postgresql; then
        print_warning "PostgreSQL не запущен, запускаем..."
        sudo systemctl start postgresql
    fi
    
    # Проверяем и исправляем базу данных
    if ! check_and_fix_database; then
        print_error "Не удалось исправить базу данных"
        exit 1
    fi
    
    # Проверяем Django подключение
    if ! check_django_connection; then
        print_warning "Django не может подключиться, но база данных работает"
    fi
    
    print_success "Проверка завершена!"
    echo
    echo "Теперь можно запустить миграции:"
    echo "cd backend"
    echo "source venv/bin/activate"
    echo "python manage.py migrate"
}

# Запуск
main "$@"
