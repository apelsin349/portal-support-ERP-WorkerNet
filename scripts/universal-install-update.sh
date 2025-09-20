#!/bin/bash

# Универсальный скрипт установки и обновления WorkerNet Portal для Ubuntu
# Объединяет функциональность установки с нуля и обновления существующей системы
# Версия: 2025-01-27.1

set -e

# Ensure stable working directory to avoid "getcwd() failed" issues
if git rev-parse --show-toplevel >/dev/null 2>&1; then
    export WORKERNET_ROOT="$(git rev-parse --show-toplevel)"
    cd "$WORKERNET_ROOT" || exit 1
else
    cd "$HOME" || exit 1
fi

# Repository configuration (can be overridden via env)
REPO_URL="${WORKERNET_REPO_URL:-}"
REPO_URL_MIRROR="${WORKERNET_REPO_MIRROR:-}"
REPO_BRANCH="${WORKERNET_BRANCH:-main}"

# DEBUG: Показываем начальные значения переменных

# Server configuration (can be overridden via env)
# Автоматическое определение IP сервера для Ubuntu
if command -v hostname >/dev/null 2>&1; then
    SERVER_DOMAIN_OR_IP="${WORKERNET_DOMAIN_OR_IP:-$(hostname -I | awk '{print $1}' | head -1)}"
else
    SERVER_DOMAIN_OR_IP="${WORKERNET_DOMAIN_OR_IP:-$(curl -s ifconfig.me 2>/dev/null || echo 'localhost')}"
fi

# NPM registry and proxy configuration
NPM_REGISTRY_DEFAULT="https://registry.npmmirror.com"
NPM_REGISTRY="${NPM_REGISTRY:-$NPM_REGISTRY_DEFAULT}"

# Installation mode (will be set by check_existing_installation)
INSTALLATION_MODE=""

# Script version
SCRIPT_VERSION="2025-01-27.1"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Без цвета

# Сетевые таймауты
CURL_CONNECT_TIMEOUT=${CURL_CONNECT_TIMEOUT:-3}
CURL_MAX_TIME=${CURL_MAX_TIME:-10}
CURL_OPTS="--fail --silent --show-error --location --connect-timeout $CURL_CONNECT_TIMEOUT --max-time $CURL_MAX_TIME"

# Таймауты APT
APT_HTTP_TIMEOUT=${APT_HTTP_TIMEOUT:-25}
APT_HTTPS_TIMEOUT=${APT_HTTPS_TIMEOUT:-25}

# Параметры по умолчанию для паролей/секретов
WORKERNET_DB_PASS="${WORKERNET_DB_PASS:-workernet123}"
WORKERNET_REDIS_PASS="${WORKERNET_REDIS_PASS:-redis123}"
WORKERNET_ADMIN_PASS="${WORKERNET_ADMIN_PASS:-admin123}"
WORKERNET_POSTGRES_SUPER_PASS="${WORKERNET_POSTGRES_SUPER_PASS:-postgres123}"

# Function to print colored output
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

# Выбор ветки с проверкой реально существующих веток
select_branch_with_check() {
    # Если ветка указана через переменную окружения
    if [ -n "${WORKERNET_BRANCH:-}" ]; then
        SELECTED_BRANCH="${WORKERNET_BRANCH}"
        print_status "Используем ветку из переменной окружения: $SELECTED_BRANCH"
        return 0
    fi
    
    # Если неинтерактивный режим, используем main
    if [[ -n "${CI:-}" || -n "${WORKERNET_NONINTERACTIVE:-}" ]]; then
        SELECTED_BRANCH="main"
        print_status "Неинтерактивный режим: используем ветку main"
        return 0
    fi
    
    # Проверяем доступные ветки в репозитории
    print_status "Проверяем доступные ветки в репозитории..."
    
    AVAILABLE_BRANCHES=()
    CURRENT_BRANCH=""
    
    # Получаем список веток, если мы в git репозитории
    if [ -d ".git" ]; then
        # Обновляем информацию о ветках
        git fetch origin 2>/dev/null || true
        
        # Получаем список удаленных веток
        REMOTE_BRANCHES=($(git branch -r --format='%(refname:short)' 2>/dev/null | grep -v 'HEAD' | sed 's/origin\///' | sort -u))
        
        # Получаем текущую ветку
        CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
        
        # Добавляем реально существующие ветки
        for branch in "${REMOTE_BRANCHES[@]}"; do
            AVAILABLE_BRANCHES+=("$branch")
        done
    fi
    
    # Если нет доступных веток, добавляем популярные по умолчанию
    if [ ${#AVAILABLE_BRANCHES[@]} -eq 0 ]; then
        print_warning "Не удалось получить список веток, используем популярные варианты"
        AVAILABLE_BRANCHES=("main" "develop" "new-frontend" "master")
    fi
    
    echo
    print_status "Доступные ветки в репозитории:"
    for i in "${!AVAILABLE_BRANCHES[@]}"; do
        branch="${AVAILABLE_BRANCHES[$i]}"
        if [ "$branch" = "$CURRENT_BRANCH" ]; then
            echo "$((i+1))) $branch (текущая)"
        else
            echo "$((i+1))) $branch"
        fi
    done
    
    echo "$(( ${#AVAILABLE_BRANCHES[@]} + 1 ))) Указать другую ветку"
    echo "$(( ${#AVAILABLE_BRANCHES[@]} + 2 ))) Использовать main (по умолчанию)"
    echo
    
    while true; do
        read -p "Введите номер (1-$(( ${#AVAILABLE_BRANCHES[@]} + 2 ))) или название ветки: " choice
        
        # Проверяем, не введено ли название ветки напрямую
        if [[ "$choice" =~ ^[a-zA-Z0-9._/-]+$ ]] && [[ ! "$choice" =~ ^[0-9]+$ ]]; then
            SELECTED_BRANCH="$choice"
            print_status "Выбрана ветка: $SELECTED_BRANCH"
            return 0
        fi
        
        case "$choice" in
            [1-9]|[1-9][0-9])
                if [ "$choice" -le "${#AVAILABLE_BRANCHES[@]}" ]; then
                    SELECTED_BRANCH="${AVAILABLE_BRANCHES[$((choice-1))]}"
                    print_status "Выбрана ветка: $SELECTED_BRANCH"
                    break
                elif [ "$choice" -eq "$(( ${#AVAILABLE_BRANCHES[@]} + 1 ))" ]; then
                    read -p "Введите название ветки: " custom_branch
                    if [ -n "$custom_branch" ]; then
                        SELECTED_BRANCH="$custom_branch"
                        print_status "Выбрана ветка: $SELECTED_BRANCH"
                        break
                    else
                        print_error "Название ветки не может быть пустым"
                    fi
                elif [ "$choice" -eq "$(( ${#AVAILABLE_BRANCHES[@]} + 2 ))" ]; then
                    SELECTED_BRANCH="main"
                    print_status "Выбрана ветка: $SELECTED_BRANCH"
                    break
                else
                    print_error "Неверный выбор. Введите номер от 1 до $(( ${#AVAILABLE_BRANCHES[@]} + 2 ))"
                fi
                ;;
            "")
                SELECTED_BRANCH="main"
                print_status "Выбрана ветка по умолчанию: $SELECTED_BRANCH"
                break
                ;;
            *)
                print_error "Неверный выбор. Введите номер или название ветки"
                ;;
        esac
    done
}



ok() {
    echo -e "${GREEN}[OK]${NC} $1"
}

# Простая проверка доступности URL
check_url() {
    curl -sSfI --connect-timeout "$CURL_CONNECT_TIMEOUT" --max-time "$CURL_MAX_TIME" "$1" >/dev/null 2>&1
}

