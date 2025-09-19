#!/bin/bash

# Скрипт быстрого обновления WorkerNet Portal
# Используется для быстрого обновления без полной переустановки

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

# Версия скрипта
SCRIPT_VERSION="2025-09-18.1"

# Server configuration (can be overridden via env)
SERVER_DOMAIN_OR_IP="${WORKERNET_DOMAIN_OR_IP:-$(hostname -I | awk '{print $1}')}"

# Самообновление скрипта с GitHub raw
self_update_script() {
  if [ "${WORKERNET_SELF_UPDATE:-0}" != "1" ] && [ "${1:-}" != "--self-update" ]; then
    return 0
  fi

  print_status "Проверяем обновления quick-update.sh... (self-update)"

  SCRIPT_PATH="$0"
  if command -v readlink >/dev/null 2>&1; then
    SCRIPT_PATH="$(readlink -f "$SCRIPT_PATH" 2>/dev/null || echo "$SCRIPT_PATH")"
  fi

  RAW_BRANCH="${WORKERNET_BRANCH:-main}"
  RAW_URL="${WORKERNET_RAW_QUICK_URL:-https://raw.githubusercontent.com/apelsin349/portal-support-ERP-WorkerNet/${RAW_BRANCH}/scripts/quick-update.sh}"

  TMP_FILE="/tmp/quick-update.sh.$$"
  if curl -fsSL "$RAW_URL" -o "$TMP_FILE"; then
    if cmp -s "$TMP_FILE" "$SCRIPT_PATH"; then
      print_status "Скрипт quick-update актуален (версия: $SCRIPT_VERSION)"
      rm -f "$TMP_FILE"
    else
      print_status "Найдена новая версия quick-update — обновляем..."
      chmod +x "$TMP_FILE" 2>/dev/null || true
      sudo cp -f "$TMP_FILE" "$SCRIPT_PATH" 2>/dev/null || cp -f "$TMP_FILE" "$SCRIPT_PATH"
      rm -f "$TMP_FILE"
      print_success "Скрипт обновлён. Перезапуск..."
      exec bash "$SCRIPT_PATH" "$@"
    fi
  else
    print_warning "Не удалось загрузить обновление quick-update по адресу: $RAW_URL"
  fi
}

# Находим директорию проекта
find_project_directory() {
    if [ -d "/opt/workernet" ]; then
        PROJECT_DIR="/opt/workernet"
    elif [ -d "$HOME/portal-support-ERP-WorkerNet" ]; then
        PROJECT_DIR="$HOME/portal-support-ERP-WorkerNet"
    elif [ -d "$HOME/workernet-portal" ]; then
        PROJECT_DIR="$HOME/workernet-portal"
    else
        print_error "Директория проекта не найдена"
        print_status "Ищем в стандартных местах:"
        print_status "- /opt/workernet"
        print_status "- $HOME/portal-support-ERP-WorkerNet"
        print_status "- $HOME/workernet-portal"
        exit 1
    fi
    
    print_status "Найдена директория проекта: $PROJECT_DIR"
}

# Проверка обновлений
check_for_updates() {
    print_status "Проверяем наличие обновлений..."
    
    cd "$PROJECT_DIR"
    
    # Получаем информацию о текущей ветке
    CURRENT_BRANCH=$(git branch --show-current)
    git fetch --all --prune
    
    # Проверяем наличие новых коммитов
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse "origin/$CURRENT_BRANCH")
    
    if [ "$LOCAL" = "$REMOTE" ]; then
        print_success "Обновления не найдены - система актуальна"
        return 1
    else
        print_warning "Найдены обновления"
        print_status "Текущая версия: $LOCAL"
        print_status "Новая версия: $REMOTE"
        return 0
    fi
}

# Остановка сервисов
stop_services() {
    print_status "Останавливаем сервисы..."
    
    sudo systemctl stop workernet-backend 2>/dev/null || true
    sudo systemctl stop workernet-frontend 2>/dev/null || true
    
    print_success "Сервисы остановлены"
}

