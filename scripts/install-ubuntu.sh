#!/bin/bash

# Скрипт установки WorkerNet Portal для Ubuntu 24.04 LTS
# Скрипт устанавливает все зависимости и подготавливает WorkerNet Portal

set -e

# Ensure stable working directory to avoid "getcwd() failed" issues
# If launched from inside a cloned repo, pin to repo root; otherwise use $HOME
if git rev-parse --show-toplevel >/dev/null 2>&1; then
    export WORKERNET_ROOT="$(git rev-parse --show-toplevel)"
    cd "$WORKERNET_ROOT" || exit 1
else
    cd "$HOME" || exit 1
fi

# Repository configuration (can be overridden via env)
REPO_URL="${WORKERNET_REPO_URL:-https://github.com/apelsin349/portal-support-ERP-WorkerNet.git}"
REPO_URL_MIRROR="${WORKERNET_REPO_MIRROR:-}"
REPO_BRANCH="${WORKERNET_BRANCH:-main}"

# Server configuration (can be overridden via env)
SERVER_DOMAIN_OR_IP="${WORKERNET_DOMAIN_OR_IP:-$(hostname -I | awk '{print $1}')}"

# NPM registry and proxy configuration (tunable for restricted networks)
NPM_REGISTRY_DEFAULT="https://registry.npmmirror.com"
NPM_REGISTRY="${NPM_REGISTRY:-$NPM_REGISTRY_DEFAULT}"
NPM_FETCH_TIMEOUT_MS="${NPM_FETCH_TIMEOUT_MS:-120000}"
NPM_FETCH_RETRY_MAXTIMEOUT_MS="${NPM_FETCH_RETRY_MAXTIMEOUT_MS:-120000}"
NPM_FETCH_RETRIES="${NPM_FETCH_RETRIES:-5}"
NPM_STRICT_SSL="${NPM_STRICT_SSL:-true}"

# Installation mode (will be set by check_existing_installation)
INSTALLATION_MODE=""

# Script version (bump on meaningful changes)
SCRIPT_VERSION="2025-09-18.1"

# Self-update of this script from GitHub raw if requested
self_update_script() {
    # Enable with env WORKERNET_SELF_UPDATE=1 or argument --self-update
    if [ "${WORKERNET_SELF_UPDATE:-0}" != "1" ]; then
        return 0
    fi

    print_status "Проверяем обновления install-ubuntu.sh... (self-update)"

    # Resolve current script path
    SCRIPT_PATH="$0"
    if command -v readlink >/dev/null 2>&1; then
        SCRIPT_PATH="$(readlink -f "$SCRIPT_PATH" 2>/dev/null || echo "$SCRIPT_PATH")"
    fi

    RAW_BRANCH="${REPO_BRANCH:-main}"
    RAW_URL="${WORKERNET_RAW_SCRIPT_URL:-https://raw.githubusercontent.com/apelsin349/portal-support-ERP-WorkerNet/${RAW_BRANCH}/scripts/install-ubuntu.sh}"

    TMP_FILE="/tmp/install-ubuntu.sh.$$"
    if curl -fsSL "$RAW_URL" -o "$TMP_FILE"; then
        if cmp -s "$TMP_FILE" "$SCRIPT_PATH"; then
            print_status "Скрипт установки уже актуален (версия: $SCRIPT_VERSION)"
            rm -f "$TMP_FILE"
        else
            print_status "Найдена новая версия скрипта — обновляем..."
            chmod +x "$TMP_FILE" 2>/dev/null || true
            # Try to preserve owner/permissions
            sudo cp -f "$TMP_FILE" "$SCRIPT_PATH" 2>/dev/null || cp -f "$TMP_FILE" "$SCRIPT_PATH"
            rm -f "$TMP_FILE"
            print_success "Скрипт обновлён. Перезапуск..."
            exec bash "$SCRIPT_PATH" "$@"
        fi
    else
        print_warning "Не удалось загрузить обновление скрипта по адресу: $RAW_URL"
    fi
}

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Без цвета

# Сетевые таймауты (можно менять через переменные окружения)
CURL_CONNECT_TIMEOUT=${CURL_CONNECT_TIMEOUT:-3}
CURL_MAX_TIME=${CURL_MAX_TIME:-10}
CURL_OPTS="--fail --silent --show-error --location --connect-timeout $CURL_CONNECT_TIMEOUT --max-time $CURL_MAX_TIME"

