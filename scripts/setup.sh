#!/bin/bash

# WorkerNet Portal Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up WorkerNet Portal..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
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
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    print_status "Detected OS: $OS"
}

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    print_status "All dependencies are installed ✓"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p uploads
    mkdir -p data/postgres
    mkdir -p data/redis
    mkdir -p data/elasticsearch
    mkdir -p data/prometheus
    mkdir -p data/grafana
    
    print_status "Directories created ✓"
}

# Copy environment files
setup_environment() {
    print_status "Setting up environment files..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_warning "Created .env file from .env.example"
        print_warning "Please edit .env file with your configuration"
    else
        print_status ".env file already exists ✓"
    fi
    
    if [ ! -f docker-compose.override.yml ]; then
        cp docker-compose.override.yml.example docker-compose.override.yml
        print_warning "Created docker-compose.override.yml from example"
    else
        print_status "docker-compose.override.yml already exists ✓"
    fi
}

# Generate secrets
generate_secrets() {
    print_status "Generating secrets..."
    
    # Generate random secrets if not set
    if ! grep -q "SECRET_KEY=" .env || grep -q "your-secret-key-here" .env; then
        SECRET_KEY=$(openssl rand -base64 32)
        sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        print_status "Generated SECRET_KEY"
    fi
    
    if ! grep -q "JWT_SECRET=" .env || grep -q "your-jwt-secret-here" .env; then
        JWT_SECRET=$(openssl rand -base64 32)
        sed -i.bak "s/JWT_SECRET=.*/JWT_SECRET=$JWT_SECRET/" .env
        print_status "Generated JWT_SECRET"
    fi
    
    if ! grep -q "ENCRYPTION_KEY=" .env || grep -q "your-encryption-key-here" .env; then
        ENCRYPTION_KEY=$(openssl rand -base64 32)
        sed -i.bak "s/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=$ENCRYPTION_KEY/" .env
        print_status "Generated ENCRYPTION_KEY"
    fi
    
    # Clean up backup files
    rm -f .env.bak
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    
    docker-compose build --no-cache
    
    print_status "Docker images built ✓"
}

# Start services
start_services() {
    print_status "Starting services..."
    
    docker-compose up -d
    
    print_status "Services started ✓"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    print_status "Waiting for PostgreSQL..."
    until docker-compose exec -T postgres pg_isready -U workernet -d worker_net; do
        sleep 2
    done
    print_status "PostgreSQL is ready ✓"
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    until docker-compose exec -T redis redis-cli ping; do
        sleep 2
    done
    print_status "Redis is ready ✓"
    
    # Wait for Elasticsearch
    print_status "Waiting for Elasticsearch..."
    until curl -f http://localhost:9200/_cluster/health > /dev/null 2>&1; do
        sleep 2
    done
    print_status "Elasticsearch is ready ✓"
    
    # Wait for Backend
    print_status "Waiting for Backend API..."
    until curl -f http://localhost:8000/api/system/health > /dev/null 2>&1; do
        sleep 2
    done
    print_status "Backend API is ready ✓"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    docker-compose exec backend python manage.py migrate
    
    print_status "Database migrations completed ✓"
}

# Create superuser
create_superuser() {
    print_status "Creating superuser..."
    
    # Check if superuser already exists
    if docker-compose exec -T backend python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser')" | grep -q "Superuser exists"; then
        print_status "Superuser already exists ✓"
    else
        print_warning "Please create a superuser manually:"
        echo "docker-compose exec backend python manage.py createsuperuser"
    fi
}

# Load initial data
load_initial_data() {
    print_status "Loading initial data..."
    
    # Check if initial data exists
    if [ -f "fixtures/initial_data.json" ]; then
        docker-compose exec backend python manage.py loaddata fixtures/initial_data.json
        print_status "Initial data loaded ✓"
    else
        print_warning "No initial data file found, skipping..."
    fi
}

# Create search indexes
create_search_indexes() {
    print_status "Creating search indexes..."
    
    docker-compose exec backend python manage.py search_index --rebuild
    
    print_status "Search indexes created ✓"
}

# Show service URLs
show_urls() {
    print_status "Setup completed! 🎉"
    echo ""
    echo "Service URLs:"
    echo "  Frontend:     http://localhost:3000"
    echo "  Backend API:  http://localhost:8000"
    echo "  API Docs:     http://localhost:8000/api/docs"
    echo "  Admin Panel:  http://localhost:8000/admin"
    echo "  Grafana:      http://localhost:3001 (admin/admin)"
    echo "  Prometheus:   http://localhost:9090"
    echo "  Celery Flower: http://localhost:5555"
    echo "  Mailhog:      http://localhost:8025"
    echo ""
    echo "Useful commands:"
    echo "  View logs:    docker-compose logs -f [service]"
    echo "  Stop all:     docker-compose down"
    echo "  Restart:      docker-compose restart [service]"
    echo "  Shell:        docker-compose exec backend python manage.py shell"
    echo ""
}

# Main execution
main() {
    check_os
    check_dependencies
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
