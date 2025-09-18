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
    
    if ! command -v docker-compose &> /dev/null; then
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
    
    docker-compose build --no-cache
    
    print_success "Docker images built successfully"
}

# Function to start services
start_services() {
    print_status "Запускаем сервисы..."
    
    # Start database and cache first
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
    
    print_success "Все сервисы успешно запущены"
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    docker-compose exec backend python manage.py migrate
    
    print_success "Database migrations completed successfully"
}

# Function to create superuser
create_superuser() {
    print_status "Creating superuser..."
    
    docker-compose exec backend python manage.py shell << EOF
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
    
    docker-compose exec backend python manage.py collectstatic --noinput
    
    print_success "Static files collected successfully"
}

# Function to show service status
show_status() {
    print_status "Статус сервисов:"
    docker-compose ps
}

# Function to show logs
show_logs() {
    print_status "Showing logs (press Ctrl+C to exit):"
    docker-compose logs -f
}

# Function to stop services
stop_services() {
    print_status "Останавливаем сервисы..."
    docker-compose down
    print_success "Services stopped successfully"
}

# Function to restart services
restart_services() {
    print_status "Перезапускаем сервисы..."
    docker-compose restart
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
    echo "  help      Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs"
    echo "  $0 restart"
}

# Function to show final information
show_final_info() {
    print_success "WorkerNet Portal is now running!"
    echo
    echo "=== Access Information ==="
    echo "Frontend: http://localhost:3000"
    echo "API: http://localhost:8000"
    echo "API Docs: http://localhost:8000/api/docs"
    echo "Admin Panel: http://localhost:8000/admin"
    echo "Grafana: http://localhost:3001 (admin/admin123)"
    echo "Prometheus: http://localhost:9090"
    echo "Kibana: http://localhost:5601"
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