# Таймауты APT
APT_HTTP_TIMEOUT=${APT_HTTP_TIMEOUT:-25}
APT_HTTPS_TIMEOUT=${APT_HTTPS_TIMEOUT:-25}

# Параметры по умолчанию для паролей/секретов (можно переопределить окружением)
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

# Additional status helper
ok() {
    echo -e "${GREEN}[OK]${NC} $1"
}

# Простая проверка доступности URL (HEAD)
check_url() {
    curl -sSfI --connect-timeout "$CURL_CONNECT_TIMEOUT" --max-time "$CURL_MAX_TIME" "$1" >/dev/null 2>&1
}

# Раннее обновление репозитория проекта (если он уже есть на сервере)
early_update_repository() {
    print_status "Пробуем рано обновить файлы проекта (если репозиторий уже существует)..."
    if ! command -v git >/dev/null 2>&1; then
        print_warning "git не установлен, пропускаем раннее обновление"
        return 0
    fi

    # Кандидаты на корень репозитория
    CANDIDATES=(
        "$(pwd)"
        "$HOME/workernet-portal/portal-support-ERP-WorkerNet"
        "$HOME/portal-support-ERP-WorkerNet"
    )

    for dir in "${CANDIDATES[@]}"; do
        if [ -d "$dir/.git" ] && [ -f "$dir/scripts/install-ubuntu.sh" ]; then
            print_status "Найден репозиторий: $dir — обновляем..."
            (
                cd "$dir" || exit 0
                git remote -v >/dev/null 2>&1 || exit 0
                # Выбираем origin URL и ветку
                ORIGIN_URL=$(git remote get-url origin 2>/dev/null || echo "")
                [ -n "$REPO_URL" ] && [ "$ORIGIN_URL" != "$REPO_URL" ] && git remote set-url origin "$REPO_URL" || true
                git fetch --all --prune || true
                # Выбор ветки
                BR=${REPO_BRANCH:-$(git remote show origin | awk '/HEAD branch/ {print $NF}')}
                BR=${BR:-main}
                git checkout "$BR" 2>/dev/null || git checkout -B "$BR" || true
                git reset --hard "origin/$BR" || true
                git submodule update --init --recursive || true
            )
            export WORKERNET_ROOT="$dir"
            print_success "Репозиторий обновлён: $dir"
            return 0
        fi
    done

    print_status "Существующий репозиторий не найден — перейдём к стандартной установке."
}

# Проверяем доступность внешних репозиториев и настраиваем запасные источники
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

# Установка Python (предпочтительно 3.12, затем 3.11, иначе системный python3)
install_python() {
    print_status "Устанавливаем Python..."

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
        export WORKERNET_PY3="$PYTHON_TARGET"
        print_success "Python установлен ($("$PYTHON_TARGET" -V 2>&1))"
    else
        export WORKERNET_PY3="$(command -v python3)"
        print_success "Python установлен ($(python3 -V 2>&1))"
    fi
}

