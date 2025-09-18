#!/bin/bash

# Скрипт для настройки базы данных PostgreSQL
# Создает пользователя, базу данных и настраивает права доступа

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
DB_TEST_NAME="workernet_test"
POSTGRES_USER="postgres"

print_status "Настройка базы данных PostgreSQL..."

# Проверяем, запущен ли PostgreSQL
if ! systemctl is-active --quiet postgresql; then
    print_status "Запускаем PostgreSQL..."
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
fi

# Проверяем подключение к PostgreSQL
if ! sudo -u postgres psql -c '\q' 2>/dev/null; then
    print_error "Не удается подключиться к PostgreSQL"
    print_status "Проверьте, что PostgreSQL установлен и запущен"
    exit 1
fi

print_success "PostgreSQL запущен и доступен"

# Создаем пользователя workernet
print_status "Создаем пользователя базы данных: $DB_USER"

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
        sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    else
        print_status "Пользователь $DB_USER успешно удален, создаем заново..."
        sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    fi
else
    print_status "Пользователь $DB_USER не существует, создаем..."
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
fi

# Создаем базу данных
print_status "Создаем базу данных: $DB_NAME"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null || {
    print_warning "База данных $DB_NAME уже существует"
}

# Создаем тестовую базу данных
print_status "Создаем тестовую базу данных: $DB_TEST_NAME"
sudo -u postgres psql -c "CREATE DATABASE $DB_TEST_NAME OWNER $DB_USER;" 2>/dev/null || {
    print_warning "Тестовая база данных $DB_TEST_NAME уже существует"
}

# Предоставляем права
print_status "Предоставляем права пользователю $DB_USER"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_TEST_NAME TO $DB_USER;"
sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;"

# Проверяем подключение
print_status "Проверяем подключение к базе данных..."
if PGPASSWORD="$DB_PASSWORD" psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; then
    print_success "Подключение к базе данных успешно!"
else
    print_error "Не удается подключиться к базе данных"
    print_status "Проверьте настройки PostgreSQL"
    exit 1
fi

# Создаем .env файл если его нет
if [ ! -f ".env" ]; then
    print_status "Создаем файл .env..."
    cat > .env << EOF
# Django Settings
SECRET_KEY=workernet-secret-key-2024-development-only
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
DATABASE_TEST_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_TEST_NAME

# Redis
REDIS_URL=redis://:redis123@localhost:6379/0
REDIS_CACHE_URL=redis://:redis123@localhost:6379/1

# Celery
CELERY_BROKER_URL=redis://:redis123@localhost:6379/2
CELERY_RESULT_BACKEND=redis://:redis123@localhost:6379/3

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=admin@workernet.com
EMAIL_HOST_PASSWORD=password
DEFAULT_FROM_EMAIL=WorkerNet Portal <noreply@workernet.com>

# File Storage
DEFAULT_FILE_STORAGE=django.core.files.storage.FileSystemStorage
MEDIA_ROOT=/app/media
MEDIA_URL=/media/
STATIC_ROOT=/app/static
STATIC_URL=/static/

# Security
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CORS_ALLOW_CREDENTIALS=True
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# JWT
JWT_SECRET_KEY=workernet-jwt-secret-key-2024-development-only
JWT_ACCESS_TOKEN_LIFETIME=3600
JWT_REFRESH_TOKEN_LIFETIME=604800

# Monitoring
PROMETHEUS_ENABLED=True
GRAFANA_ENABLED=True

# Feature Flags
FEATURE_FLAGS_ENABLED=True
AB_TESTING_ENABLED=True

# API Versioning
API_VERSION=v1
API_VERSIONING_STRATEGY=url

# Multitenancy
MULTITENANCY_ENABLED=True
TENANT_HEADER=X-Tenant-ID

# Performance
CACHE_TTL=3600
MAX_UPLOAD_SIZE=10485760
RATE_LIMIT_ENABLED=True

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Development
DEVELOPMENT_MODE=True
HOT_RELOAD=True
DEBUG_TOOLBAR=True
EOF
    print_success "Файл .env создан"
else
    print_warning "Файл .env уже существует"
fi

# Копируем .env в backend/ если нужно
if [ -d "backend" ] && [ ! -f "backend/.env" ]; then
    print_status "Копируем .env в backend/"
    cp .env backend/.env
fi

print_success "Настройка базы данных завершена!"
print_status "Теперь можно запустить миграции Django"
