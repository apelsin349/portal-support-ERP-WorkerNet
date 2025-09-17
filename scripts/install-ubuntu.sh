#!/bin/bash

# WorkerNet Portal Installation Script for Ubuntu 24.04 LTS
# This script installs all dependencies and sets up the WorkerNet Portal

set -e

# Repository configuration (can be overridden via env)
REPO_URL="${WORKERNET_REPO_URL:-https://github.com/apelsin349/portal-support-ERP-WorkerNet.git}"
REPO_URL_MIRROR="${WORKERNET_REPO_MIRROR:-}"
REPO_BRANCH="${WORKERNET_BRANCH:-main}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Network timeouts (tunable via env)
CURL_CONNECT_TIMEOUT=${CURL_CONNECT_TIMEOUT:-3}
CURL_MAX_TIME=${CURL_MAX_TIME:-10}
CURL_OPTS="--fail --silent --show-error --location --connect-timeout $CURL_CONNECT_TIMEOUT --max-time $CURL_MAX_TIME"

# APT timeouts
APT_HTTP_TIMEOUT=${APT_HTTP_TIMEOUT:-5}
APT_HTTPS_TIMEOUT=${APT_HTTPS_TIMEOUT:-5}

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Additional status helper
ok() {
    echo -e "${GREEN}[OK]${NC} $1"
}

# Simple reachability check (HEAD)
check_url() {
    curl -sSfI --connect-timeout "$CURL_CONNECT_TIMEOUT" --max-time "$CURL_CONNECT_TIMEOUT" "$1" >/dev/null 2>&1
}

# Check external repos and set fallbacks
check_connectivity() {
    print_status "Checking external repositories reachability..."
    APT_PRIMARY_OK=true
    DOCKER_OK=true
    NODESOURCE_OK=true
    GITHUB_OK=true
    GITHUB_RAW_OK=true
    PYPI_OK=true

    # Ubuntu archives
    if ! check_url "http://archive.ubuntu.com/ubuntu/"; then APT_PRIMARY_OK=false; fi

    # Docker repo
    if ! check_url "https://download.docker.com/linux/ubuntu/dists/"; then DOCKER_OK=false; fi

    # NodeSource
    if ! check_url "https://deb.nodesource.com/"; then NODESOURCE_OK=false; fi

    # GitHub and raw
    if ! check_url "https://github.com/"; then GITHUB_OK=false; fi
    if ! check_url "https://raw.githubusercontent.com/"; then GITHUB_RAW_OK=false; fi

    # PyPI
    if ! check_url "https://pypi.org/simple/"; then PYPI_OK=false; fi

    $APT_PRIMARY_OK && ok "APT primary mirror reachable" || print_warning "APT primary mirror not reachable"
    $DOCKER_OK && ok "Docker repo reachable" || print_warning "Docker repo not reachable"
    $NODESOURCE_OK && ok "NodeSource reachable" || print_warning "NodeSource not reachable"
    $GITHUB_OK && ok "GitHub reachable" || print_warning "GitHub not reachable"
    $GITHUB_RAW_OK && ok "GitHub RAW reachable" || print_warning "GitHub RAW not reachable"
    $PYPI_OK && ok "PyPI reachable" || print_warning "PyPI not reachable"
}

# Try to switch APT mirrors to RU mirror if primary is down
configure_apt_mirror_if_needed() {
    if [ "$APT_PRIMARY_OK" = false ]; then
        print_warning "Switching APT mirrors to ru.archive.ubuntu.com"
        sudo cp -f /etc/apt/sources.list /etc/apt/sources.list.bak || true
        sudo sed -i 's|http://archive.ubuntu.com/ubuntu/|http://ru.archive.ubuntu.com/ubuntu/|g' /etc/apt/sources.list || true
        sudo sed -i 's|http://security.ubuntu.com/ubuntu|http://ru.archive.ubuntu.com/ubuntu|g' /etc/apt/sources.list || true
    fi
    sudo apt -o Acquire::http::Timeout=$APT_HTTP_TIMEOUT -o Acquire::https::Timeout=$APT_HTTPS_TIMEOUT update || true
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        exit 1
    fi
}

