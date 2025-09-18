#!/bin/bash

# Экстренный скрипт для исправления проблем с базой данных
# Создает пользователя, базу данных и файл .env

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
DB_USER="workernet"
DB_PASSWORD="workernet123"
DB_NAME="workernet"

print_status "ЭКСТРЕННОЕ исправление проблем с базой данных..."

# Проверяем, запущен ли PostgreSQL
if ! systemctl is-active --quiet postgresql; then
    print_status "Запускаем PostgreSQL..."
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
fi

# Проверяем подключение к PostgreSQL
if ! sudo -u postgres psql -c '\q' 2>/dev/null; then
    print_error "Не удается подключиться к PostgreSQL"
    exit 1
fi

print_success "PostgreSQL запущен и доступен"

# Удаляем пользователя если существует (для пересоздания)
print_status "Удаляем существующего пользователя $DB_USER (если есть)..."

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
    
    # Проверяем, что пользователь действительно удален
    if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
        print_warning "Не удалось удалить пользователя $DB_USER, продолжаем с существующим..."
    else
        print_status "Пользователь $DB_USER успешно удален"
    fi
else
    print_status "Пользователь $DB_USER не существует"
fi

# Удаляем базу данных если существует (для пересоздания)
print_status "Удаляем существующую базу данных $DB_NAME (если есть)..."
sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null || true

# Создаем пользователя заново
print_status "Создаем пользователя базы данных: $DB_USER"
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    print_status "Пользователь $DB_USER создан"
else
    print_status "Пользователь $DB_USER уже существует, обновляем пароль..."
    sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
fi

# Создаем базу данных заново
print_status "Создаем базу данных: $DB_NAME"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# Предоставляем права
print_status "Предоставляем права пользователю $DB_USER"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;"
sudo -u postgres psql -c "ALTER USER $DB_USER WITH SUPERUSER;" 2>/dev/null || true

# Проверяем подключение
print_status "Проверяем подключение к базе данных..."
if PGPASSWORD="$DB_PASSWORD" psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; then
    print_success "Подключение к базе данных успешно!"
else
    print_error "Не удается подключиться к базе данных"
    print_status "Пробуем альтернативный способ..."
    
    # Пробуем подключиться через localhost
    if PGPASSWORD="$DB_PASSWORD" psql -h 127.0.0.1 -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; then
        print_success "Подключение через 127.0.0.1 успешно!"
    else
        print_error "Все попытки подключения не удались"
        exit 1
    fi
fi

# Создаем .env файл
print_status "Создаем файл .env..."
cat > .env << EOF
SECRET_KEY=workernet-secret-key-2024-development-only
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
REDIS_URL=redis://:redis123@localhost:6379/0
JWT_SECRET_KEY=workernet-jwt-secret-key-2024-development-only
EOF

# Копируем .env в backend/ если нужно
if [ -d "backend" ] && [ ! -f "backend/.env" ]; then
    print_status "Копируем .env в backend/"
    cp .env backend/.env
fi

# Проверяем Django подключение
if [ -d "backend" ]; then
    print_status "Проверяем Django подключение..."
    cd backend
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        
        # Проверяем Django
        if python manage.py check --database default >/dev/null 2>&1; then
            print_success "Django может подключиться к базе данных!"
        else
            print_warning "Django не может подключиться, но продолжаем..."
        fi
    fi
    
    cd ..
fi

print_success "ЭКСТРЕННОЕ исправление базы данных завершено!"
print_status "Теперь можно запустить миграции Django"
