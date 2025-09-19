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

# Выбор ветки Git
select_branch() {
    local target_branch="${1:-}"
    
    # Если ветка указана через аргумент или переменную окружения
    if [ -n "$target_branch" ]; then
        SELECTED_BRANCH=$(echo "$target_branch" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
        print_status "Выбрана ветка: $SELECTED_BRANCH"
        return 0
    fi
    
    # Если ветка указана через переменную окружения
    if [ -n "${WORKERNET_BRANCH:-}" ]; then
        SELECTED_BRANCH=$(echo "$WORKERNET_BRANCH" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
        print_status "Выбрана ветка из переменной окружения: $SELECTED_BRANCH"
        return 0
    fi
    
    cd "$PROJECT_DIR"
    
    # Получаем текущую ветку
    local current_branch
    current_branch=$(git branch --show-current 2>/dev/null || git rev-parse --abbrev-ref HEAD)
    
    # Получаем список доступных веток
    local available_branches
    available_branches=$(git branch -r | grep -v HEAD | sed 's/origin\///' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | sort -u)
    
    # Если неинтерактивный режим, используем текущую ветку
    if [[ -n "${CI:-}" || -n "${WORKERNET_NONINTERACTIVE:-}" ]]; then
        SELECTED_BRANCH="$current_branch"
        print_status "Неинтерактивный режим: используем текущую ветку $SELECTED_BRANCH"
        return 0
    fi
    
    # Интерактивный выбор ветки
    echo
    print_status "Доступные удаленные ветки:"
    echo "$available_branches" | nl -w2 -s') '
    echo
    echo "Текущая ветка: $current_branch"
    
    # Показываем локальные ветки
    local local_branches
    local_branches=$(git branch | sed 's/^\*//' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | grep -v "^$")
    if [ -n "$local_branches" ]; then
        echo "Локальные ветки:"
        echo "$local_branches" | sed 's/^/  - /'
    fi
    echo
    
    while true; do
        read -p "Выберите ветку для обновления (номер или название, Enter для текущей): " choice
        
        # Если Enter - используем текущую ветку
        if [ -z "$choice" ]; then
            SELECTED_BRANCH="$current_branch"
            break
        fi
        
        # Если введен номер
        if [[ "$choice" =~ ^[0-9]+$ ]]; then
            SELECTED_BRANCH=$(echo "$available_branches" | sed -n "${choice}p")
            if [ -n "$SELECTED_BRANCH" ]; then
                break
            else
                print_error "Неверный номер ветки"
            fi
        else
            # Если введено название ветки
            if echo "$available_branches" | grep -q "^$choice$"; then
                SELECTED_BRANCH="$choice"
                break
            else
                print_error "Ветка '$choice' не найдена"
            fi
        fi
    done
    
    print_status "Выбрана ветка: $SELECTED_BRANCH"
}

# Проверка обновлений
check_for_updates() {
    print_status "Проверяем наличие обновлений в ветке '$SELECTED_BRANCH'..."
    
    cd "$PROJECT_DIR"
    
    # Получаем информацию о текущей ветке
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || git rev-parse --abbrev-ref HEAD)
    
    # Принудительно обновляем удаленные ссылки
    print_status "Обновляем удаленные ссылки..."
    git fetch --all --prune --force 2>/dev/null || true
    
    # Дополнительная синхронизация
    git remote update 2>/dev/null || true
    
    # Очищаем название ветки от лишних пробелов
    SELECTED_BRANCH=$(echo "$SELECTED_BRANCH" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
    
    # Проверяем, существует ли выбранная ветка на удаленном репозитории
    if ! git show-ref --verify --quiet "refs/remotes/origin/$SELECTED_BRANCH"; then
        print_error "Ветка '$SELECTED_BRANCH' не найдена на удаленном репозитории"
        print_status "Доступные ветки:"
        git branch -r | grep -v HEAD | sed 's/origin\///' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | sort -u | sed 's/^/  - /'
        return 1
    fi
    
    # Если мы не на выбранной ветке, переключаемся на неё
    if [ "$CURRENT_BRANCH" != "$SELECTED_BRANCH" ]; then
        print_status "Переключаемся на ветку '$SELECTED_BRANCH'..."
        
        # Сначала пытаемся переключиться на существующую локальную ветку
        if git checkout "$SELECTED_BRANCH" 2>/dev/null; then
            print_success "Переключились на существующую локальную ветку '$SELECTED_BRANCH'"
        else
            print_status "Локальная ветка '$SELECTED_BRANCH' не найдена, создаем из удаленной..."
            
            # Создаем локальную ветку из удаленной
            print_status "Проверяем удаленную ветку 'origin/$SELECTED_BRANCH'..."
            
            # Проверяем, что удаленная ветка действительно существует
            if ! git show-ref --verify --quiet "refs/remotes/origin/$SELECTED_BRANCH"; then
                print_error "Удаленная ветка 'origin/$SELECTED_BRANCH' не найдена"
                print_status "Доступные удаленные ветки:"
                git branch -r | grep -v HEAD | sed 's/origin\///' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | sort -u | sed 's/^/  - /'
                return 1
            fi
            
            # Показываем информацию об удаленной ветке
            local remote_commit
            remote_commit=$(git rev-parse "origin/$SELECTED_BRANCH" 2>/dev/null)
            print_status "Удаленная ветка найдена: $remote_commit"
            
            # Пытаемся создать локальную ветку
            if git checkout -b "$SELECTED_BRANCH" "origin/$SELECTED_BRANCH" 2>/dev/null; then
                print_success "Создали и переключились на ветку '$SELECTED_BRANCH'"
            else
                print_warning "Основной способ не сработал, пробуем альтернативный..."
                
                # Альтернативный способ: создаем ветку и затем устанавливаем upstream
                if git checkout -b "$SELECTED_BRANCH" 2>/dev/null; then
                    print_status "Создали локальную ветку '$SELECTED_BRANCH', устанавливаем upstream..."
                    if git branch --set-upstream-to="origin/$SELECTED_BRANCH" "$SELECTED_BRANCH" 2>/dev/null; then
                        print_status "Устанавливаем связь с удаленной веткой..."
                        git pull origin "$SELECTED_BRANCH" 2>/dev/null || true
                        print_success "Создали и настроили ветку '$SELECTED_BRANCH'"
                    else
                        print_error "Не удалось установить связь с удаленной веткой"
                        print_status "Проверяем статус Git:"
                        git status --porcelain 2>/dev/null || true
                        print_status "Проверяем рабочую директорию:"
                        git diff --name-only 2>/dev/null || true
                        print_status "Попробуйте выполнить команды вручную:"
                        echo "  git checkout -b $SELECTED_BRANCH"
                        echo "  git branch --set-upstream-to=origin/$SELECTED_BRANCH $SELECTED_BRANCH"
                        echo "  git pull origin $SELECTED_BRANCH"
                        return 1
                    fi
                else
                    print_error "Не удалось создать ветку '$SELECTED_BRANCH'"
                    print_status "Проверяем статус Git:"
                    git status --porcelain 2>/dev/null || true
                    print_status "Проверяем рабочую директорию:"
                    git diff --name-only 2>/dev/null || true
                    print_status "Попробуйте выполнить команду вручную:"
                    echo "  git checkout -b $SELECTED_BRANCH origin/$SELECTED_BRANCH"
                    return 1
                fi
            fi
        fi
    fi
    
    # Проверяем наличие новых коммитов в выбранной ветке
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse "origin/$SELECTED_BRANCH" 2>/dev/null)
    
    if [ "$LOCAL" = "$REMOTE" ]; then
        print_success "Обновления не найдены - ветка '$SELECTED_BRANCH' актуальна"
        return 1
    else
        print_warning "Найдены обновления в ветке '$SELECTED_BRANCH'"
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
    print_status "Обновляем код из репозитория (ветка: $SELECTED_BRANCH)..."
    
    cd "$PROJECT_DIR"
    
    # Сохраняем локальные изменения
    if ! git diff --quiet || ! git diff --cached --quiet; then
        print_warning "Обнаружены локальные изменения"
        git stash push -m "Auto-stash before update to $SELECTED_BRANCH $(date)" || true
    fi
    
    # Обновляем код
    git fetch --all --prune
    
    # Переключаемся на выбранную ветку если нужно
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || git rev-parse --abbrev-ref HEAD)
    if [ "$CURRENT_BRANCH" != "$SELECTED_BRANCH" ]; then
        print_status "Переключаемся на ветку '$SELECTED_BRANCH'..."
        
        # Сначала пытаемся переключиться на существующую локальную ветку
        if git checkout "$SELECTED_BRANCH" 2>/dev/null; then
            print_success "Переключились на существующую локальную ветку '$SELECTED_BRANCH'"
        else
            print_status "Локальная ветка '$SELECTED_BRANCH' не найдена, создаем из удаленной..."
            
            # Создаем локальную ветку из удаленной
            if git checkout -b "$SELECTED_BRANCH" "origin/$SELECTED_BRANCH" 2>/dev/null; then
                print_success "Создали и переключились на ветку '$SELECTED_BRANCH'"
            else
                print_warning "Не удалось переключиться на ветку '$SELECTED_BRANCH', продолжаем с текущей веткой '$CURRENT_BRANCH'"
            fi
        fi
    fi
    
    # Обновляем до последней версии выбранной ветки
    git reset --hard "origin/$SELECTED_BRANCH" 2>/dev/null || true
    git submodule update --init --recursive 2>/dev/null || true
    
    print_success "Код обновлен до ветки '$SELECTED_BRANCH'"
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
        
        # Исправляем права доступа к webpack
        if [ -f "node_modules/.bin/webpack" ]; then
            chmod +x node_modules/.bin/webpack 2>/dev/null || true
        fi
        
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
            # Исправляем проблему с несуществующим ограничением
            print_status "Исправляем проблему с миграциями..."
            python manage.py dbshell << 'EOF' 2>/dev/null || true
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'unique_username_per_tenant' 
        AND table_name = 'users'
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE users DROP CONSTRAINT unique_username_per_tenant;
        RAISE NOTICE 'Constraint unique_username_per_tenant dropped successfully';
    ELSE
        RAISE NOTICE 'Constraint unique_username_per_tenant does not exist, skipping';
    END IF;
END $$;
EOF
            
            # Проверяем конфликты миграций и исправляем их
            print_status "Проверяем конфликты миграций..."
            if python manage.py showmigrations app 2>/dev/null | grep -q "\[ \] 0008"; then
                print_status "Обнаружен конфликт миграций, исправляем..."
                # Помечаем все проблемные миграции как выполненные
                python manage.py migrate app 0008 --fake 2>/dev/null || true
                python manage.py migrate app 0009 --fake 2>/dev/null || true
                python manage.py migrate app 0010 --fake 2>/dev/null || true
            fi
            
            # Выполняем миграции
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
    
    # Выбираем ветку
    select_branch
    
    # Проверяем обновления
    if ! check_for_updates; then
        exit 0
    fi
    
    # Подтверждение обновления
    if [[ -z "${CI:-}" && -z "${WORKERNET_NONINTERACTIVE:-}" ]]; then
        echo
        print_warning "Обновление до ветки: $SELECTED_BRANCH"
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
        echo "  --branch BRANCH Указать ветку для обновления"
        echo "  --create-branch Создать локальную ветку из удаленной"
        echo "  --debug        Показать диагностическую информацию"
        echo
        echo "Подсказка: при ошибке 'Permission denied' запустите так: bash ./scripts/quick-update.sh"
        echo
        echo "Переменные окружения:"
        echo "  WORKERNET_NONINTERACTIVE=1  Неинтерактивный режим"
        echo "  WORKERNET_BRANCH=BRANCH     Ветка для обновления"
        echo
        echo "Примеры:"
        echo "  $0 --branch develop        Обновить до ветки develop"
        echo "  $0 --branch feature/new    Обновить до ветки feature/new"
        echo "  $0 --check --branch main   Проверить обновления в ветке main"
        echo "  $0 --create-branch new-feature Создать локальную ветку new-feature"
        echo "  $0 --debug                Показать диагностическую информацию"
        echo
        exit 0
        ;;
    --check)
        find_project_directory
        # Обработка аргумента --branch для --check
        if [ "${2:-}" = "--branch" ] && [ -n "${3:-}" ]; then
            select_branch "$3"
        else
            select_branch
        fi
        if check_for_updates; then
            print_warning "Доступны обновления в ветке '$SELECTED_BRANCH'"
            exit 1
        else
            print_success "Обновления не найдены в ветке '$SELECTED_BRANCH'"
            exit 0
        fi
        ;;
    --force)
        print_warning "Принудительное обновление"
        find_project_directory
        # Обработка аргумента --branch для --force
        if [ "${2:-}" = "--branch" ] && [ -n "${3:-}" ]; then
            select_branch "$3"
        else
            select_branch
        fi
        stop_services
        update_code
        update_python_deps
        update_nodejs_deps
        build_frontend
        run_migrations
        start_services
        show_status
        ;;
    --branch)
        if [ -z "${2:-}" ]; then
            print_error "Не указана ветка для --branch"
            echo "Использование: $0 --branch BRANCH_NAME"
            exit 1
        fi
        find_project_directory
        select_branch "$2"
        if check_for_updates; then
            # Подтверждение обновления
            if [[ -z "${CI:-}" && -z "${WORKERNET_NONINTERACTIVE:-}" ]]; then
                echo
                print_warning "Обновление до ветки: $SELECTED_BRANCH"
                read -p "Продолжить обновление? (y/N): " confirm
                if [[ ! $confirm =~ ^[Yy]$ ]]; then
                    print_status "Обновление отменено пользователем"
                    exit 0
                fi
            fi
            stop_services
            update_code
            update_python_deps
            update_nodejs_deps
            build_frontend
            run_migrations
            start_services
            show_status
        else
            print_success "Ветка '$SELECTED_BRANCH' уже актуальна"
        fi
        ;;
    --create-branch)
        if [ -z "${2:-}" ]; then
            print_error "Не указана ветка для --create-branch"
            echo "Использование: $0 --create-branch BRANCH_NAME"
            exit 1
        fi
        find_project_directory
        print_status "Создаем локальную ветку '$2' из удаленной..."
        cd "$PROJECT_DIR"
        git fetch --all --prune
        if git checkout -b "$2" "origin/$2" 2>/dev/null; then
            print_success "Локальная ветка '$2' создана и переключение выполнено"
        else
            print_error "Не удалось создать ветку '$2' из 'origin/$2'"
            print_status "Проверьте, что ветка '$2' существует на удаленном репозитории"
            exit 1
        fi
        ;;
    --debug)
        find_project_directory
        print_status "Диагностическая информация Git:"
        cd "$PROJECT_DIR"
        echo
        echo "=== Информация о репозитории ==="
        echo "Директория: $(pwd)"
        echo "Git версия: $(git --version 2>/dev/null || echo 'недоступна')"
        echo
        echo "=== Удаленные репозитории ==="
        git remote -v 2>/dev/null || echo "недоступны"
        echo
        echo "=== Текущая ветка ==="
        git branch --show-current 2>/dev/null || git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "недоступна"
        echo
        echo "=== Локальные ветки ==="
        git branch 2>/dev/null || echo "недоступны"
        echo
        echo "=== Удаленные ветки ==="
        git branch -r 2>/dev/null || echo "недоступны"
        echo
        echo "=== Статус рабочей директории ==="
        git status --porcelain 2>/dev/null || echo "недоступен"
        echo
        echo "=== Последний коммит ==="
        git log -1 --oneline 2>/dev/null || echo "недоступен"
        echo
        echo "=== Конфигурация Git ==="
        git config --list --local 2>/dev/null | head -10 || echo "недоступна"
        ;;
    --self-update)
        # Явный вызов самообновления
        WORKERNET_SELF_UPDATE=1 exec bash "$0" "$@"
        ;;
    *)
        main "$@"
        ;;
esac