# Самообновление скрипта
self_update_script() {
    if [ "${WORKERNET_SELF_UPDATE:-0}" != "1" ] && [ "${1:-}" != "--self-update" ]; then
        return 0
    fi

    print_status "Проверяем обновления universal-install-update.sh... (self-update)"

    SCRIPT_PATH="$0"
    if command -v readlink >/dev/null 2>&1; then
        SCRIPT_PATH="$(readlink -f "$SCRIPT_PATH" 2>/dev/null || echo "$SCRIPT_PATH")"
    fi

    RAW_BRANCH="${REPO_BRANCH:-main}"
    RAW_URL="${WORKERNET_RAW_SCRIPT_URL:-https://raw.githubusercontent.com/apelsin349/portal-support-ERP-WorkerNet/${RAW_BRANCH}/scripts/universal-install-update.sh}"

    TMP_FILE="/tmp/universal-install-update.sh.$$"
    if curl -fsSL "$RAW_URL" -o "$TMP_FILE"; then
        if cmp -s "$TMP_FILE" "$SCRIPT_PATH"; then
            print_status "Скрипт уже актуален (версия: $SCRIPT_VERSION)"
            rm -f "$TMP_FILE"
        else
            print_status "Найдена новая версия скрипта — обновляем..."
            chmod +x "$TMP_FILE" 2>/dev/null || true
            sudo cp -f "$TMP_FILE" "$SCRIPT_PATH" 2>/dev/null || cp -f "$TMP_FILE" "$SCRIPT_PATH"
            rm -f "$TMP_FILE"
            print_success "Скрипт обновлён. Перезапуск..."
            exec bash "$SCRIPT_PATH" "$@"
        fi
    else
        print_warning "Не удалось загрузить обновление скрипта по адресу: $RAW_URL"
    fi
}

# Проверка наличия команды
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Проверка запуска от root (запрещено)
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "Этот скрипт не должен выполняться от root"
        exit 1
    fi
}

# Проверка версии Ubuntu
check_ubuntu_version() {
    if ! command_exists lsb_release; then
        print_status "Устанавливаем lsb-release..."
        sudo apt -o Acquire::http::Timeout=$APT_HTTP_TIMEOUT -o Acquire::https::Timeout=$APT_HTTPS_TIMEOUT update && sudo apt install -y lsb-release
    fi
    
    UBUNTU_VERSION=$(lsb_release -rs)
    if [[ "$UBUNTU_VERSION" != "24.04" ]]; then
        if [[ -n "${CI:-}" || -n "${WORKERNET_NONINTERACTIVE:-}" || "${WORKERNET_YES:-0}" = "1" ]]; then
            print_warning "Скрипт рассчитан на Ubuntu 24.04 LTS. Обнаружена версия $UBUNTU_VERSION — продолжаем в неинтерактивном режиме"
        else
            print_warning "Скрипт рассчитан на Ubuntu 24.04 LTS. Обнаружена версия $UBUNTU_VERSION"
            read -p "Продолжить в любом случае? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    fi
}

# Проверка доступности внешних репозиториев
check_connectivity() {
    print_status "Проверяем доступность внешних репозиториев..."
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

    $APT_PRIMARY_OK && ok "Основное зеркало APT доступно" || print_warning "Основное зеркало APT недоступно"
    $DOCKER_OK && ok "Репозиторий Docker доступен" || print_warning "Репозиторий Docker недоступен"
    $NODESOURCE_OK && ok "NodeSource доступен" || print_warning "NodeSource недоступен"
    $GITHUB_OK && ok "GitHub доступен" || print_warning "GitHub недоступен"
    $GITHUB_RAW_OK && ok "GitHub RAW доступен" || print_warning "GitHub RAW недоступен"
    $PYPI_OK && ok "PyPI доступен" || print_warning "PyPI недоступен"
}

# Переключение зеркал APT на российские при недоступности основных
configure_apt_mirror_if_needed() {
    if [ "$APT_PRIMARY_OK" = false ]; then
        print_warning "Переключаем зеркала APT на ru.archive.ubuntu.com"
        sudo cp -f /etc/apt/sources.list /etc/apt/sources.list.bak || true
        sudo sed -i 's|http://archive.ubuntu.com/ubuntu/|http://ru.archive.ubuntu.com/ubuntu/|g' /etc/apt/sources.list || true
        sudo sed -i 's|http://security.ubuntu.com/ubuntu|http://ru.archive.ubuntu.com/ubuntu|g' /etc/apt/sources.list || true
    fi
    sudo apt -o Acquire::http::Timeout=$APT_HTTP_TIMEOUT -o Acquire::https::Timeout=$APT_HTTPS_TIMEOUT update || true
}

# Проверка существующей установки
check_existing_installation() {
    print_status "Проверяем существующую установку WorkerNet Portal..."
    
    EXISTING_INSTALLATION=false
    SERVICES_RUNNING=false
    
    # Проверяем наличие сервисов systemd
    if systemctl list-units --type=service | grep -q "workernet-backend\|workernet-frontend"; then
        EXISTING_INSTALLATION=true
        print_warning "Обнаружены существующие сервисы WorkerNet Portal"
        
        # Проверяем статус сервисов
        if systemctl is-active --quiet workernet-backend || systemctl is-active --quiet workernet-frontend; then
            SERVICES_RUNNING=true
            print_warning "Сервисы WorkerNet Portal запущены"
        fi
    fi
    
    # Проверяем наличие директории проекта
    if [ -d "/opt/workernet" ] || [ -d "$HOME/workernet-portal" ] || [ -d "$HOME/portal-support-ERP-WorkerNet" ]; then
        EXISTING_INSTALLATION=true
        print_warning "Обнаружена существующая директория проекта"
    fi
    
    # Проверяем наличие базы данных
    if sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='workernet'" 2>/dev/null | grep -q 1; then
        EXISTING_INSTALLATION=true
        print_warning "Обнаружена база данных workernet"
    fi
    
    if [ "$EXISTING_INSTALLATION" = true ]; then
        echo
        print_status "Обнаружена существующая установка WorkerNet Portal"
        
        # Проверяем неинтерактивный режим
        if [[ -n "${CI:-}" || -n "${WORKERNET_NONINTERACTIVE:-}" || "${WORKERNET_AUTO_UPDATE:-0}" = "1" ]]; then
            print_status "Неинтерактивный режим: автоматически выбираем обновление"
            INSTALLATION_MODE="update"
            return 0
        fi
        
        if [ "$SERVICES_RUNNING" = true ]; then
            print_warning "Сервисы в настоящее время запущены"
            echo
            echo "Выберите действие:"
            echo "1) Обновить существующую установку (рекомендуется)"
            echo "2) Выполнить новую установку (остановит сервисы)"
            echo "3) Выйти"
            echo
            
            while true; do
                read -p "Введите номер (1-3): " choice
                case $choice in
                    1)
                        print_status "Выбрано обновление существующей установки"
                        INSTALLATION_MODE="update"
                        return 0
                        ;;
                    2)
                        print_warning "Выбрана новая установка"
                        echo
                        read -p "Это остановит все сервисы WorkerNet Portal. Продолжить? (y/N): " confirm
                        if [[ $confirm =~ ^[Yy]$ ]]; then
                            print_status "Подтверждена новая установка"
                            INSTALLATION_MODE="fresh"
                            return 0
                        else
                            print_status "Установка отменена пользователем"
                            exit 0
                        fi
                        ;;
                    3)
                        print_status "Установка отменена пользователем"
                        exit 0
                        ;;
                    *)
                        print_error "Неверный выбор. Введите 1, 2 или 3"
                        ;;
                esac
            done
        else
            echo
            echo "Выберите действие:"
            echo "1) Обновить существующую установку"
            echo "2) Выполнить новую установку"
            echo "3) Выйти"
            echo
            
            while true; do
                read -p "Введите номер (1-3): " choice
                case $choice in
                    1)
                        print_status "Выбрано обновление существующей установки"
                        INSTALLATION_MODE="update"
                        return 0
                        ;;
                    2)
                        print_status "Выбрана новая установка"
                        INSTALLATION_MODE="fresh"
                        return 0
                        ;;
                    3)
                        print_status "Установка отменена пользователем"
                        exit 0
                        ;;
                    *)
                        print_error "Неверный выбор. Введите 1, 2 или 3"
                        ;;
                esac
            done
        fi
    else
        print_success "Существующая установка не обнаружена"
        INSTALLATION_MODE="fresh"
    fi
}