# Function to check Ubuntu version
check_ubuntu_version() {
    if ! command_exists lsb_release; then
        print_status "Installing lsb-release..."
        sudo apt -o Acquire::http::Timeout=$APT_HTTP_TIMEOUT -o Acquire::https::Timeout=$APT_HTTPS_TIMEOUT update && sudo apt install -y lsb-release
    fi
    
    UBUNTU_VERSION=$(lsb_release -rs)
    if [[ "$UBUNTU_VERSION" != "24.04" ]]; then
        print_warning "This script is designed for Ubuntu 24.04 LTS. You are running Ubuntu $UBUNTU_VERSION"
        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Function to update system
update_system() {
    print_status "Updating system packages..."
    sudo apt -o Acquire::http::Timeout=$APT_HTTP_TIMEOUT -o Acquire::https::Timeout=$APT_HTTPS_TIMEOUT update && sudo apt upgrade -y
    print_success "System updated successfully"
}

# Function to install basic packages
install_basic_packages() {
    print_status "Installing basic packages..."
    sudo apt install -y \
        curl \
        wget \
        git \
        build-essential \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        unzip \
        make \
        htop \
        tree \
        vim \
        nano
    print_success "Basic packages installed successfully"
}

# Function to install Python (prefer 3.12 on Ubuntu 24.04, fallback to 3.11, else generic python3)
install_python() {
    print_status "Installing Python..."

    PYTHON_TARGET=""

    if sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip; then
        PYTHON_TARGET="/usr/bin/python3.12"
    elif sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip; then
        PYTHON_TARGET="/usr/bin/python3.11"
    else
        # Fallback to default python3 packages available on the system
        sudo apt install -y python3 python3-venv python3-dev python3-pip
    fi

    if [[ -n "$PYTHON_TARGET" && -x "$PYTHON_TARGET" ]]; then
        sudo update-alternatives --install /usr/bin/python3 python3 "$PYTHON_TARGET" 1
        print_success "Python installed successfully ($("$PYTHON_TARGET" -V 2>&1))"
    else
        print_success "Python installed successfully ($(python3 -V 2>&1))"
    fi
}

# Function to install Node.js 18 (with resilient fallbacks)
install_nodejs() {
    print_status "Installing Node.js 18..."

    # 1) NodeSource (обычно быстрее по версиям)
    if curl $CURL_OPTS https://deb.nodesource.com/setup_18.x | sudo -E bash - && \
       sudo apt install -y nodejs; then
        print_success "Node.js 18 installed (Node: $(node -v 2>/dev/null), NPM: $(npm -v 2>/dev/null))"
        return 0
    fi

    print_warning "NodeSource недоступен. Пробую репозитории Ubuntu..."
    sudo apt -o Acquire::http::Timeout=$APT_HTTP_TIMEOUT -o Acquire::https::Timeout=$APT_HTTPS_TIMEOUT update || true
    if sudo apt install -y nodejs npm; then
        print_success "Node.js установлен из Ubuntu (Node: $(node -v 2>/dev/null), NPM: $(npm -v 2>/dev/null))"
        return 0
    fi

    print_warning "Репозитории Ubuntu недоступны. Пробую NVM..."
    curl $CURL_OPTS https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash || true
    # shellcheck source=/dev/null
    [ -s "$HOME/.nvm/nvm.sh" ] && . "$HOME/.nvm/nvm.sh"
    if command -v nvm >/dev/null 2>&1; then
        # Зеркала, если github/nodejs недоступны
        export NVM_NODEJS_ORG_MIRROR="https://npmmirror.com/mirrors/node"
        export NVM_IOJS_ORG_MIRROR="https://npmmirror.com/mirrors/iojs"
        if nvm install 18 && nvm alias default 18 && nvm use 18; then
            print_success "Node.js установлен через NVM (Node: $(node -v 2>/dev/null), NPM: $(npm -v 2>/dev/null))"
            npm config set registry https://registry.npmmirror.com || true
            return 0
        fi
    fi

    print_warning "NVM недоступен. Пробую Snap..."
    if sudo snap install node --channel=18/stable --classic; then
        if ! echo "$PATH" | grep -q "/snap/bin"; then
            echo 'export PATH="/snap/bin:$PATH"' >> "$HOME/.profile"
            export PATH="/snap/bin:$PATH"
        fi
        print_success "Node.js установлен через Snap (Node: $(node -v 2>/dev/null), NPM: $(npm -v 2>/dev/null))"
        npm config set registry https://registry.npmmirror.com || true
        return 0
    fi

    print_error "Не удалось установить Node.js всеми способами. Проверьте сеть и повторите."
    exit 1
}

# Function to install PostgreSQL 15
install_postgresql() {
    print_status "Installing PostgreSQL 15..."
    sudo apt install -y postgresql postgresql-contrib postgresql-client
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    print_success "PostgreSQL 15 installed successfully"
}

# Function to install Redis
install_redis() {
    print_status "Installing Redis..."
    sudo apt install -y redis-server
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    print_success "Redis installed successfully"
}

# Function to install Docker
install_docker() {
    print_status "Installing Docker..."
    
    # Remove old Docker packages
    sudo apt remove -y docker docker-engine docker.io containerd runc || true
    
    # Install Docker (prefer official repo)
    curl $CURL_OPTS https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg || true
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null || true
    sudo apt -o Acquire::http::Timeout=$APT_HTTP_TIMEOUT -o Acquire::https::Timeout=$APT_HTTPS_TIMEOUT update || true
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin || true
    
    # If official failed, try ubuntu docker.io and compose plugin / standalone
    if ! command -v docker >/dev/null 2>&1; then
        sudo apt install -y docker.io || true
    fi
    # Compose V2 plugin (preferred)
    sudo apt install -y docker-compose-plugin || true
    # As a fallback, try standalone docker-compose if plugin unavailable
    if ! docker compose version >/dev/null 2>&1; then
        sudo apt install -y docker-compose || true
        # Provide alias for consistency
        if ! grep -q "alias docker-compose='docker compose'" "$HOME/.bashrc" 2>/dev/null; then
            echo "alias docker-compose='docker compose'" >> "$HOME/.bashrc"
        fi
    fi

    # Ensure Docker daemon enabled on boot
    sudo systemctl enable --now docker || true

    # Add user to docker group
    sudo usermod -aG docker $USER || true
    newgrp docker || true
    print_success "Docker installed successfully"
}

# Function to install additional tools
install_additional_tools() {
    print_status "Installing additional tools..."
    
    # Git LFS
    sudo apt install -y git-lfs
    git lfs install
    
    # Python development tools
    sudo apt install -y python3-dev python3-venv python3-pip
    
    # Database tools (use generic client to match Ubuntu release)
    sudo apt install -y postgresql-client-common postgresql-client || true

    # Useful CLI utilities used by scripts
    sudo apt install -y jq net-tools unzip make htop tree || true
    
    print_success "Additional tools installed successfully"
}

# Verify that all required dependencies are present and report versions
verify_dependencies() {
    print_status "Verifying installed dependencies..."

    # Commands
    declare -A CMDS=(
        [curl]="curl --version | head -n1"
        [git]="git --version"
        [python3]="python3 -V"
        [pip3]="pip3 -V"
        [node]="node -v"
        [npm]="npm -v"
        [docker]="docker --version"
    )

    for cmd in "${!CMDS[@]}"; do
        if command -v "$cmd" >/dev/null 2>&1; then
            eval ${CMDS[$cmd]} || true
        else
            print_warning "Missing command: $cmd"
            MISSING=1
        fi
    done

    # Docker Compose (plugin or standalone)
    if docker compose version >/dev/null 2>&1; then
        docker compose version | head -n1
    elif command -v docker-compose >/dev/null 2>&1; then
        docker-compose --version
    else
        print_warning "Missing Docker Compose (plugin or standalone)"
        MISSING=1
    fi

    # Services status
    print_status "Checking services status (PostgreSQL/Redis/Docker)"
    sudo systemctl is-enabled postgresql >/dev/null 2>&1 && echo "postgresql: enabled" || echo "postgresql: not enabled"
    sudo systemctl is-active postgresql >/dev/null 2>&1 && echo "postgresql: active" || echo "postgresql: inactive"

    sudo systemctl is-enabled redis-server >/dev/null 2>&1 && echo "redis-server: enabled" || echo "redis-server: not enabled" 
    sudo systemctl is-active redis-server >/dev/null 2>&1 && echo "redis-server: active" || echo "redis-server: inactive"

    sudo systemctl is-enabled docker >/dev/null 2>&1 && echo "docker: enabled" || echo "docker: not enabled"
    sudo systemctl is-active docker >/dev/null 2>&1 && echo "docker: active" || echo "docker: inactive"

    if [ "${MISSING:-0}" = "1" ]; then
        print_warning "One or more dependencies are missing. Attempting to continue, but build may fail."
    else
        print_success "All required dependencies are present"
    fi
}

# Function to configure PostgreSQL
configure_postgresql() {
    print_status "Configuring PostgreSQL..."
    
    # Set password for postgres user
    sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres123';" || true
    
    # Create user if not exists and set password
    if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='workernet'" | grep -q 1; then
        sudo -u postgres psql -c "CREATE USER workernet WITH PASSWORD 'workernet123';"
    else
        sudo -u postgres psql -c "ALTER USER workernet WITH PASSWORD 'workernet123';" || true
    fi

    # Create databases if not exist
    if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='worker_net'" | grep -q 1; then
        sudo -u postgres createdb worker_net
    fi
    if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='worker_net_test'" | grep -q 1; then
        sudo -u postgres createdb worker_net_test
    fi

    # Grants (idempotent)
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE worker_net TO workernet;" || true
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE worker_net_test TO workernet;" || true
    
    # Enable auto-start on boot
    sudo systemctl enable postgresql || true
    print_success "PostgreSQL configured successfully"
}

# Function to configure Redis
configure_redis() {
    print_status "Configuring Redis..."
    
    # Set password for Redis
    sudo sed -i 's/# requirepass foobared/requirepass redis123/' /etc/redis/redis.conf
    
    # Configure Redis for better performance
    sudo sed -i 's/# maxmemory <bytes>/maxmemory 512mb/' /etc/redis/redis.conf
    sudo sed -i 's/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf
    
    # Restart Redis
    sudo systemctl restart redis-server
    # Enable auto-start on boot
    sudo systemctl enable redis-server || true

    print_success "Redis configured successfully"
}

# Function to create project directory
create_project_directory() {
    print_status "Creating project directory..."
    
    PROJECT_DIR="$HOME/workernet-portal"
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    print_success "Project directory created at $PROJECT_DIR"
}

# Function to clone repository
clone_repository() {
    print_status "Cloning/updating repository..."

    # Create directory if missing
    if [ ! -d "portal-support-ERP-WorkerNet" ]; then
        if git clone "$REPO_URL" portal-support-ERP-WorkerNet; then
            :
        elif [ -n "$REPO_URL_MIRROR" ]; then
            print_warning "Primary repo unavailable, trying mirror: $REPO_URL_MIRROR"
            git clone "$REPO_URL_MIRROR" portal-support-ERP-WorkerNet
        else
            print_error "Failed to clone repository"
            exit 1
        fi
    fi

    cd portal-support-ERP-WorkerNet

    # Ensure remote URL is correct (prefer primary, otherwise keep existing)
    CURRENT_URL=$(git remote get-url origin 2>/dev/null || echo "")
    if [ -n "$REPO_URL" ] && [ "$CURRENT_URL" != "$REPO_URL" ]; then
        git remote set-url origin "$REPO_URL" || true
    fi

    # Fetch and hard-update to requested branch
    git fetch --all --prune || true
    # Determine default branch if requested not found
    if ! git show-ref --verify --quiet "refs/remotes/origin/$REPO_BRANCH"; then
        REPO_BRANCH=$(git remote show origin | awk '/HEAD branch/ {print $NF}')
        REPO_BRANCH=${REPO_BRANCH:-main}
        print_warning "Requested branch not found; using default: $REPO_BRANCH"
    fi

    git checkout "$REPO_BRANCH" 2>/dev/null || git checkout -B "$REPO_BRANCH"
    git reset --hard "origin/$REPO_BRANCH" || true
    git submodule update --init --recursive || true

    print_success "Repository is up-to-date (branch: $REPO_BRANCH)"
}

# Function to setup environment (.env autogeneration with safe defaults)
setup_environment() {
    print_status "Setting up environment (.env generation)..."

    # Do not overwrite existing .env; back up if we need to update
    if [ -f .env ]; then
        cp -f .env .env.bak.$(date +%Y%m%d%H%M%S)
    fi

    # Create .env from example if missing
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            cp env.example .env
        elif [ -f .env.example ]; then
            cp .env.example .env
        else
            print_error "env.example not found; cannot create .env"
            exit 1
        fi
    fi

    # Helper: escape for sed delimiter |
    esc() { printf '%s' "$1" | sed -e 's/[|/\\&]/\\&/g'; }

    # Generate secrets only if placeholders are present
    SECRET_KEY=$(openssl rand -base64 32 2>/dev/null || head -c 32 /dev/urandom | base64)
    JWT_SECRET=$(openssl rand -base64 32 2>/dev/null || head -c 32 /dev/urandom | base64)

    # Replace placeholders safely (idempotent if already replaced)
    if grep -q "your-secret-key-here" .env; then
        sed -i "s|your-secret-key-here|$(esc "$SECRET_KEY")|" .env
    fi
    if grep -q "your-jwt-secret-key" .env; then
        sed -i "s|your-jwt-secret-key|$(esc "$JWT_SECRET")|" .env
    fi
    # Defaults for DB/Redis if placeholders exist
    if grep -q "your-redis-password" .env; then
        sed -i "s|your-redis-password|redis123|" .env
    fi
    if grep -q "your-secure-password" .env; then
        sed -i "s|your-secure-password|workernet123|" .env
    fi

    # Ensure required minimum set if keys were entirely absent
    grep -q "^DJANGO_SECRET_KEY=" .env || echo "DJANGO_SECRET_KEY=$(esc "$SECRET_KEY")" >> .env
    grep -q "^JWT_SECRET=" .env || echo "JWT_SECRET=$(esc "$JWT_SECRET")" >> .env

    print_success "Environment configured (.env generated/updated)"
}

# Function to setup Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    
    print_success "Python virtual environment setup successfully"
}

