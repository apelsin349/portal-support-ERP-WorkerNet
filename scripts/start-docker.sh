#!/bin/bash

# WorkerNet Portal Docker Quick Start Script
# This script starts the WorkerNet Portal using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[ИНФО]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[ВНИМАНИЕ]${NC} $1"
}

print_error() {
    echo -e "${RED}[ОШИБКА]${NC} $1"
}

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Function to check if .env file exists
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from example..."
        if [ -f "env.example" ]; then
            cp env.example .env
            print_success ".env file created from example"
        else
            print_error "env.example file not found. Please create .env file manually."
            exit 1
        fi
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p data/postgres
    mkdir -p data/redis
    mkdir -p data/grafana
    mkdir -p data/prometheus
    mkdir -p data/elasticsearch
    
    print_success "Directories created successfully"
}

# Function to build Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Build frontend with PWA support
    print_status "Building frontend with PWA support..."
    if command -v docker-compose &> /dev/null; then
        docker-compose build --no-cache frontend
        # Build other services
        print_status "Building other services..."
        docker-compose build --no-cache
    else
        docker compose build --no-cache frontend
        # Build other services
        print_status "Building other services..."
        docker compose build --no-cache
    fi
    
    print_success "Docker images built successfully"
}

# Function to start services
start_services() {
    print_status "Запускаем сервисы..."
    
    # Start database and cache first
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d db redis
        # Wait for database to be ready
        print_status "Waiting for database to be ready..."
        sleep 10
        # Start backend
        docker-compose up -d backend
        # Wait for backend to be ready
        print_status "Waiting for backend to be ready..."
        sleep 15
        # Start remaining services
        docker-compose up -d
    else
        docker compose up -d db redis
        # Wait for database to be ready
        print_status "Waiting for database to be ready..."
        sleep 10
        # Start backend
        docker compose up -d backend
        # Wait for backend to be ready
        print_status "Waiting for backend to be ready..."
        sleep 15
        # Start remaining services
        docker compose up -d
    fi
    
    print_success "Все сервисы успешно запущены"
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose exec backend python manage.py migrate
    else
        docker compose exec backend python manage.py migrate
    fi
    
    print_success "Database migrations completed successfully"
}

# Function to create superuser
create_superuser() {
    print_status "Creating superuser..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose exec backend python manage.py shell << EOF
    else
        docker compose exec backend python manage.py shell << EOF
    fi
from django.contrib.auth import get_user_model
from app.models.tenant import Tenant

User = get_user_model()

# Create default tenant
tenant, created = Tenant.objects.get_or_create(
    name='Default Tenant',
    defaults={
        'slug': 'default',
        'domain': 'localhost',
        'is_active': True
    }
)

# Create superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@workernet.com',
        password='admin123',
        tenant=tenant
    )
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
EOF
    
    print_success "Superuser created successfully"
}

# Function to collect static files
collect_static() {
    print_status "Collecting static files..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose exec backend python manage.py collectstatic --noinput
    else
        docker compose exec backend python manage.py collectstatic --noinput
    fi
    
    print_success "Static files collected successfully"
}

# Function to show service status
show_status() {
    print_status "Статус сервисов:"
    if command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        docker compose ps
    fi
}

# Function to show logs
show_logs() {
    print_status "Showing logs (press Ctrl+C to exit):"
    if command -v docker-compose &> /dev/null; then
        docker-compose logs -f
    else
        docker compose logs -f
    fi
}

# Function to stop services
stop_services() {
    print_status "Останавливаем сервисы..."
    if command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        docker compose down
    fi
    print_success "Services stopped successfully"
}

# Function to restart services
restart_services() {
    print_status "Перезапускаем сервисы..."
    if command -v docker-compose &> /dev/null; then
        docker-compose restart
    else
        docker compose restart
    fi
    print_success "Services restarted successfully"
}

# Function to show help
show_help() {
    echo "WorkerNet Portal Docker Management Script"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start     Запустить все сервисы"
    echo "  stop      Остановить все сервисы"
    echo "  restart   Перезапустить все сервисы"
    echo "  status    Показать статус сервисов"
    echo "  logs      Show logs"
    echo "  build     Build Docker images"
    echo "  migrate   Run database migrations"
    echo "  superuser Create superuser"
    echo "  static    Collect static files"
    echo "  branch    Показать текущую ветку Git"
    echo "  help      Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs"
    echo "  $0 restart"
}

# Function to show current Git branch
show_branch() {
    print_status "Информация о ветке Git:"
    
    if [ -d ".git" ]; then
        local current_branch
        current_branch=$(git branch --show-current 2>/dev/null || git rev-parse --abbrev-ref HEAD)
        echo "Текущая ветка: $current_branch"
        
        local remote_branch
        remote_branch=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo "не настроена")
        echo "Отслеживаемая ветка: $remote_branch"
        
        local last_commit
        last_commit=$(git log -1 --oneline 2>/dev/null || echo "недоступен")
        echo "Последний коммит: $last_commit"
        
        local status
        status=$(git status --porcelain 2>/dev/null | wc -l)
        if [ "$status" -gt 0 ]; then
            echo "Незафиксированные изменения: $status файлов"
        else
            echo "Рабочая директория чистая"
        fi
    else
        print_warning "Не найдена Git директория"
    fi
}

# Function to show final information
show_final_info() {
    print_success "WorkerNet Portal is now running!"
    echo
    echo "=== Access Information ==="
    echo "Frontend (PWA): http://localhost:3000"
    echo "API: http://localhost:8000"
    echo "API Docs: http://localhost:8000/api/docs"
    echo "Admin Panel: http://localhost:8000/admin"
    echo "Grafana: http://localhost:3001 (admin/admin123)"
    echo "Prometheus: http://localhost:9090"
    echo "Kibana: http://localhost:5601"
    echo
    echo "=== PWA Features ==="
    echo "• Install as app on mobile/desktop"
    echo "• Offline support"
    echo "• Push notifications"
    echo "• Auto-updates"
    echo
    echo "=== Default Credentials ==="
    echo "Admin User: admin"
    echo "Admin Password: admin123"
    echo
    echo "=== Management Commands ==="
    echo "View logs: $0 logs"
    echo "Проверка статуса: $0 status"
    echo "Перезапуск: $0 restart"
    echo "Stop: $0 stop"
    echo "Git branch info: $0 branch"
    echo
}

# Main function
main() {
    case "${1:-start}" in
        start)
            check_docker
            check_env_file
            create_directories
            build_images
            start_services
            run_migrations
            create_superuser
            collect_static
            show_final_info
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        build)
            check_docker
            build_images
            ;;
        migrate)
            run_migrations
            ;;
        superuser)
            create_superuser
            ;;
        static)
            collect_static
            ;;
        branch)
            show_branch
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