# Обновление кода
update_code() {
    print_status "Обновляем код из репозитория..."
    
    cd "$PROJECT_DIR"
    
    # Сохраняем локальные изменения
    if ! git diff --quiet || ! git diff --cached --quiet; then
        print_warning "Обнаружены локальные изменения"
        git stash push -m "Auto-stash before update $(date)" || true
    fi
    
    # Обновляем код
    git fetch --all --prune
    git reset --hard "origin/$(git branch --show-current)"
    git submodule update --init --recursive 2>/dev/null || true
    
    print_success "Код обновлен"
}

# Обновление зависимостей Python
update_python_deps() {
    # Определяем путь к venv (по умолчанию backend/venv)
    VENV_DIR="$PROJECT_DIR/backend/venv"
    if [ ! -f "$VENV_DIR/bin/activate" ]; then
        print_warning "Виртуальное окружение не найдено в $VENV_DIR"
        # Пытаемся найти альтернативный venv
        if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
            VENV_DIR="$PROJECT_DIR/venv"
            print_status "Используем альтернативный venv: $VENV_DIR"
        else
            print_warning "Виртуальное окружение Python не найдено — пропускаем обновление Python зависимостей"
            return 0
        fi
    fi

    print_status "Обновляем зависимости Python..."

    # Активируем окружение
    # shellcheck disable=SC1090
    source "$VENV_DIR/bin/activate"

    pip install -U pip setuptools wheel

    # Ищем requirements: сначала в backend/, затем в корне
    REQ_PRIMARY="$PROJECT_DIR/requirements.txt"
    REQ_SECONDARY="$PROJECT_DIR/backend/requirements.txt"
    DEV_PRIMARY="$PROJECT_DIR/requirements-dev.txt"
    DEV_SECONDARY="$PROJECT_DIR/backend/requirements-dev.txt"

    if [ -f "$REQ_PRIMARY" ]; then
        pip install -r "$REQ_PRIMARY"
    elif [ -f "$REQ_SECONDARY" ]; then
        pip install -r "$REQ_SECONDARY"
    else
        print_warning "requirements.txt не найден ни в backend/, ни в корне — пропускаем установку основных зависимостей"
    fi

    if [ -f "$DEV_PRIMARY" ]; then
        pip install -r "$DEV_PRIMARY"
    elif [ -f "$DEV_SECONDARY" ]; then
        pip install -r "$DEV_SECONDARY"
    fi

    print_success "Зависимости Python обновлены"
}

# Обновление зависимостей Node.js
update_nodejs_deps() {
    if [ -d "$PROJECT_DIR/frontend" ]; then
        print_status "Обновляем зависимости Node.js..."
        
        cd "$PROJECT_DIR/frontend"
        npm update
        
        print_success "Зависимости Node.js обновлены"
    else
        print_warning "Директория frontend не найдена"
    fi
}

# Сборка фронтенда с PWA
build_frontend() {
    if [ -d "$PROJECT_DIR/frontend" ]; then
        print_status "Собираем фронтенд с PWA поддержкой..."
        
        cd "$PROJECT_DIR/frontend"
        
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
    else
        print_warning "Директория frontend не найдена — пропускаем сборку"
    fi
}