# Function to setup Node.js environment
setup_nodejs_env() {
    print_status "Setting up Node.js environment..."
    
    cd ../frontend
    npm install
    
    print_success "Node.js environment setup successfully"
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    cd ../backend
    source venv/bin/activate
    python manage.py migrate
    python manage.py collectstatic --noinput
    
    print_success "Database migrations completed successfully"
}

# Function to create superuser
create_superuser() {
    print_status "Creating superuser..."
    
    cd backend
    source venv/bin/activate
    
    # Create superuser non-interactively
    python manage.py shell << EOF
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

# Function to setup systemd services
setup_systemd_services() {
    print_status "Setting up systemd services..."
    
    # Create systemd service for backend
    sudo tee /etc/systemd/system/workernet-backend.service > /dev/null << EOF
[Unit]
Description=WorkerNet Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/workernet-portal/portal-support-ERP-WorkerNet/backend
Environment=PATH=$HOME/workernet-portal/portal-support-ERP-WorkerNet/backend/venv/bin
ExecStart=$HOME/workernet-portal/portal-support-ERP-WorkerNet/backend/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    # Create systemd service for frontend
    sudo tee /etc/systemd/system/workernet-frontend.service > /dev/null << EOF
[Unit]
Description=WorkerNet Frontend
After=network.target workernet-backend.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/workernet-portal/portal-support-ERP-WorkerNet/frontend
Environment=PATH=/usr/bin:/bin
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    sudo systemctl daemon-reload
    # Enable on boot
    sudo systemctl enable workernet-backend || true
    sudo systemctl enable workernet-frontend || true
    
    print_success "Systemd services configured successfully"
}

# Function to setup firewall
setup_firewall() {
    print_status "Setting up firewall..."
    
    sudo ufw enable
    sudo ufw allow 22      # SSH
    sudo ufw allow 80      # HTTP
    sudo ufw allow 443     # HTTPS
    sudo ufw allow 3000    # Frontend
    sudo ufw allow 8000    # API
    sudo ufw allow 9090    # Prometheus
    sudo ufw allow 3001    # Grafana
    
    print_success "Firewall configured successfully"
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    # Start systemd services
    sudo systemctl start workernet-backend
    sudo systemctl start workernet-frontend
    
    print_success "Services started successfully"
}

# Function to show final information
show_final_info() {
    print_success "WorkerNet Portal installation completed successfully!"
    echo
    echo "=== Access Information ==="
    echo "Frontend: http://localhost:3000"
    echo "API: http://localhost:8000"
    echo "API Docs: http://localhost:8000/api/docs"
    echo "Admin Panel: http://localhost:8000/admin"
    echo "Grafana: http://localhost:3001 (admin/admin123)"
    echo "Prometheus: http://localhost:9090"
    echo
    echo "=== Default Credentials ==="
    echo "Admin User: admin"
    echo "Admin Password: admin123"
    echo "Database User: workernet"
    echo "Database Password: workernet123"
    echo "Redis Password: redis123"
    echo
    echo "=== Service Management ==="
    echo "Start services: sudo systemctl start workernet-backend workernet-frontend"
    echo "Stop services: sudo systemctl stop workernet-backend workernet-frontend"
    echo "Restart services: sudo systemctl restart workernet-backend workernet-frontend"
    echo "Check status: sudo systemctl status workernet-backend workernet-frontend"
    echo
    echo "=== Logs ==="
    echo "Backend logs: sudo journalctl -u workernet-backend -f"
    echo "Frontend logs: sudo journalctl -u workernet-frontend -f"
    echo
    echo "=== Next Steps ==="
    echo "1. Access the application at http://localhost:3000"
    echo "2. Login with admin/admin123"
    echo "3. Configure your tenant settings"
    echo "4. Set up monitoring in Grafana"
    echo "5. Configure SSL certificates for production"
    echo
}

# Main installation function
main() {
    print_status "Starting WorkerNet Portal installation for Ubuntu 24.04 LTS..."
    echo
    
    # Check prerequisites
    check_root
    check_ubuntu_version
    check_connectivity
    configure_apt_mirror_if_needed
    
    # Installation steps
    update_system
    install_basic_packages
    install_python
    install_nodejs
    install_postgresql
    install_redis
    install_docker
    install_additional_tools
    verify_dependencies
    
    # Configuration
    configure_postgresql
    configure_redis
    
    # Project setup
    create_project_directory
    clone_repository
    setup_environment
    setup_python_env
    setup_nodejs_env
    run_migrations
    create_superuser
    
    # Service setup
    setup_systemd_services
    setup_firewall
    start_services
    
    # Final information
    show_final_info
}

# Run main function
main "$@"
