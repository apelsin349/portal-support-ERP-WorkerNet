#!/bin/bash

# WorkerNet Portal Setup Script
# This script sets up the development environment

set -e

echo "🚀 Настраиваем WorkerNet Portal..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[ИНФО]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[ВНИМАНИЕ]${NC} $1"
}

print_error() {
    echo -e "${RED}[ОШИБКА]${NC} $1"
}

# Check if running on supported OS
check_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        print_error "Неподдерживаемая операционная система: $OSTYPE"
        exit 1
    fi
    print_status "Обнаружена ОС: $OS"
}

# Check if required tools are installed
check_dependencies() {
    print_status "Проверяем зависимости..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker не установлен. Пожалуйста, установите Docker."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose не установлен. Пожалуйста, установите Docker Compose."
        exit 1
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        print_error "Git не установлен. Пожалуйста, установите Git."
        exit 1
    fi
    
    print_status "Все зависимости установлены ✓"
}

# Create necessary directories
create_directories() {
    print_status "Создаём необходимые директории..."
    
    mkdir -p logs
    mkdir -p uploads
    mkdir -p data/postgres
    mkdir -p data/redis
    mkdir -p data/elasticsearch
    mkdir -p data/prometheus
    mkdir -p data/grafana
    
    print_status "Директории созданы ✓"
}

# Copy environment files
setup_environment() {
    print_status "Настраиваем файлы окружения..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_warning "Создан .env из .env.example"
        print_warning "Отредактируйте .env под вашу конфигурацию"
    else
        print_status ".env уже существует ✓"
    fi
    
    if [ ! -f docker-compose.override.yml ]; then
        cp docker-compose.override.yml.example docker-compose.override.yml
        print_warning "Создан docker-compose.override.yml из примера"
    else
        print_status "docker-compose.override.yml уже существует ✓"
    fi
}

# Generate secrets
generate_secrets() {
    print_status "Генерируем секреты..."
    
    # Generate random secrets if not set
    if ! grep -q "SECRET_KEY=" .env || grep -q "your-secret-key-here" .env; then
        SECRET_KEY=$(openssl rand -base64 32)
        sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        print_status "Сгенерирован SECRET_KEY"
    fi
    
    if ! grep -q "JWT_SECRET=" .env || grep -q "your-jwt-secret-here" .env; then
        JWT_SECRET=$(openssl rand -base64 32)
        sed -i.bak "s/JWT_SECRET=.*/JWT_SECRET=$JWT_SECRET/" .env
        print_status "Сгенерирован JWT_SECRET"
    fi
    
    if ! grep -q "ENCRYPTION_KEY=" .env || grep -q "your-encryption-key-here" .env; then
        ENCRYPTION_KEY=$(openssl rand -base64 32)
        sed -i.bak "s/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=$ENCRYPTION_KEY/" .env
        print_status "Сгенерирован ENCRYPTION_KEY"
    fi
    
    # Clean up backup files
    rm -f .env.bak
}

# Build Docker images
build_images() {
    print_status "Собираем Docker-образы..."
    
    docker-compose build --no-cache
    
    print_status "Docker-образы собраны ✓"
}

# Start services
start_services() {
    print_status "Запускаем сервисы..."
    
    docker-compose up -d
    
    print_status "Сервисы запущены ✓"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Ожидание готовности сервисов..."
    
    # Wait for PostgreSQL
    print_status "Ожидание PostgreSQL..."
    until docker-compose exec -T postgres pg_isready -U workernet -d workernet; do
        sleep 2
    done
    print_status "PostgreSQL готов ✓"
    
    # Wait for Redis
    print_status "Ожидание Redis..."
    until docker-compose exec -T redis redis-cli ping; do
        sleep 2
    done
    print_status "Redis готов ✓"
    
    # Wait for Elasticsearch
    print_status "Ожидание Elasticsearch..."
    until curl -f http://localhost:9200/_cluster/health > /dev/null 2>&1; do
        sleep 2
    done
    print_status "Elasticsearch готов ✓"
    
    # Wait for Backend
    print_status "Ожидание Backend API..."
    until curl -f http://localhost:8000/api/system/health > /dev/null 2>&1; do
        sleep 2
    done
    print_status "Backend API готов ✓"
}

# Run database migrations
run_migrations() {
    print_status "Выполняем миграции базы данных..."
    
    docker-compose exec backend python manage.py migrate --fake-initial
    
    print_status "Миграции выполнены ✓"
}

# Create superuser
create_superuser() {
    print_status "Создаём суперпользователя..."
    
    # Check if superuser already exists
    if docker-compose exec -T backend python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser')" | grep -q "Superuser exists"; then
        print_status "Суперпользователь уже существует ✓"
    else
        print_warning "Создайте суперпользователя вручную:"
        echo "docker-compose exec backend python manage.py createsuperuser"
    fi
}

# Load initial data
load_initial_data() {
    print_status "Загружаем начальные данные..."
    
    # Check if initial data exists
    if [ -f "fixtures/initial_data.json" ]; then
        docker-compose exec backend python manage.py loaddata fixtures/initial_data.json
        print_status "Начальные данные загружены ✓"
    else
        print_warning "Файл начальных данных не найден, пропускаем..."
    fi
}

# Create search indexes
create_search_indexes() {
    print_status "Создаём поисковые индексы..."
    
    docker-compose exec backend python manage.py search_index --rebuild
    
    print_status "Поисковые индексы созданы ✓"
}

# Show service URLs
show_urls() {
    print_status "Настройка завершена! 🎉"
    echo ""
    echo "Адреса сервисов:"
    echo "  Frontend:      http://localhost:3000"
    echo "  Backend API:   http://localhost:8000"
    echo "  API Docs:      http://localhost:8000/api/docs"
    echo "  Admin Panel:   http://localhost:8000/admin"
    echo "  Grafana:       http://localhost:3001 (admin/admin)"
    echo "  Prometheus:    http://localhost:9090"
    echo "  Celery Flower: http://localhost:5555"
    echo "  Mailhog:       http://localhost:8025"
    echo ""
    echo "Полезные команды:"
    echo "  Логи:          docker-compose logs -f [service]"
    echo "  Остановить:    docker-compose down"
    echo "  Перезапуск:    docker-compose restart [service]"
    echo "  Shell:         docker-compose exec backend python manage.py shell"
    echo ""
}

# Main execution
main() {
    check_os
    check_dependencies
    # Fix script permissions and normalize line endings (idempotent)
    if [ -f "$(dirname "$0")/fix-perms.sh" ]; then
        bash "$(dirname "$0")/fix-perms.sh" || true
    fi
    create_directories
    setup_environment
    generate_secrets
    build_images
    start_services
    wait_for_services
    run_migrations
    create_superuser
    load_initial_data
    create_search_indexes
    show_urls
}

# Run main function
main "$@"