# Выполнение миграций
run_migrations() {
    if [ -d "$PROJECT_DIR/backend" ]; then
        print_status "Выполняем миграции базы данных..."
        
        cd "$PROJECT_DIR/backend"
        # Активируем venv, если он есть
        if [ -f "venv/bin/activate" ]; then
            # shellcheck disable=SC1091
            source venv/bin/activate
        elif [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
            # shellcheck disable=SC1091
            source "$PROJECT_DIR/venv/bin/activate"
        else
            print_warning "Виртуальное окружение не найдено — пытаемся запустить системным Python"
        fi
        
        # Гарантируем корректные переменные окружения в backend/.env
        if [ -f ".env" ]; then
            sed -i "s/^DEBUG=.*/DEBUG=False/" .env || true
            grep -q "^ALLOWED_HOSTS=" .env || echo "ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0" >> .env
            if grep -q "^ALLOWED_HOSTS_EXTRA=" .env; then
                sed -i "s/^ALLOWED_HOSTS_EXTRA=.*/ALLOWED_HOSTS_EXTRA=${WORKERNET_ALLOWED_HOSTS_EXTRA:-}/" .env || true
            else
                echo "ALLOWED_HOSTS_EXTRA=${WORKERNET_ALLOWED_HOSTS_EXTRA:-}" >> .env
            fi
            grep -q "^DATABASE_URL=" .env || echo "DATABASE_URL=postgresql://workernet:workernet123@localhost:5432/workernet" >> .env
        fi

        if command -v python >/dev/null 2>&1; then
            python manage.py migrate --fake-initial || { print_error "Ошибка выполнения миграций"; return 1; }
            python manage.py collectstatic --noinput || true
            print_success "Миграции выполнены"
        else
            print_error "Python не найден в PATH — пропускаем миграции"
        fi
    else
        print_warning "Не удалось выполнить миграции - виртуальное окружение не найдено"
    fi
}

# Запуск сервисов
start_services() {
    print_status "Запускаем сервисы..."
    
    sudo systemctl start workernet-backend
    sudo systemctl start workernet-frontend
    
    # Ждем запуска сервисов
    sleep 5
    
    # Проверяем статус
    if systemctl is-active --quiet workernet-backend && systemctl is-active --quiet workernet-frontend; then
        print_success "Сервисы запущены успешно"
    else
        print_error "Ошибка запуска сервисов"
        print_status "Проверьте логи:"
        print_status "sudo journalctl -u workernet-backend -f"
        print_status "sudo journalctl -u workernet-frontend -f"
        exit 1
    fi
}

# Показ статуса
show_status() {
    echo
    print_success "Обновление завершено!"
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
    echo "⚠️  Для доступа извне замените ${SERVER_DOMAIN_OR_IP} на ваш домен или IP-адрес"
    echo
    echo "=== Управление сервисами ==="
    echo "Перезапуск: sudo systemctl restart workernet-backend workernet-frontend"
    echo "Статус: sudo systemctl status workernet-backend workernet-frontend"
    echo "Логи: sudo journalctl -u workernet-backend -f"
}

# Основная функция
main() {
    print_status "Запуск быстрого обновления WorkerNet Portal..."
    echo

    # Самообновление (при запросе)
    if [ "${WORKERNET_SELF_UPDATE:-0}" = "1" ] || [ "${1:-}" = "--self-update" ]; then
      self_update_script "$@"
    fi
    
    # Находим директорию проекта
    find_project_directory
    
    # Проверяем обновления
    if ! check_for_updates; then
        exit 0
    fi
    
    # Подтверждение обновления
    if [[ -z "${CI:-}" && -z "${WORKERNET_NONINTERACTIVE:-}" ]]; then
        echo
        read -p "Продолжить обновление? (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            print_status "Обновление отменено пользователем"
            exit 0
        fi
    fi
    
    # Выполняем обновление
    stop_services
    update_code
    update_python_deps
    update_nodejs_deps
    build_frontend
    run_migrations
    start_services
    show_status
}

# Обработка аргументов
case "${1:-}" in
    --help|-h)
        echo "Скрипт быстрого обновления WorkerNet Portal"
        echo
        echo "Использование: $0 [опции]"
        echo
        echo "Опции:"
        echo "  --help, -h     Показать эту справку"
        echo "  --check        Только проверить наличие обновлений"
        echo "  --force        Принудительное обновление без проверки"
        echo
        echo "Подсказка: при ошибке 'Permission denied' запустите так: bash ./scripts/quick-update.sh"
        echo
        echo "Переменные окружения:"
        echo "  WORKERNET_NONINTERACTIVE=1  Неинтерактивный режим"
        echo
        exit 0
        ;;
    --check)
        find_project_directory
        if check_for_updates; then
            print_warning "Доступны обновления"
            exit 1
        else
            print_success "Обновления не найдены"
            exit 0
        fi
        ;;
    --force)
        print_warning "Принудительное обновление"
        find_project_directory
        stop_services
        update_code
        update_python_deps
        update_nodejs_deps
        build_frontend
        run_migrations
        start_services
        show_status
        ;;
    --self-update)
        # Явный вызов самообновления
        WORKERNET_SELF_UPDATE=1 exec bash "$0" "$@"
        ;;
    *)
        main "$@"
        ;;
esac