# Установка Node.js 18 (с устойчивыми фолбэками)
install_nodejs() {
    print_status "Устанавливаем Node.js 18..."

    # 1) NodeSource (обычно быстрее по версиям)
    if curl $CURL_OPTS https://deb.nodesource.com/setup_18.x | sudo -E bash - && \
       sudo apt install -y nodejs; then
        print_success "Node.js 18 установлен (Node: $(node -v 2>/dev/null), NPM: $(npm -v 2>/dev/null))"
        return 0
    fi

    print_warning "NodeSource недоступен. Пробуем репозитории Ubuntu..."
    # Очистка потенциально проблемного источника NodeSource, чтобы не мешал APT
    if [ -f /etc/apt/sources.list.d/nodesource.list ]; then
        sudo rm -f /etc/apt/sources.list.d/nodesource.list || true
    fi
    sudo apt -o Acquire::http::Timeout=$APT_HTTP_TIMEOUT -o Acquire::https::Timeout=$APT_HTTPS_TIMEOUT update || true
    # Устанавливаем только nodejs, npm подтянется при необходимости или есть в комплекте
    if sudo apt install -y nodejs; then
        # Если npm всё ещё отсутствует, пытаемся доставить (может конфликтовать с nodesource, поэтому не падаем)
        if ! command -v npm >/dev/null 2>&1; then
            sudo apt install -y npm || true
        fi
        print_success "Node.js установлен из репозиториев Ubuntu (Node: $(node -v 2>/dev/null), NPM: $(npm -v 2>/dev/null))"
        return 0
    fi

    print_warning "Репозитории Ubuntu недоступны. Пробуем NVM..."
    ( 
        cd "$HOME" || true
        curl $CURL_OPTS https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash || true
    )
    # shellcheck source=/dev/null
    [ -s "$HOME/.nvm/nvm.sh" ] && . "$HOME/.nvm/nvm.sh"
    if command -v nvm >/dev/null 2>&1; then
        # Зеркала, если github/nodejs недоступны
        export NVM_NODEJS_ORG_MIRROR="https://npmmirror.com/mirrors/node"
        export NVM_IOJS_ORG_MIRROR="https://npmmirror.com/mirrors/iojs"
        if nvm install 18 && nvm alias default 18 && nvm use 18; then
            print_success "Node.js установлен через NVM (Node: $(node -v 2>/dev/null), NPM: $(npm -v 2>/dev/null))"
            # Защита от ошибок npm при отсутствии валидной CWD и верификация npm
            if ( cd "$HOME" && npm -v >/dev/null 2>&1 ); then
                ( cd "$HOME" && npm config set registry https://registry.npmmirror.com ) || true
            else
                print_warning "npm недоступен после установки NVM. Пробую переустановить Node 18..."
                nvm uninstall 18 || true
                nvm install 18 || true
                nvm alias default 18 || true
                nvm use 18 || true
                ( cd "$HOME" && npm -v ) || print_warning "npm всё ещё недоступен; продолжайте с Node без npm или установите npm вручную."
            fi
            return 0
        fi
    fi

    print_warning "NVM недоступен. Пробуем Snap..."
    if ! command -v snap >/dev/null 2>&1; then
        sudo apt install -y snapd
        sudo systemctl enable --now snapd || true
    fi
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

# Установка Prometheus и Grafana (опционально)
install_monitoring_stack() {
    print_status "Устанавливаем Prometheus и Grafana..."

    # Репозиторий Grafana
    # Удаляем устаревшие записи repos/keys (идемпотентно)
    if grep -q "packages.grafana.com" /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null; then
        print_status "Удаляем устаревший репозиторий packages.grafana.com..."
        sudo rm -f /etc/apt/sources.list.d/grafana.list /etc/apt/sources.list.d/grafana-oss.list || true
    fi
    # Настраиваем актуальный репозиторий apt.grafana.com с keyring
    APT_GRAFANA_OK=false
    if ! grep -q "apt.grafana.com" /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null; then
        print_status "Добавляем репозиторий Grafana (apt.grafana.com) и ключ..."
        sudo install -m 0755 -d /etc/apt/keyrings || true
        if curl $CURL_OPTS https://apt.grafana.com/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/grafana.gpg; then
            sudo chmod a+r /etc/apt/keyrings/grafana.gpg || true
            echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list >/dev/null
        else
            print_warning "Не удалось получить ключ apt.grafana.com (возможно 403). Будет использован фолбэк на .deb установку."
        fi
    fi

    # Обновляем индексы пакетов; не прерываем выполнение при ошибке Grafana репозитория
    if sudo apt -o Acquire::http::Timeout=$APT_HTTP_TIMEOUT -o Acquire::https::Timeout=$APT_HTTPS_TIMEOUT update; then
        # Проверим, нет ли явной ошибки 403 для apt.grafana.com
        if check_url "https://apt.grafana.com/dists/stable/InRelease"; then
            APT_GRAFANA_OK=true
        fi
    fi

    # Устанавливаем Prometheus из APT, а Grafana — либо из APT, либо из .deb (фолбэк)
    # Prometheus: пропускаем, если бинарь/сервис есть
    if command -v prometheus >/dev/null 2>&1 || systemctl list-unit-files | grep -q "^prometheus\.service"; then
        print_status "Prometheus уже установлен — пропускаем установку"
    else
        sudo apt install -y prometheus || true
    fi

    # Grafana: если сервис уже есть — не переустанавливаем
    if systemctl list-unit-files | grep -q "^grafana-server\.service"; then
        print_status "Grafana уже установлена — пропускаем установку"
    elif [ "$APT_GRAFANA_OK" = true ]; then
        sudo apt install -y grafana || true
    else
        print_warning "Установка Grafana из репозитория недоступна. Переходим на установку из .deb"
        # Фолбэк: установка Grafana из релизного .deb
        GRAFANA_VERSION="${GRAFANA_VERSION:-10.4.3}"
        # Можно переопределить зеркалом в РФ через переменную окружения GRAFANA_DEB_URL
        GRAFANA_DEB_URL_DEFAULT="https://dl.grafana.com/oss/release/grafana_${GRAFANA_VERSION}_amd64.deb"
        GRAFANA_DEB_URL="${GRAFANA_DEB_URL:-$GRAFANA_DEB_URL_DEFAULT}"
        TMP_DEB="/tmp/grafana_${GRAFANA_VERSION}_amd64.deb"
        if curl $CURL_OPTS "$GRAFANA_DEB_URL" -o "$TMP_DEB"; then
            sudo apt install -y adduser libfontconfig1 || true
            if sudo dpkg -i "$TMP_DEB"; then
                print_success "Grafana установлена из .deb (${GRAFANA_VERSION})"
            else
                print_warning "dpkg сообщил о неудовлетворённых зависимостях — пытаемся исправить"
                sudo apt -f install -y || true
            fi
            rm -f "$TMP_DEB" || true
        else
            print_error "Не удалось загрузить .deb Grafana по адресу: $GRAFANA_DEB_URL"
            echo "Подсказка: укажите зеркало через переменную окружения GRAFANA_DEB_URL (например, локальный артефакт-сервер)."
        fi
    fi

    # Включаем автозапуск
    sudo systemctl enable prometheus 2>/dev/null || true
    sudo systemctl enable grafana-server 2>/dev/null || true

    # Применяем нашу конфигурацию Prometheus, если она есть в репозитории
    if [ -f "$WORKERNET_ROOT/config/prometheus.yml" ]; then
        print_status "Копируем конфигурацию Prometheus из репозитория..."
        sudo mkdir -p /etc/prometheus
        sudo cp -f "$WORKERNET_ROOT/config/prometheus.yml" /etc/prometheus/prometheus.yml
    fi
    if [ -f "$WORKERNET_ROOT/config/alert_rules.yml" ]; then
        sudo cp -f "$WORKERNET_ROOT/config/alert_rules.yml" /etc/prometheus/alert_rules.yml
    fi

    # Перезапускаем сервисы
    sudo systemctl restart prometheus 2>/dev/null || true
    sudo systemctl restart grafana-server 2>/dev/null || true

    print_success "Prometheus и Grafana установлены"
}

# Проверка Prometheus и Grafana
verify_monitoring_stack() {
    print_status "Проверяем Prometheus и Grafana..."

    local ok=true

    # Проверяем systemd статусы
    if systemctl is-active --quiet prometheus; then
        print_success "Prometheus: активен"
    else
        print_warning "Prometheus: не запущен"
        ok=false
    fi
    if systemctl is-active --quiet grafana-server; then
        print_success "Grafana: активна"
    else
        print_warning "Grafana: не запущена"
        ok=false
    fi

    # Проверка портов
    if command -v curl >/dev/null 2>&1; then
        curl -fsS http://${SERVER_DOMAIN_OR_IP}:9090 >/dev/null 2>&1 && print_success "Prometheus UI доступен: http://${SERVER_DOMAIN_OR_IP}:9090" || { print_warning "Prometheus UI недоступен: http://${SERVER_DOMAIN_OR_IP}:9090"; ok=false; }
        # Проверяем оба варианта портов Grafana: 3000 (deb) и 3001 (docker-compose)
        if curl -fsS http://${SERVER_DOMAIN_OR_IP}:3000 >/dev/null 2>&1; then
            print_success "Grafana UI доступна: http://${SERVER_DOMAIN_OR_IP}:3000 (admin/admin)"
        elif curl -fsS http://${SERVER_DOMAIN_OR_IP}:3001 >/dev/null 2>&1; then
            print_success "Grafana UI доступна: http://${SERVER_DOMAIN_OR_IP}:3001 (admin/admin)"
        else
            print_warning "Grafana UI недоступна на портах 3000/3001"
            ok=false
        fi
    fi

    if [ "$ok" = true ]; then
        print_success "Мониторинг работает корректно"
    else
        print_warning "Мониторинг настроен не полностью. Проверьте логи: sudo journalctl -u prometheus -u grafana-server -f"
    fi
}

# Установка Docker
install_docker() {
    if command -v docker >/dev/null 2>&1; then
        print_status "Docker уже установлен — пропускаем установку"
        # Ensure docker service running and compose present
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
        # Ensure compose plugin when using docker-ce
        sudo apt install -y docker-compose-plugin || true
    fi

    # Ensure Docker daemon enabled on boot
    sudo systemctl enable --now docker || true

    # Add user to docker group
    sudo usermod -aG docker $USER || true
    print_warning "Чтобы использовать docker без sudo, выйдите и войдите в систему заново."
    print_success "Docker установлен"
}

# Установка дополнительных инструментов
install_additional_tools() {
    print_status "Устанавливаем дополнительные инструменты..."
    
    # Git LFS
    sudo apt install -y git-lfs
    git lfs install
    
    # Python development tools
    sudo apt install -y python3-dev python3-venv python3-pip
    
    # Database tools (use generic client to match Ubuntu release)
    sudo apt install -y postgresql-client-common postgresql-client || true

    # Useful CLI utilities used by scripts
    sudo apt install -y jq net-tools unzip make htop tree || true
    
    print_success "Дополнительные инструменты установлены"
}

# Проверка наличия зависимостей и вывод версий
verify_dependencies() {
    print_status "Проверяем установленные зависимости..."

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
            print_warning "Отсутствует команда: $cmd"
            MISSING=1
        fi
    done

    # Docker Compose (plugin or standalone)
    if docker compose version >/dev/null 2>&1; then
        docker compose version | head -n1
    elif command -v docker-compose >/dev/null 2>&1; then
        docker-compose --version
    else
        print_warning "Отсутствует Docker Compose (plugin или standalone)"
        MISSING=1
    fi

    # Services status
    print_status "Проверяем статусы сервисов (PostgreSQL/Redis/Docker)"
    sudo systemctl is-enabled postgresql >/dev/null 2>&1 && echo "postgresql: enabled" || echo "postgresql: not enabled"
    sudo systemctl is-active postgresql >/dev/null 2>&1 && echo "postgresql: active" || echo "postgresql: inactive"

    sudo systemctl is-enabled redis-server >/dev/null 2>&1 && echo "redis-server: enabled" || echo "redis-server: not enabled" 
    sudo systemctl is-active redis-server >/dev/null 2>&1 && echo "redis-server: active" || echo "redis-server: inactive"

    sudo systemctl is-enabled docker >/dev/null 2>&1 && echo "docker: enabled" || echo "docker: not enabled"
    sudo systemctl is-active docker >/dev/null 2>&1 && echo "docker: active" || echo "docker: inactive"

    if [ "${MISSING:-0}" = "1" ]; then
        print_warning "Отсутствуют зависимости. Продолжаем, но сборка может завершиться ошибкой."
    else
        print_success "Все необходимые зависимости установлены"
    fi
}

# Настройка Redis
configure_redis() {
    print_status "Настраиваем Redis..."
    
    # Проверяем, существует ли файл конфигурации Redis
    if [ ! -f "/etc/redis/redis.conf" ]; then
        print_warning "Файл конфигурации Redis не найден: /etc/redis/redis.conf"
        print_status "Пропускаем настройку Redis конфигурации"
        return 0
    fi
    
    # Set password for Redis (robust replace or append)
    sudo sed -i "s/^[#[:space:]]*requirepass .*/requirepass ${WORKERNET_REDIS_PASS}/" /etc/redis/redis.conf 2>/dev/null || true
    if ! sudo grep -q "^requirepass" /etc/redis/redis.conf 2>/dev/null; then
        echo "requirepass ${WORKERNET_REDIS_PASS}" | sudo tee -a /etc/redis/redis.conf >/dev/null 2>&1 || true
    fi
    
    # Configure Redis for better performance (robust replace or append)
    sudo sed -i "s/^[#[:space:]]*maxmemory .*/maxmemory 512mb/" /etc/redis/redis.conf 2>/dev/null || true
    if ! sudo grep -q "^maxmemory 512mb" /etc/redis/redis.conf 2>/dev/null; then
        echo "maxmemory 512mb" | sudo tee -a /etc/redis/redis.conf >/dev/null 2>&1 || true
    fi
    sudo sed -i "s/^[#[:space:]]*maxmemory-policy .*/maxmemory-policy allkeys-lru/" /etc/redis/redis.conf 2>/dev/null || true
    if ! sudo grep -q "^maxmemory-policy allkeys-lru" /etc/redis/redis.conf 2>/dev/null; then
        echo "maxmemory-policy allkeys-lru" | sudo tee -a /etc/redis/redis.conf >/dev/null 2>&1 || true
    fi
    
    # Restart Redis
    sudo systemctl restart redis-server 2>/dev/null || true
    # Enable auto-start on boot
    sudo systemctl enable redis-server 2>/dev/null || true

    print_success "Redis настроен"
}

# Создание каталога проекта
create_project_directory() {
    print_status "Создаём каталог проекта..."
    
    # Если WORKERNET_ROOT уже установлен (например, early_update_repository), используем его
    if [ -n "${WORKERNET_ROOT:-}" ] && [ -d "$WORKERNET_ROOT" ]; then
        print_success "Используем уже установленный корень проекта: $WORKERNET_ROOT"
        cd "$WORKERNET_ROOT"
        return 0
    fi

    # Создаём временный каталог для клонирования (будет перезаписан в clone_repository)
    PROJECT_DIR="$HOME/workernet-portal"
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    print_success "Временный каталог проекта создан: $PROJECT_DIR"
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
    if [ -d .git ] && [ -d backend ] && [ -f scripts/install-ubuntu.sh ]; then
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

    # Обновляем ссылки и жёстко синхронизируемся с нужной веткой
    git fetch --all --prune || true
    # Determine default branch if requested not found
    if ! git show-ref --verify --quiet "refs/remotes/origin/$REPO_BRANCH"; then
        REPO_BRANCH=$(git remote show origin | awk '/HEAD branch/ {print $NF}')
        REPO_BRANCH=${REPO_BRANCH:-main}
        print_warning "Запрошенная ветка не найдена; используем ветку по умолчанию: $REPO_BRANCH"
    fi

    git checkout "$REPO_BRANCH" 2>/dev/null || git checkout -B "$REPO_BRANCH"
    git reset --hard "origin/$REPO_BRANCH" || true
    git submodule update --init --recursive || true

    print_success "Репозиторий актуален (ветка: $REPO_BRANCH)"

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

    # Ensure required minimum set if keys were entirely absent
    grep -q "^DJANGO_SECRET_KEY=" .env || echo "DJANGO_SECRET_KEY=$(esc "$SECRET_KEY")" >> .env
    grep -q "^JWT_SECRET=" .env || echo "JWT_SECRET=$(esc "$JWT_SECRET")" >> .env
    # Для совместимости с настройками Django/DRF SimpleJWT
    grep -q "^SECRET_KEY=" .env || echo "SECRET_KEY=$(esc "$SECRET_KEY")" >> .env
    grep -q "^JWT_SECRET_KEY=" .env || echo "JWT_SECRET_KEY=$(esc "$JWT_SECRET")" >> .env

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
    sudo -u postgres psql -c "DROP USER IF EXISTS $DB_USER;" 2>/dev/null || true
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD' CREATEDB SUPERUSER;"
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
    # Если включена установка мониторинга — открываем порты Grafana/Prometheus
    if [ "${WORKERNET_INSTALL_MONITORING:-1}" = "1" ]; then
        # Grafana .deb по умолчанию слушает 3000; docker-compose — 3001
        sudo ufw allow 3000/tcp || true
        sudo ufw allow 3001/tcp || true
        sudo ufw allow 9090/tcp || true
    fi
    
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
    # Мониторинг (Grafana/Prometheus) не устанавливается этим скриптом
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
    echo "=== Обновления ==="
    echo "Ручное обновление: /opt/update-workernet.sh"
    echo "Автоматическое обновление: настроено (ежедневно в 2:00)"
    echo "Логи обновлений: /var/log/workernet-update.log"
    echo "Отключить автообновление: crontab -e (удалить строку с update-workernet.sh)"
    echo
}

# Проверка существующей установки
check_existing_installation() {
    print_status "Проверяем существующую установку WorkerNet Portal..."
    print_status "Этот шаг выполняется ПЕРВЫМ для определения режима установки"
    
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

# Создание скрипта автоматического обновления
create_auto_update_script() {
    print_status "Создаем скрипт автоматического обновления..."
    
    # Создаем скрипт обновления
    sudo tee /opt/update-workernet.sh > /dev/null << 'EOF'
#!/bin/bash

# Скрипт автоматического обновления WorkerNet Portal
# Запускается через cron для автоматических обновлений

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

# Логирование
LOG_FILE="/var/log/workernet-update.log"
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Проверка обновлений
check_for_updates() {
    print_status "Проверяем наличие обновлений..."
    
    cd /opt/workernet || cd "$HOME/portal-support-ERP-WorkerNet" || {
        print_error "Директория проекта не найдена"
        exit 1
    }
    
    # Получаем информацию о текущей ветке
    CURRENT_BRANCH=$(git branch --show-current)
    git fetch --all --prune
    
    # Проверяем наличие новых коммитов
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse "origin/$CURRENT_BRANCH")
    
    if [ "$LOCAL" = "$REMOTE" ]; then
        print_status "Обновления не найдены"
        return 1
    else
        print_status "Найдены обновления"
        return 0
    fi
}

# Выполнение обновления
perform_update() {
    print_status "Выполняем обновление..."
    
    # Устанавливаем переменные для неинтерактивного режима
    export WORKERNET_AUTO_UPDATE=1
    export WORKERNET_NONINTERACTIVE=1
    
    # Запускаем скрипт установки в режиме обновления
    if [ -f "/opt/workernet/scripts/install-ubuntu.sh" ]; then
        cd /opt/workernet
        ./scripts/install-ubuntu.sh
    elif [ -f "$HOME/portal-support-ERP-WorkerNet/scripts/install-ubuntu.sh" ]; then
        cd "$HOME/portal-support-ERP-WorkerNet"
        ./scripts/install-ubuntu.sh
    else
        print_error "Скрипт установки не найден"
        exit 1
    fi
}

# Основная функция
main() {
    log "Запуск проверки обновлений WorkerNet Portal"
    
    if check_for_updates; then
        log "Найдены обновления, начинаем процесс обновления"
        perform_update
        log "Обновление завершено успешно"
        print_success "WorkerNet Portal успешно обновлен!"
    else
        log "Обновления не найдены"
    fi
}

# Запуск
main "$@"
EOF

    # Делаем скрипт исполняемым
    sudo chmod +x /opt/update-workernet.sh
    
    # Создаем задачу cron для автоматического обновления (ежедневно в 2:00)
    print_status "Настраиваем автоматическое обновление..."
    
    # Проверяем, есть ли уже задача cron
    if ! crontab -l 2>/dev/null | grep -q "update-workernet.sh"; then
        # Добавляем задачу cron
        (crontab -l 2>/dev/null; echo "0 2 * * * /opt/update-workernet.sh >> /var/log/workernet-update.log 2>&1") | crontab -
        print_success "Автоматическое обновление настроено (ежедневно в 2:00)"
    else
        print_status "Автоматическое обновление уже настроено"
    fi
    
    print_success "Скрипт автоматического обновления создан: /opt/update-workernet.sh"
}

# Новая установка
fresh_installation() {
    print_status "Выполнение новой установки WorkerNet Portal..."
    
    # Останавливаем существующие сервисы если они есть
    stop_services
}

# Main installation function
main() {
    print_status "Запуск установки WorkerNet Portal для Ubuntu 24.04 LTS..."
    echo
    
    # Опционально: самообновление скрипта (выполнится до любых действий)
    if [ "${WORKERNET_SELF_UPDATE:-0}" = "1" ] || [ "${1:-}" = "--self-update" ]; then
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
        # Раннее обновление проекта, если уже клонирован
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
        echo "=== Обновления ==="
        echo "Ручное обновление: /opt/update-workernet.sh"
        echo "Автоматическое обновление: настроено (ежедневно в 2:00)"
        echo "Логи обновлений: /var/log/workernet-update.log"
        echo "Отключить автообновление: crontab -e (удалить строку с update-workernet.sh)"
        
    else
        # Режим новой установки
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
        install_additional_tools
        verify_dependencies
        
        # Configuration
        configure_redis
        
        # Optional monitoring stack (Prometheus + Grafana) если включено
        if [ "${WORKERNET_INSTALL_MONITORING:-1}" = "1" ]; then
            install_monitoring_stack
        else
            print_status "Пропускаем установку мониторинга (WORKERNET_INSTALL_MONITORING=0)"
        fi
        
        # Project setup
        create_project_directory
        clone_repository
        setup_environment
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
        
        # Создаем скрипт автоматического обновления
        create_auto_update_script
        
        # Проверка мониторинга
        if [ "${WORKERNET_INSTALL_MONITORING:-1}" = "1" ]; then
            verify_monitoring_stack
        fi
        
        # Final information
        show_final_info
    fi
}

# Run main function
main "$@"