# Раннее обновление репозитория проекта
early_update_repository() {
    print_status "Пробуем рано обновить файлы проекта (если репозиторий уже существует)..."
    if ! command -v git >/dev/null 2>&1; then
        print_warning "git не установлен, пропускаем раннее обновление"
        return 0
    fi

    # Кандидаты на корень репозитория
    CANDIDATES=(
        "$(pwd)"
        "$HOME/workernet-portal"
        "$HOME/portal-support-ERP-WorkerNet"
    )

    for dir in "${CANDIDATES[@]}"; do
        if [ -d "$dir/.git" ] && [ -f "$dir/scripts/universal-install-update.sh" ]; then
            print_status "Найден репозиторий: $dir — обновляем..."
            (
                cd "$dir" || exit 0
                git remote -v >/dev/null 2>&1 || exit 0
                # Выбираем origin URL и ветку
                ORIGIN_URL=$(git remote get-url origin 2>/dev/null || echo "")
                [ -n "$REPO_URL" ] && [ "$ORIGIN_URL" != "$REPO_URL" ] && git remote set-url origin "$REPO_URL" || true
                git fetch --all --prune || true
                # Выбор ветки
                BR=${SELECTED_BRANCH:-${REPO_BRANCH:-$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")}}
                BR=${BR:-main}
                git checkout "$BR" 2>/dev/null || git checkout -B "$BR" || true
                git reset --hard "origin/$BR" 2>/dev/null || git reset --hard "origin/main" 2>/dev/null || git reset --hard "origin/master" 2>/dev/null || true
                git submodule update --init --recursive || true
            )
            export WORKERNET_ROOT="$dir"
            print_success "Репозиторий обновлён: $dir"
            return 0
        fi
    done

    print_status "Существующий репозиторий не найден — перейдём к стандартной установке."
}

# Остановка сервисов
stop_services() {
    print_status "Останавливаем сервисы WorkerNet Portal..."
    
    # Останавливаем systemd сервисы
    sudo systemctl stop workernet-backend 2>/dev/null || true
    sudo systemctl stop workernet-frontend 2>/dev/null || true
    
    # Останавливаем Docker контейнеры если они запущены
    if command -v docker >/dev/null 2>&1; then
        if docker ps | grep -q "workernet"; then
            print_status "Останавливаем Docker контейнеры..."
            docker compose down 2>/dev/null || true
        fi
    fi
    
    print_success "Сервисы остановлены"
}

# Обновление системы
update_system() {
    print_status "Обновляем пакеты системы..."
    sudo apt -o Acquire::http::Timeout=$APT_HTTP_TIMEOUT -o Acquire::https::Timeout=$APT_HTTPS_TIMEOUT update && sudo apt upgrade -y
    print_success "Система обновлена"
}

# Установка базовых пакетов
install_basic_packages() {
    print_status "Устанавливаем базовые пакеты..."
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
    print_success "Базовые пакеты установлены"
}

# Установка Python
install_python() {
    print_status "Устанавливаем Python..."

    PYTHON_TARGET=""

    if sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip; then
        PYTHON_TARGET="/usr/bin/python3.12"
    elif sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip; then
        PYTHON_TARGET="/usr/bin/python3.11"
    else
        sudo apt install -y python3 python3-venv python3-dev python3-pip
    fi

    if [[ -n "$PYTHON_TARGET" && -x "$PYTHON_TARGET" ]]; then
        export WORKERNET_PY3="$PYTHON_TARGET"
        print_success "Python установлен ($("$PYTHON_TARGET" -V 2>&1))"
    else
        export WORKERNET_PY3="$(command -v python3)"
        print_success "Python установлен ($(python3 -V 2>&1))"
    fi
}

# Установка Node.js 18
install_nodejs() {
    print_status "Устанавливаем Node.js 18..."

    # 1) NodeSource (обычно быстрее по версиям)
    if curl $CURL_OPTS https://deb.nodesource.com/setup_18.x | sudo -E bash - && \
       sudo apt install -y nodejs; then
        print_success "Node.js 18 установлен (Node: $(node -v 2>/dev/null), NPM: $(npm -v 2>/dev/null))"
        return 0
    fi

    print_warning "NodeSource недоступен. Пробуем репозитории Ubuntu..."
    # Очистка потенциально проблемного источника NodeSource
    if [ -f /etc/apt/sources.list.d/nodesource.list ]; then
        sudo rm -f /etc/apt/sources.list.d/nodesource.list || true
    fi
    sudo apt -o Acquire::http::Timeout=$APT_HTTP_TIMEOUT -o Acquire::https::Timeout=$APT_HTTPS_TIMEOUT update || true
    
    if sudo apt install -y nodejs; then
        if ! command -v npm >/dev/null 2>&1; then
            sudo apt install -y npm || true
        fi
        print_success "Node.js установлен из репозиториев Ubuntu (Node: $(node -v 2>/dev/null), NPM: $(npm -v 2>/dev/null))"
        return 0
    fi

    print_error "Не удалось установить Node.js всеми способами. Проверьте сеть и повторите."
    exit 1
}

# Установка PostgreSQL
install_postgresql() {
    if command -v psql >/dev/null 2>&1; then
        print_status "PostgreSQL уже установлен ($(psql --version 2>/dev/null || echo unknown)) — пропускаем установку"
    else
        print_status "Устанавливаем PostgreSQL..."
        sudo apt install -y postgresql postgresql-contrib postgresql-client
    fi
    sudo systemctl enable postgresql 2>/dev/null || true
    sudo systemctl start postgresql 2>/dev/null || true
    print_success "PostgreSQL готов ($(psql --version 2>/dev/null || echo unknown))"
}

# Установка Redis
install_redis() {
    if command -v redis-server >/dev/null 2>&1; then
        print_status "Redis уже установлен — пропускаем установку"
    else
        print_status "Устанавливаем Redis..."
        sudo apt install -y redis-server
    fi
    sudo systemctl enable redis-server 2>/dev/null || true
    sudo systemctl start redis-server 2>/dev/null || true
    print_success "Redis готов"
}

# Установка Docker
install_docker() {
    if command -v docker >/dev/null 2>&1; then
        print_status "Docker уже установлен — пропускаем установку"
        sudo systemctl enable --now docker || true
        if ! docker compose version >/dev/null 2>&1; then
            sudo apt install -y docker-compose-plugin || true
        fi
        return 0
    fi
    print_status "Устанавливаем Docker..."
    
    # Remove old Docker packages
    sudo apt remove -y docker docker-engine docker.io containerd runc || true
    
    # Install Docker (prefer official repo)
    curl $CURL_OPTS https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg || true
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null || true
    sudo apt -o Acquire::http::Timeout=$APT_HTTP_TIMEOUT -o Acquire::https::Timeout=$APT_HTTPS_TIMEOUT update || true
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin || true
    
    # If official failed, switch cleanly to ubuntu docker.io and standalone compose
    if ! command -v docker >/dev/null 2>&1; then
        print_warning "Официальный репозиторий Docker недоступен, переключаемся на docker.io"
        sudo apt remove -y docker-ce docker-ce-cli containerd.io docker-compose-plugin || true
        sudo apt install -y docker.io docker-compose || true
        if ! grep -q "alias docker-compose='docker compose'" "$HOME/.bashrc" 2>/dev/null; then
            echo "alias docker-compose='docker compose'" >> "$HOME/.bashrc"
        fi
    else
        sudo apt install -y docker-compose-plugin || true
    fi

    # Ensure Docker daemon enabled on boot
    sudo systemctl enable --now docker || true

    # Add user to docker group
    sudo usermod -aG docker $USER || true
    print_warning "Чтобы использовать docker без sudo, выйдите и войдите в систему заново."
    print_success "Docker установлен"
}


# Клонирование/обновление репозитория
clone_repository() {
    print_status "Клонируем/обновляем репозиторий..."

    # Если WORKERNET_ROOT уже установлен (например, early_update_repository), используем его
    if [ -n "${WORKERNET_ROOT:-}" ] && [ -d "$WORKERNET_ROOT" ]; then
        print_success "Используем уже установленный корень проекта: $WORKERNET_ROOT"
        cd "$WORKERNET_ROOT"
        return 0
    fi

    # If already at repo root, skip clone and just set WORKERNET_ROOT
    if [ -d .git ] && [ -d backend ] && [ -f scripts/universal-install-update.sh ]; then
        export WORKERNET_ROOT="$(pwd)"
        print_success "Используем существующий репозиторий: $WORKERNET_ROOT"
        return 0
    fi

    # Create directory if missing
    if [ ! -d "portal-support-ERP-WorkerNet" ]; then
        if git clone "$REPO_URL" portal-support-ERP-WorkerNet; then
            :
        elif [ -n "$REPO_URL_MIRROR" ]; then
            print_warning "Основной репозиторий недоступен, пробуем зеркало: $REPO_URL_MIRROR"
            git clone "$REPO_URL_MIRROR" portal-support-ERP-WorkerNet
        else
            print_error "Не удалось клонировать репозиторий"
            exit 1
        fi
    fi

    cd portal-support-ERP-WorkerNet
    export WORKERNET_ROOT="$(pwd)"

    # Гарантируем корректный origin (предпочитаем основной URL)
    CURRENT_URL=$(git remote get-url origin 2>/dev/null || echo "")
    if [ -n "$REPO_URL" ] && [ "$CURRENT_URL" != "$REPO_URL" ]; then
        git remote set-url origin "$REPO_URL" || true
    fi

    # Обновляем ссылки и жёстко синхронизируемся с выбранной веткой
    git fetch --all --prune || true
    
    # Очищаем название ветки от лишних пробелов
    SELECTED_BRANCH=$(echo "$SELECTED_BRANCH" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
    
    # Проверяем, существует ли выбранная ветка на удаленном репозитории
    if ! git show-ref --verify --quiet "refs/remotes/origin/$SELECTED_BRANCH"; then
        print_error "Ветка '$SELECTED_BRANCH' не найдена на удаленном репозитории"
        print_status "Доступные ветки:"
        git branch -r | grep -v HEAD | sed 's/origin\///' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | sort -u | sed 's/^/  - /'
        print_status "Используем ветку main по умолчанию"
        SELECTED_BRANCH="main"
    fi

    git checkout "$SELECTED_BRANCH" 2>/dev/null || git checkout -B "$SELECTED_BRANCH" "origin/$SELECTED_BRANCH" 2>/dev/null || true
    git reset --hard "origin/$SELECTED_BRANCH" 2>/dev/null || true
    git submodule update --init --recursive || true

    print_success "Репозиторий актуален (ветка: $SELECTED_BRANCH)"

    # Проверяем наличие фронтенда, если он обязателен
    if [ "${WORKERNET_REQUIRE_FRONTEND:-true}" = "true" ]; then
        if [ ! -d "frontend" ] || [ ! -f "frontend/package.json" ]; then
            print_error "Требуемый каталог фронтенда отсутствует: $(pwd)/frontend"
            echo "Подсказка: убедитесь, что вы клонировали актуальную ветку с каталогом 'frontend'"
            echo "Либо укажите WORKERNET_REQUIRE_FRONTEND=false для пропуска (не рекомендуется)."
            exit 1
        fi
    fi
}

# Настройка файрвола Ubuntu
setup_firewall() {
    print_status "Настраиваем файрвол Ubuntu (UFW)..."
    
    # Проверяем, установлен ли UFW
    if ! command -v ufw >/dev/null 2>&1; then
        print_warning "UFW не установлен, пропускаем настройку файрвола"
        return 0
    fi
    
    # Порты для WorkerNet Portal
    PORTS=(
        "3000/tcp"  # Frontend
        "8000/tcp"  # API
        "3001/tcp"  # Grafana
        "9090/tcp"  # Prometheus
        "5555/tcp"  # Celery Flower
    )
    
    # Открываем порты
    for port in "${PORTS[@]}"; do
        if ! ufw status | grep -q "$port"; then
            print_status "Открываем порт $port..."
            ufw allow "$port" 2>/dev/null || true
        else
            print_status "Порт $port уже открыт"
        fi
    done
    
    # Включаем UFW если он отключен
    if ! ufw status | grep -q "Status: active"; then
        print_status "Включаем UFW..."
        ufw --force enable 2>/dev/null || true
    fi
    
    print_success "Файрвол настроен"
}

# Показ информации о доступе к серверу
show_access_info() {
    print_status "Информация о доступе к WorkerNet Portal:"
    echo
    echo "🌐 Доступ к приложению:"
    echo "   Frontend (PWA):    http://${SERVER_DOMAIN_OR_IP}:3000"
    echo "   API:               http://${SERVER_DOMAIN_OR_IP}:8000"
    echo "   Админ-панель:      http://${SERVER_DOMAIN_OR_IP}:8000/admin"
    echo "   API документация:  http://${SERVER_DOMAIN_OR_IP}:8000/api/docs"
    echo
    echo "📊 Мониторинг:"
    echo "   Grafana:           http://${SERVER_DOMAIN_OR_IP}:3001"
    echo "   Prometheus:        http://${SERVER_DOMAIN_OR_IP}:9090"
    echo "   Celery Flower:     http://${SERVER_DOMAIN_OR_IP}:5555"
    echo
    echo "🔑 Логин: admin | Пароль: admin123"
    echo
    echo "📝 Полезные команды:"
    echo "   Статус сервисов:   sudo systemctl status workernet-backend workernet-frontend"
    echo "   Логи бэкенда:      sudo journalctl -u workernet-backend -f"
    echo "   Логи фронтенда:    sudo journalctl -u workernet-frontend -f"
    echo "   Перезапуск:        sudo systemctl restart workernet-backend workernet-frontend"
    echo
}

# Настройка окружения (.env с автогенерацией безопасных значений)
setup_environment() {
    print_status "Настраиваем окружение (.env с автогенерацией)..."

    # Do not overwrite existing .env; back up if we need to update
    if [ -f .env ]; then
        cp -f .env .env.bak.$(date +%Y%m%d%H%M%S)
    fi

    # Create .env from example if missing or if it contains old paths
    if [ ! -f .env ] || grep -q "/app/static\|/app/media" .env; then
        if [ -f env.example ]; then
            cp env.example .env
            print_status "Обновлен .env из env.example (исправлены пути для статических файлов)"
        elif [ -f .env.example ]; then
            cp .env.example .env
            print_status "Обновлен .env из .env.example (исправлены пути для статических файлов)"
        else
            print_error "env.example не найден; невозможно создать .env"
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
        sed -i "s|your-redis-password|${WORKERNET_REDIS_PASS}|" .env
    fi
    if grep -q "your-secure-password" .env; then
        sed -i "s|your-secure-password|${WORKERNET_DB_PASS}|" .env
    fi
    # Replace password placeholder in DATABASE_URL
    if grep -q "password" .env; then
        sed -i "s|password|${WORKERNET_DB_PASS}|" .env
    fi
    # Replace database name if needed
    if grep -q "worker_net" .env; then
        sed -i "s|worker_net|workernet|g" .env
    fi
    
    # Fix static files paths to use relative paths
    if grep -q "/app/static" .env; then
        sed -i "s|/app/static|./staticfiles|g" .env
    fi
    if grep -q "/app/media" .env; then
        sed -i "s|/app/media|./media|g" .env
    fi

    # Update DOMAIN_OR_IP with server IP
    if grep -q "^DOMAIN_OR_IP=" .env; then
        sed -i "s|^DOMAIN_OR_IP=.*|DOMAIN_OR_IP=${SERVER_DOMAIN_OR_IP}|" .env
    else
        echo "DOMAIN_OR_IP=${SERVER_DOMAIN_OR_IP}" >> .env
    fi

    # Update ALLOWED_HOSTS with server IP
    if grep -q "^ALLOWED_HOSTS=" .env; then
        sed -i "s|^ALLOWED_HOSTS=.*|ALLOWED_HOSTS=${SERVER_DOMAIN_OR_IP},127.0.0.1,0.0.0.0,localhost|" .env
    else
        echo "ALLOWED_HOSTS=${SERVER_DOMAIN_OR_IP},127.0.0.1,0.0.0.0,localhost" >> .env
    fi

    # Update CORS_ALLOWED_ORIGINS with server IP
    if grep -q "^CORS_ALLOWED_ORIGINS=" .env; then
        sed -i "s|^CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=http://${SERVER_DOMAIN_OR_IP}:3000,http://127.0.0.1:3000,http://localhost:3000|" .env
    else
        echo "CORS_ALLOWED_ORIGINS=http://${SERVER_DOMAIN_OR_IP}:3000,http://127.0.0.1:3000,http://localhost:3000" >> .env
    fi

    # Update CSRF_TRUSTED_ORIGINS with server IP
    if grep -q "^CSRF_TRUSTED_ORIGINS=" .env; then
        sed -i "s|^CSRF_TRUSTED_ORIGINS=.*|CSRF_TRUSTED_ORIGINS=http://${SERVER_DOMAIN_OR_IP}:3000,http://127.0.0.1:3000,http://localhost:3000|" .env
    else
        echo "CSRF_TRUSTED_ORIGINS=http://${SERVER_DOMAIN_OR_IP}:3000,http://127.0.0.1:3000,http://localhost:3000" >> .env
    fi

    print_status "Обновлен DOMAIN_OR_IP и ALLOWED_HOSTS для IP: ${SERVER_DOMAIN_OR_IP}"

    # Ensure required minimum set if keys were entirely absent or contain placeholders
    if ! grep -q "^DJANGO_SECRET_KEY=" .env || grep -q "your-secret-key-here" .env; then
        grep -q "^DJANGO_SECRET_KEY=" .env && sed -i "s|^DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=$(esc "$SECRET_KEY")|" .env || echo "DJANGO_SECRET_KEY=$(esc "$SECRET_KEY")" >> .env
    fi
    if ! grep -q "^JWT_SECRET=" .env || grep -q "your-jwt-secret-key" .env; then
        grep -q "^JWT_SECRET=" .env && sed -i "s|^JWT_SECRET=.*|JWT_SECRET=$(esc "$JWT_SECRET")|" .env || echo "JWT_SECRET=$(esc "$JWT_SECRET")" >> .env
    fi
    # Для совместимости с настройками Django/DRF SimpleJWT
    if ! grep -q "^SECRET_KEY=" .env || grep -q "your-secret-key-here" .env || grep -q "^SECRET_KEY=$" .env; then
        grep -q "^SECRET_KEY=" .env && sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$(esc "$SECRET_KEY")|" .env || echo "SECRET_KEY=$(esc "$SECRET_KEY")" >> .env
    fi
    if ! grep -q "^JWT_SECRET_KEY=" .env || grep -q "your-jwt-secret-key" .env || grep -q "^JWT_SECRET_KEY=$" .env; then
        grep -q "^JWT_SECRET_KEY=" .env && sed -i "s|^JWT_SECRET_KEY=.*|JWT_SECRET_KEY=$(esc "$JWT_SECRET")|" .env || echo "JWT_SECRET_KEY=$(esc "$JWT_SECRET")" >> .env
    fi

    # Дополнительная проверка: принудительно устанавливаем SECRET_KEY если он пустой или содержит плейсхолдеры
    if grep -q "^SECRET_KEY=$" .env || grep -q "your-secret-key-here" .env || ! grep -q "^SECRET_KEY=" .env; then
        sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$(esc "$SECRET_KEY")|" .env || echo "SECRET_KEY=$(esc "$SECRET_KEY")" >> .env
        print_status "Установлен SECRET_KEY"
    fi
    if grep -q "^JWT_SECRET_KEY=$" .env || grep -q "your-jwt-secret-key" .env || ! grep -q "^JWT_SECRET_KEY=" .env; then
        sed -i "s|^JWT_SECRET_KEY=.*|JWT_SECRET_KEY=$(esc "$JWT_SECRET")|" .env || echo "JWT_SECRET_KEY=$(esc "$JWT_SECRET")" >> .env
        print_status "Установлен JWT_SECRET_KEY"
    fi

    # Продублируем .env в backend/, чтобы Django гарантированно его увидел
    if [ -d backend ]; then
        cp -f .env backend/.env || true
    fi

    print_success ".env создан/обновлён"
}

# Настройка виртуального окружения Python
setup_python_env() {
    print_status "Настраиваем виртуальное окружение Python..."
    
    # Проверяем существование каталога backend
    if [ ! -d "$WORKERNET_ROOT/backend" ]; then
        print_error "Каталог backend не найден: $WORKERNET_ROOT/backend"
        exit 1
    fi
    
    cd "$WORKERNET_ROOT/backend"
    "${WORKERNET_PY3:-python3}" -m venv venv
    source venv/bin/activate
    python -m pip install -U pip setuptools wheel
    # Install from repo root to avoid CWD issues
    if [ -f "$WORKERNET_ROOT/requirements.txt" ]; then
        python -m pip install -r "$WORKERNET_ROOT/requirements.txt"
    else
        print_error "Файл requirements.txt не найден: $WORKERNET_ROOT/requirements.txt"
        exit 1
    fi
    if [ -f "$WORKERNET_ROOT/requirements-dev.txt" ]; then
        python -m pip install -r "$WORKERNET_ROOT/requirements-dev.txt"
    fi
    # Страховка: принудительная установка django-filter (если файл зависимостей локально устарел)
    python -m pip install "django-filter==23.5" || true
    
    print_success "Виртуальное окружение Python настроено"
}

# Настройка окружения Node.js
setup_nodejs_env() {
    print_status "Настраиваем окружение Node.js..."
    
    # Ищем каталог фронтенда максимально устойчиво
    FRONTEND_DIR=""
    
    print_status "Поиск каталога фронтенда..."
    print_status "WORKERNET_ROOT: ${WORKERNET_ROOT:-не определен}"
    
    if [ -n "${WORKERNET_ROOT:-}" ]; then
        # Если WORKERNET_ROOT определен, используем его
        FRONTEND_DIR="${WORKERNET_ROOT}/frontend"
        print_status "Проверяем: $FRONTEND_DIR"
        if [ ! -f "$FRONTEND_DIR/package.json" ]; then
            print_warning "Фронтенд не найден в $FRONTEND_DIR, пробуем другие варианты..."
            FRONTEND_DIR=""
        else
            print_status "Найден фронтенд в: $FRONTEND_DIR"
        fi
    fi
    
    # Fallback логика для случаев, когда WORKERNET_ROOT не определен или фронтенд не найден
    if [ -z "$FRONTEND_DIR" ]; then
        print_status "Пробуем fallback варианты..."
        CANDIDATES=(
            "../frontend"
            "./frontend"
            "../../frontend"
        )
        # Попытка извлечь корень git-репозитория и добавить как кандидат
        GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || true)
        if [ -n "$GIT_ROOT" ] && [ -d "$GIT_ROOT/frontend" ]; then
            CANDIDATES+=("$GIT_ROOT/frontend")
            print_status "Добавлен git-корень: $GIT_ROOT/frontend"
        fi
        
        for p in "${CANDIDATES[@]}"; do
            print_status "Проверяем: $p"
            if [ -f "$p/package.json" ]; then 
                FRONTEND_DIR="$p"
                print_status "Найден фронтенд в: $FRONTEND_DIR"
                break
            fi
        done
    fi

    # Если не нашли — пробуем поискать в $HOME (ограничим глубину для скорости)
    if [ -z "$FRONTEND_DIR" ]; then
        print_status "Поиск в $HOME..."
        FOUND=$(find "$HOME" -maxdepth 6 -type f -name package.json -path "*/frontend/package.json" -print -quit 2>/dev/null || true)
        if [ -n "$FOUND" ]; then
            FRONTEND_DIR=$(dirname "$FOUND")
            print_status "Найден фронтенд в: $FRONTEND_DIR"
        else
            print_status "Фронтенд не найден в $HOME"
        fi
    fi

    if [ -z "$FRONTEND_DIR" ]; then
        if [ "${WORKERNET_REQUIRE_FRONTEND:-true}" = "true" ]; then
            print_error "Требуемый каталог фронтенда не найден."
            echo "Подсказка: ожидается каталог 'frontend' с package.json в $WORKERNET_ROOT"
            echo "Проверьте, что репозиторий клонирован и структура каталогов стандартная."
            echo "Либо укажите WORKERNET_REQUIRE_FRONTEND=false для пропуска (не рекомендуется)."
            exit 1
        else
            print_warning "Каталог фронтенда не найден. Пропускаем установку npm-зависимостей."
            echo "Подсказка: ожидается каталог 'frontend' с package.json."
            return 0
        fi
    fi

    # Проверяем существование каталога frontend
    if [ ! -d "$FRONTEND_DIR" ]; then
        print_error "Каталог frontend не найден: $FRONTEND_DIR"
        return 1
    fi

    cd "$FRONTEND_DIR"
    # Базовые настройки npm
    npm config set fund false >/dev/null 2>&1 || true
    npm config set audit false >/dev/null 2>&1 || true
    npm config set progress false >/dev/null 2>&1 || true
    npm config set fetch-retries 5 >/dev/null 2>&1 || true
    npm config set fetch-retry-factor 2 >/dev/null 2>&1 || true
    npm config set fetch-retry-maxtimeout 300000 >/dev/null 2>&1 || true
    npm config set fetch-timeout 300000 >/dev/null 2>&1 || true
    npm config set maxsockets 3 >/dev/null 2>&1 || true

    # Автоподхват системного корневого хранилища сертификатов (для корпоративных прокси/MITM)
    if [ -f /etc/ssl/certs/ca-certificates.crt ]; then
        npm config set cafile /etc/ssl/certs/ca-certificates.crt >/dev/null 2>&1 || true
        npm config set strict-ssl true >/dev/null 2>&1 || true
    fi

    # Прокси из переменных окружения, если заданы
    if [ -n "${HTTPS_PROXY:-${https_proxy:-}}" ]; then
        npm config set https-proxy "${HTTPS_PROXY:-${https_proxy}}" >/dev/null 2>&1 || true
    fi
    if [ -n "${HTTP_PROXY:-${http_proxy:-}}" ]; then
        npm config set proxy "${HTTP_PROXY:-${http_proxy}}" >/dev/null 2>&1 || true
    fi

    # АГРЕССИВНАЯ очистка кэша при проблемах с integrity
    print_status "Проверяем и очищаем npm кэш..."
    npm cache verify >/dev/null 2>&1 || {
        print_warning "Кэш npm поврежден, выполняем агрессивную очистку..."
        npm cache clean --force >/dev/null 2>&1 || true
        rm -rf ~/.npm >/dev/null 2>&1 || true
        rm -rf /tmp/npm-* >/dev/null 2>&1 || true
    }

    # Удаляем проблемные lock файлы
    if [ -f package-lock.json ]; then
        print_status "Проверяем package-lock.json на синхронизацию..."
        # Простая проверка - если файл слишком маленький, он поврежден
        if [ $(wc -c < package-lock.json) -lt 1000 ]; then
            print_warning "package-lock.json поврежден, удаляем..."
            rm -f package-lock.json
        fi
    fi

    # Последовательно пробуем реестры с повторами
    REGISTRIES=(
        "https://registry.npmjs.org"
        "https://registry.npmmirror.com"
    )

    INSTALL_OK=false
    for REG in "${REGISTRIES[@]}"; do
        npm config set registry "$REG" >/dev/null 2>&1 || true
        
        # Стратегия 1: npm install без lock файла
        if [ ! -f package-lock.json ]; then
            for ATTEMPT in 1 2 3; do
                echo "Попытка $ATTEMPT с реестром: $REG (npm install без lock)"
                if npm install --omit=optional --no-audit --no-fund; then
                    INSTALL_OK=true
                    break
                fi
                sleep $((ATTEMPT * 2))
            done
        fi
        
        # Стратегия 2: npm install с принудительным обновлением
        if [ "$INSTALL_OK" != true ]; then
            for ATTEMPT in 1 2 3; do
                echo "Попытка $ATTEMPT с реестром: $REG (npm install принудительно)"
                if npm install --omit=optional --no-audit --no-fund --force; then
                    INSTALL_OK=true
                    break
                fi
                sleep $((ATTEMPT * 2))
            done
        fi
        
        # Стратегия 3: npm ci (только если lock файл существует и синхронизирован)
        if [ "$INSTALL_OK" != true ] && [ -f package-lock.json ]; then
            for ATTEMPT in 1 2 3; do
                echo "Попытка $ATTEMPT с реестром: $REG (npm ci)"
                if npm ci --omit=optional --no-audit --no-fund; then
                    INSTALL_OK=true
                    break
                fi
                sleep $((ATTEMPT * 2))
            done
        fi
        
        # Стратегия 4: Минимальная установка без lock файла
        if [ "$INSTALL_OK" != true ]; then
            print_warning "Все стратегии не сработали, пробуем минимальную установку..."
            rm -f package-lock.json >/dev/null 2>&1 || true
            rm -rf node_modules >/dev/null 2>&1 || true
            if npm install --omit=optional --no-audit --no-fund --no-package-lock; then
                INSTALL_OK=true
            fi
        fi
        
        [ "$INSTALL_OK" = true ] && break
    done

    if [ "$INSTALL_OK" != true ]; then
        print_warning "npm install не удалось после нескольких попыток. Проверьте сеть/прокси."
    fi
    
    print_success "Окружение Node.js настроено"
}

# Сборка фронтенда с PWA
build_frontend() {
    if [ -z "$FRONTEND_DIR" ]; then
        print_warning "Каталог фронтенда не найден — пропускаем сборку"
        return 0
    fi

    print_status "Собираем фронтенд с PWA поддержкой..."
    
    cd "$FRONTEND_DIR"
    
    # Устанавливаем зависимости для генерации иконок
    if [ -f "scripts/install-icon-deps.js" ]; then
        print_status "Устанавливаем зависимости для генерации иконок..."
        node scripts/install-icon-deps.js --verbose || print_warning "Не удалось установить зависимости для иконок"
    fi
    
    # Генерируем иконки для PWA
    if [ -f "scripts/generate-icons.js" ]; then
        print_status "Генерируем иконки для PWA..."
        node scripts/generate-icons.js || print_warning "Не удалось сгенерировать иконки PWA"
    fi
    
    # Собираем фронтенд для production
    print_status "Собираем фронтенд для production..."
    if npm run build; then
        print_success "Фронтенд собран успешно"
    else
        print_warning "Ошибка сборки фронтенда — продолжаем без сборки"
    fi
    
    print_success "Сборка фронтенда завершена"
}

# Настройка базы данных
setup_database() {
    print_status "Настраиваем базу данных PostgreSQL..."
    
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
    
    # Создаем пользователя и базу данных (идемпотентно)
    DB_USER="workernet"
    DB_PASSWORD="workernet123"
    DB_NAME="workernet"
    
    # Создаем пользователя (идемпотентно)
    print_status "Создаем/обновляем пользователя базы данных: $DB_USER"
    if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
        sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD' CREATEDB;"
        print_success "Пользователь $DB_USER создан"
    else
        sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD' CREATEDB;" || true
        print_status "Пользователь $DB_USER уже существует, пароль обновлен"
    fi
    
    # Создаем базу данных (идемпотентно)
    print_status "Создаем базу данных: $DB_NAME"
    if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
        sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
        print_success "База данных $DB_NAME создана"
    else
        print_status "База данных $DB_NAME уже существует"
    fi
    
    # Настраиваем права доступа (идемпотентно)
    print_status "Настраиваем права доступа..."
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" || true
    sudo -u postgres psql -c "ALTER DATABASE $DB_NAME OWNER TO $DB_USER;" || true
    
    # Проверяем подключение
    print_status "Проверяем подключение к базе данных..."
    if PGPASSWORD="$DB_PASSWORD" psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; then
        print_success "Подключение к базе данных успешно!"
    else
        print_warning "Не удается подключиться через localhost, пробуем 127.0.0.1..."
        if PGPASSWORD="$DB_PASSWORD" psql -h 127.0.0.1 -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; then
            print_success "Подключение через 127.0.0.1 успешно!"
        else
            print_error "Не удается подключиться к базе данных"
            exit 1
        fi
    fi
    
    print_success "База данных настроена"
}

# Настройка Redis
setup_redis() {
    print_status "Настраиваем Redis..."
    
    # Проверяем, запущен ли Redis
    if ! systemctl is-active --quiet redis-server; then
        print_status "Запускаем Redis..."
        sudo systemctl start redis-server
        sudo systemctl enable redis-server
    fi
    
    # Настраиваем пароль для Redis
    REDIS_PASSWORD="redis123"
    
    # Проверяем, существует ли файл конфигурации Redis
    if [ -f "/etc/redis/redis.conf" ]; then
        if ! sudo grep -q "requirepass" /etc/redis/redis.conf 2>/dev/null; then
            echo "requirepass $REDIS_PASSWORD" | sudo tee -a /etc/redis/redis.conf >/dev/null 2>&1
            sudo systemctl restart redis-server 2>/dev/null || true
        fi
    else
        print_warning "Файл конфигурации Redis не найден: /etc/redis/redis.conf"
        print_status "Пропускаем настройку пароля Redis"
    fi
    
    print_success "Redis настроен"
}

# Применение миграций базы данных
run_migrations() {
    print_status "Выполняем миграции базы данных..."
    
    # Проверяем существование каталога backend
    if [ ! -d "$WORKERNET_ROOT/backend" ]; then
        print_error "Каталог backend не найден: $WORKERNET_ROOT/backend"
        exit 1
    fi
    
    cd "$WORKERNET_ROOT/backend"
    source venv/bin/activate
    
    # Создаем/обновляем backend/.env с корректными значениями
    if [ ! -f ".env" ]; then
        print_status "Создаем файл .env..."
        cat > .env << EOF
SECRET_KEY=workernet-secret-key-2024-development-only
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
ALLOWED_HOSTS_EXTRA=${WORKERNET_ALLOWED_HOSTS_EXTRA:-}
DATABASE_URL=postgresql://workernet:${WORKERNET_DB_PASS}@localhost:5432/workernet
REDIS_URL=redis://:${WORKERNET_REDIS_PASS}@localhost:6379/0
JWT_SECRET_KEY=workernet-jwt-secret-key-2024-development-only
EOF
    else
        # Идемпотентно правим ключевые параметры
        sed -i "s/^DEBUG=.*/DEBUG=False/" .env || true
        grep -q "^ALLOWED_HOSTS=" .env || echo "ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0" >> .env
        if grep -q "^ALLOWED_HOSTS_EXTRA=" .env; then
            sed -i "s/^ALLOWED_HOSTS_EXTRA=.*/ALLOWED_HOSTS_EXTRA=${WORKERNET_ALLOWED_HOSTS_EXTRA:-}/" .env || true
        else
            echo "ALLOWED_HOSTS_EXTRA=${WORKERNET_ALLOWED_HOSTS_EXTRA:-}" >> .env
        fi
        grep -q "^DATABASE_URL=" .env || echo "DATABASE_URL=postgresql://workernet:${WORKERNET_DB_PASS}@localhost:5432/workernet" >> .env
    fi
    
    # Проверяем и исправляем базу данных перед миграциями
    print_status "Проверяем подключение к базе данных..."
    if ! python manage.py check --database default >/dev/null 2>&1; then
        print_error "Django не может подключиться к базе данных!"
        print_status "Исправляем проблему с базой данных..."
        
        # Используем функцию проверки и исправления
        if ! check_and_fix_database; then
            print_error "Не удалось исправить проблему с базой данных!"
            exit 1
        fi
    else
        print_success "Django может подключиться к базе данных"
    fi
    
    # Создаем миграции если их нет
    print_status "Создаем миграции Django..."
    python manage.py makemigrations --noinput || true
    
    # Выполняем миграции
    print_status "Выполняем миграции Django..."
    python manage.py migrate --fake-initial
    
    print_status "Создаем папки для статических файлов..."
    mkdir -p staticfiles media || true
    
    print_status "Собираем статические файлы..."
    python manage.py collectstatic --noinput
    
    print_success "Миграции выполнены"
}

# Создание суперпользователя
create_superuser() {
    print_status "Создаём суперпользователя..."
    
    # Проверяем существование каталога backend
    if [ ! -d "$WORKERNET_ROOT/backend" ]; then
        print_error "Каталог backend не найден: $WORKERNET_ROOT/backend"
        exit 1
    fi
    
    cd "$WORKERNET_ROOT/backend"
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
        password='${WORKERNET_ADMIN_PASS}',
        tenant=tenant
    )
    print('Superuser created: admin/${WORKERNET_ADMIN_PASS}')
else:
    print('Superuser already exists')
EOF
    
    print_success "Суперпользователь создан"
}

# Настройка системных сервисов (systemd)
setup_systemd_services() {
    print_status "Настраиваем системные сервисы (systemd)..."
    
    # Create systemd service for backend
    sudo tee /etc/systemd/system/workernet-backend.service > /dev/null << EOF
[Unit]
Description=WorkerNet Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORKERNET_ROOT/backend
Environment=PATH=$WORKERNET_ROOT/backend/venv/bin:/usr/bin:/bin
Environment=DJANGO_SETTINGS_MODULE=config.settings
ExecStart=$WORKERNET_ROOT/backend/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=5

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
WorkingDirectory=$WORKERNET_ROOT/frontend
Environment=PATH=/usr/bin:/bin:/usr/local/bin
Environment=NODE_ENV=production
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    # Проверяем, что виртуальное окружение backend существует
    if [ ! -f "$WORKERNET_ROOT/backend/venv/bin/python" ]; then
        print_error "Виртуальное окружение backend не найдено: $WORKERNET_ROOT/backend/venv/bin/python"
        print_status "Создаем виртуальное окружение..."
        cd "$WORKERNET_ROOT/backend"
        python3 -m venv venv
        source venv/bin/activate
        pip install -r "$WORKERNET_ROOT/requirements.txt" || true
    fi
    
    # Reload systemd
    sudo systemctl daemon-reload
    # Enable on boot
    sudo systemctl enable workernet-backend || true
    sudo systemctl enable workernet-frontend || true
    
    # Проверяем, что зависимости frontend установлены
    if [ -d "$WORKERNET_ROOT/frontend" ]; then
        cd "$WORKERNET_ROOT/frontend"
        if [ ! -d "node_modules" ] || [ ! -f "node_modules/.package-lock.json" ]; then
            print_status "Устанавливаем зависимости frontend перед запуском сервиса..."
            npm install --omit=optional --no-audit --no-fund || true
        fi
    fi
    
    print_success "Сервисы systemd настроены"
}

# Настройка файрвола
setup_firewall() {
    print_status "Настраиваем файрвол..."
    
    sudo ufw --force enable
    sudo ufw allow 22      # SSH
    sudo ufw allow 80      # HTTP
    sudo ufw allow 443     # HTTPS
    sudo ufw allow 3000    # Frontend
    sudo ufw allow 8000    # API
    
    print_success "Файрвол настроен"
}

# Запуск сервисов
start_services() {
    print_status "Запускаем сервисы..."
    
    # Start systemd services
    sudo systemctl start workernet-backend
    sudo systemctl start workernet-frontend
    
    print_success "Сервисы запущены"
}

# Финальная информация
show_final_info() {
    print_success "Установка WorkerNet Portal успешно завершена!"
    echo
    echo "=== Доступ к сервисам ==="
    echo "Фронтенд: http://${SERVER_DOMAIN_OR_IP}:3000"
    echo "API: http://${SERVER_DOMAIN_OR_IP}:8000"
    echo "API документация: http://${SERVER_DOMAIN_OR_IP}:8000/api/docs"
    echo "Админ‑панель: http://${SERVER_DOMAIN_OR_IP}:8000/admin"
    echo
    echo "⚠️  Для доступа извне замените ${SERVER_DOMAIN_OR_IP} на ваш домен или IP-адрес"
    echo
    echo "=== Данные по умолчанию ==="
    echo "Админ‑пользователь: admin"
    echo "Пароль администратора: ${WORKERNET_ADMIN_PASS}"
    echo "Пользователь БД: workernet"
    echo "Пароль БД: ${WORKERNET_DB_PASS}"
    echo "Пароль Redis: ${WORKERNET_REDIS_PASS}"
    echo
    echo "=== Управление сервисами ==="
    echo "Старт: sudo systemctl start workernet-backend workernet-frontend"
    echo "Стоп: sudo systemctl stop workernet-backend workernet-frontend"
    echo "Перезапуск: sudo systemctl restart workernet-backend workernet-frontend"
    echo "Статус: sudo systemctl status workernet-backend workernet-frontend"
    echo
    echo "=== Логи ==="
    echo "Бэкенд: sudo journalctl -u workernet-backend -f"
    echo "Фронтенд: sudo journalctl -u workernet-frontend -f"
    echo
    echo "=== Проверка сервисов ==="
    echo "Список сервисов: sudo systemctl list-units --type=service | grep workernet"
    echo "Статус всех: sudo systemctl status workernet-backend workernet-frontend"
    echo
    echo "=== Следующие шаги ==="
    echo "1. Откройте приложение: http://${SERVER_DOMAIN_OR_IP}:3000"
    echo "2. Войдите: admin/admin123"
    echo "3. Настройте параметры тенанта"
    echo "4. Настройте SSL‑сертификаты для продакшена"
    echo
}

# Обновление существующей установки
update_installation() {
    print_status "Обновление существующей установки WorkerNet Portal..."
    
    # Останавливаем сервисы для обновления
    stop_services
    
    # Обновляем код из репозитория
    if [ -d "$WORKERNET_ROOT" ]; then
        print_status "Обновляем код из репозитория..."
        cd "$WORKERNET_ROOT"
        
        # Сохраняем локальные изменения
        git stash push -m "Auto-stash before update $(date)" 2>/dev/null || true
        
        # Обновляем код
        git fetch --all --prune
        git reset --hard "origin/main" 2>/dev/null || git reset --hard "origin/master" 2>/dev/null || true
        git submodule update --init --recursive 2>/dev/null || true
        
        print_success "Код обновлен"
    fi
    
    # Обновляем зависимости Python
    if [ -d "$WORKERNET_ROOT/backend" ] && [ -f "$WORKERNET_ROOT/backend/venv/bin/activate" ]; then
        print_status "Обновляем зависимости Python..."
        cd "$WORKERNET_ROOT/backend"
        source venv/bin/activate
        pip install -U pip setuptools wheel
        # Используем файлы зависимостей из корня репозитория
        if [ -f "$WORKERNET_ROOT/requirements.txt" ]; then
            pip install -r "$WORKERNET_ROOT/requirements.txt"
        else
            print_warning "requirements.txt не найден в корне: $WORKERNET_ROOT/requirements.txt"
        fi
        if [ -f "$WORKERNET_ROOT/requirements-dev.txt" ]; then
            pip install -r "$WORKERNET_ROOT/requirements-dev.txt"
        fi
        print_success "Зависимости Python обновлены"
    fi
    
    # Обновляем зависимости Node.js
    if [ -d "$WORKERNET_ROOT/frontend" ]; then
        print_status "Обновляем зависимости Node.js..."
        cd "$WORKERNET_ROOT/frontend"
        npm update
        print_success "Зависимости Node.js обновлены"
    fi
    
    # Выполняем миграции базы данных
    if [ -d "$WORKERNET_ROOT/backend" ]; then
        print_status "Выполняем миграции базы данных..."
        cd "$WORKERNET_ROOT/backend"
        source venv/bin/activate
        python manage.py migrate --fake-initial
        python manage.py collectstatic --noinput
        print_success "Миграции выполнены"
    fi
    
    # Перезапускаем сервисы
    print_status "Перезапускаем сервисы..."
    sudo systemctl start workernet-backend
    sudo systemctl start workernet-frontend
    
    print_success "Обновление завершено!"
}

# Новая установка
fresh_installation() {
    print_status "Выполнение новой установки WorkerNet Portal..."
    
    # Останавливаем существующие сервисы если они есть
    stop_services
}

# Main installation function
main() {
    print_status "Запуск универсального скрипта установки/обновления WorkerNet Portal для Ubuntu 24.04 LTS..."
    echo
    
    
    # Опционально: самообновление скрипта (выполнится до любых действий)
    # ВНИМАНИЕ: Самообновление отключено по умолчанию, так как может загрузить старую версию
    if [ "${WORKERNET_SELF_UPDATE:-0}" = "1" ] || [ "${1:-}" = "--self-update" ]; then
        print_warning "ВНИМАНИЕ: Самообновление может загрузить старую версию скрипта с GitHub!"
        print_status "Текущая версия скрипта: $SCRIPT_VERSION"
        self_update_script "$@"
    fi

    # Порядок выполнения:
    # 1. Проверка существующей установки (ПЕРВЫМ ДЕЛОМ!)
    # 2. Определение режима установки (update/fresh)
    # 3. Выполнение в зависимости от режима
    # 4. В режиме update: early_update_repository + update_installation
    # 5. В режиме fresh: полная установка с нуля
    
    # Проверяем существующую установку
    check_existing_installation
    
    # Проверяем, что режим установки был определен
    if [ -z "$INSTALLATION_MODE" ]; then
        print_error "Режим установки не определен"
        exit 1
    fi
    
    print_status "Выбран режим установки: $INSTALLATION_MODE"
    
    # Выполняем установку в зависимости от выбранного режима
    if [ "$INSTALLATION_MODE" = "update" ]; then
        # Режим обновления
        
        # Сначала определяем репозиторий для обновления
        if [ -z "$REPO_URL" ]; then
            # Находим существующий репозиторий для показа текущего URL
            EXISTING_REPO=""
            CANDIDATES=(
                "$(pwd)"
                "$HOME/workernet-portal"
                "$HOME/portal-support-ERP-WorkerNet"
            )
            
            for dir in "${CANDIDATES[@]}"; do
                if [ -d "$dir/.git" ] && [ -f "$dir/scripts/universal-install-update.sh" ]; then
                    EXISTING_REPO="$(cd "$dir" && git remote get-url origin 2>/dev/null || echo 'не определен')"
                    break
                fi
            done
            
            echo
            print_status "Обновление существующей установки"
            echo "Текущий репозиторий: $EXISTING_REPO"
            echo
            
            # Используем текущий репозиторий
            REPO_URL="$EXISTING_REPO"
            print_status "Используем текущий репозиторий: $REPO_URL"
            
            # Выбираем ветку
            select_branch_with_check
        else
            print_status "Используем репозиторий из переменной окружения: $REPO_URL"
        fi
        
        # Теперь выполняем раннее обновление с выбранным репозиторием
        early_update_repository
        update_installation
        
        # Показываем информацию об обновлении
        echo
        print_success "Обновление WorkerNet Portal завершено!"
        echo
        echo "=== Статус сервисов ==="
        sudo systemctl status workernet-backend --no-pager -l
        sudo systemctl status workernet-frontend --no-pager -l
        echo
        echo "=== Доступ к сервисам ==="
        echo "Фронтенд: http://${SERVER_DOMAIN_OR_IP}:3000"
        echo "API: http://${SERVER_DOMAIN_OR_IP}:8000"
        echo "Админ‑панель: http://${SERVER_DOMAIN_OR_IP}:8000/admin"
        echo
        echo "=== Управление сервисами ==="
        echo "Перезапуск: sudo systemctl restart workernet-backend workernet-frontend"
        echo "Статус: sudo systemctl status workernet-backend workernet-frontend"
        echo "Логи: sudo journalctl -u workernet-backend -f"
        echo
        
    else
        # Режим новой установки
        # Определяем репозиторий для новой установки
        if [ -z "$REPO_URL" ]; then
            REPO_URL="https://github.com/apelsin349/portal-support-ERP-WorkerNet.git"
            print_status "Используем репозиторий по умолчанию: $REPO_URL"
        fi
        # Проверяем доступные ветки для новой установки
        select_branch_with_check
        fresh_installation
        
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
        
        # Configuration
        select_branch_with_check
        clone_repository
        setup_environment
        setup_firewall
        # Гарантируем наличие каталога логов бэкенда до миграций
        mkdir -p "${WORKERNET_ROOT:-.}/backend/logs" || true
        setup_python_env
        setup_nodejs_env
        build_frontend
        
        # Database and Redis setup (ПЕРЕД миграциями!)
        setup_database
        setup_redis
        
        run_migrations
        create_superuser
        
        # Service setup
        setup_systemd_services
        setup_firewall
        start_services
        
        # Final information
        show_final_info
        show_access_info
    fi
}

# Обработка аргументов
case "${1:-}" in
    --help|-h)
        echo "Универсальный скрипт установки и обновления WorkerNet Portal для Ubuntu 24.04 LTS"
        echo
        echo "Использование: $0 [опции]"
        echo
        echo "Опции:"
        echo "  --help, -h     Показать эту справку"
        echo "  --branch BRANCH Указать ветку для установки"
        echo "  --self-update  Обновить сам скрипт"
        echo
        echo "Переменные окружения:"
        echo "  WORKERNET_BRANCH=BRANCH     Ветка для установки"
        echo "  WORKERNET_NONINTERACTIVE=1  Неинтерактивный режим"
        echo "  WORKERNET_SELF_UPDATE=1     Самообновление скрипта"
        echo
        echo "Примеры:"
        echo "  $0 --branch develop        Установить ветку develop"
        echo "  $0 --branch feature/new    Установить ветку feature/new"
        echo "  $0 --self-update           Обновить сам скрипт"
        echo "  WORKERNET_BRANCH=main $0   Установить ветку main через переменную"
        echo
        exit 0
        ;;
    --branch)
        if [ -z "${2:-}" ]; then
            print_error "Не указана ветка для --branch"
            echo "Использование: $0 --branch BRANCH_NAME"
            exit 1
        fi
        export WORKERNET_BRANCH="$2"
        main "$@"
        ;;
    --self-update)
        WORKERNET_SELF_UPDATE=1 exec bash "$0" "$@"
        ;;
    *)
        main "$@"
        ;;
esac
