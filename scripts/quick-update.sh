#!/bin/bash

# УСТАРЕЛ: Используйте universal-install-update.sh
# Этот скрипт устарел и будет заменен на universal-install-update.sh

echo "[ВНИМАНИЕ] Этот скрипт устарел!"
echo "[ИНФО] Используйте новый универсальный скрипт:"
echo "  ./scripts/universal-install-update.sh"
echo
echo "[ИНФО] Перенаправляем на универсальный скрипт..."

# Перенаправляем на универсальный скрипт
exec ./scripts/universal-install-update.sh "$@"

# Скрипт быстрого обновления WorkerNet Portal (УСТАРЕЛ)
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

# Автоматическая проверка обновлений (при каждом запуске)
auto_check_updates() {
  # Проверяем только если не отключено явно
  if [ "${WORKERNET_NO_AUTO_UPDATE:-0}" = "1" ]; then
    return 0
  fi
  
  # Проверяем не чаще чем раз в день
  local last_check_file="/tmp/.workernet_last_update_check"
  local now=$(date +%s)
  local last_check=0
  
  if [ -f "$last_check_file" ]; then
    last_check=$(cat "$last_check_file" 2>/dev/null || echo "0")
  fi
  
  # Проверяем, прошло ли 24 часа (86400 секунд)
  if [ $((now - last_check)) -lt 86400 ]; then
    return 0
  fi
  
  # Сохраняем время последней проверки
  echo "$now" > "$last_check_file" 2>/dev/null || true
  
  print_status "Автоматическая проверка обновлений скриптов..."
  
  # Проверяем обновления без перезапуска
  SCRIPT_PATH="$0"
  if command -v readlink >/dev/null 2>&1; then
    SCRIPT_PATH="$(readlink -f "$SCRIPT_PATH" 2>/dev/null || echo "$SCRIPT_PATH")"
  fi

  RAW_BRANCH="${WORKERNET_BRANCH:-main}"
  RAW_URL="${WORKERNET_RAW_QUICK_URL:-https://raw.githubusercontent.com/apelsin349/portal-support-ERP-WorkerNet/${RAW_BRANCH}/scripts/quick-update.sh}"

  TMP_FILE="/tmp/quick-update-check.$$"
  if curl -fsSL "$RAW_URL" -o "$TMP_FILE" 2>/dev/null; then
    if ! cmp -s "$TMP_FILE" "$SCRIPT_PATH"; then
      print_warning "Доступна новая версия quick-update.sh"
      print_status "Для обновления запустите: $0 --self-update"
    fi
    rm -f "$TMP_FILE"
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
        # Проверяем, что название ветки не пустое после очистки
        if [ -z "$SELECTED_BRANCH" ] || [ "$SELECTED_BRANCH" = "" ]; then
            print_error "Название ветки пустое или содержит только пробелы"
            return 1
        fi
        print_status "Выбрана ветка: $SELECTED_BRANCH"
        return 0
    fi
    
    # Если ветка указана через переменную окружения
    if [ -n "${WORKERNET_BRANCH:-}" ]; then
        SELECTED_BRANCH=$(echo "$WORKERNET_BRANCH" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
        # Проверяем, что название ветки не пустое после очистки
        if [ -z "$SELECTED_BRANCH" ] || [ "$SELECTED_BRANCH" = "" ]; then
            print_error "Название ветки из переменной окружения пустое или содержит только пробелы"
            return 1
        fi
        print_status "Выбрана ветка из переменной окружения: $SELECTED_BRANCH"
        return 0
    fi
    
    cd "$PROJECT_DIR"
    
    # Получаем текущую ветку
    local current_branch
    current_branch=$(git branch --show-current 2>/dev/null || git rev-parse --abbrev-ref HEAD)
    
    # Получаем список доступных веток
    local available_branches
    available_branches=$(git branch -r | grep -v HEAD | sed 's/origin\///' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | grep -v '^[[:space:]]*$' | sort -u)
    
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
    local_branches=$(git branch | sed 's/^\*//' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | grep -v "^$" | grep -v '^[[:space:]]*$')
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
            SELECTED_BRANCH=$(echo "$available_branches" | sed -n "${choice}p" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
            if [ -n "$SELECTED_BRANCH" ] && [ "$SELECTED_BRANCH" != "" ]; then
                break
            else
                print_error "Неверный номер ветки"
            fi
        else
            # Если введено название ветки - очищаем от пробелов
            choice=$(echo "$choice" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
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
    
    # Проверяем, что название ветки не пустое
    if [ -z "$SELECTED_BRANCH" ] || [ "$SELECTED_BRANCH" = "" ]; then
        print_error "Название ветки пустое или содержит только пробелы"
        return 1
    fi
    
    # Проверяем, существует ли выбранная ветка на удаленном репозитории
    if ! git show-ref --verify --quiet "refs/remotes/origin/$SELECTED_BRANCH"; then
        print_error "Ветка '$SELECTED_BRANCH' не найдена на удаленном репозитории"
        print_status "Доступные ветки:"
        git branch -r | grep -v HEAD | sed 's/origin\///' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | grep -v '^[[:space:]]*$' | sort -u | sed 's/^/  - /'
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
                git branch -r | grep -v HEAD | sed 's/origin\///' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | grep -v '^[[:space:]]*$' | sort -u | sed 's/^/  - /'
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

    # Проверяем, нужно ли обновлять зависимости Python
    REQ_PRIMARY="$PROJECT_DIR/requirements.txt"
    REQ_SECONDARY="$PROJECT_DIR/backend/requirements.txt"
    REQUIREMENTS_HASH_FILE="$VENV_DIR/.requirements_hash"
    
    NEED_UPDATE=false
    FORCE_UPDATE=false
    
    # Проверяем флаг принудительного обновления
    if [ "$1" = "--force" ] || [ "$FORCE_UPDATE_DEPS" = "true" ]; then
        FORCE_UPDATE=true
        print_status "Принудительное обновление зависимостей Python..."
    fi
    
    # Проверяем, изменились ли файлы requirements (используем хеш содержимого)
    if [ -f "$REQ_PRIMARY" ]; then
        CURRENT_HASH=$(sha256sum "$REQ_PRIMARY" 2>/dev/null | cut -d' ' -f1)
        if [ ! -f "$REQUIREMENTS_HASH_FILE" ] || [ "$CURRENT_HASH" != "$(cat "$REQUIREMENTS_HASH_FILE" 2>/dev/null | cut -d' ' -f1)" ]; then
            NEED_UPDATE=true
        fi
    elif [ -f "$REQ_SECONDARY" ]; then
        CURRENT_HASH=$(sha256sum "$REQ_SECONDARY" 2>/dev/null | cut -d' ' -f1)
        if [ ! -f "$REQUIREMENTS_HASH_FILE" ] || [ "$CURRENT_HASH" != "$(cat "$REQUIREMENTS_HASH_FILE" 2>/dev/null | cut -d' ' -f1)" ]; then
            NEED_UPDATE=true
        fi
    fi
    
    if [ "$NEED_UPDATE" = true ] || [ "$FORCE_UPDATE" = true ]; then
        if [ "$FORCE_UPDATE" = true ]; then
            print_status "Принудительно обновляем зависимости Python..."
        else
            print_status "Обнаружены изменения в requirements.txt, обновляем зависимости Python..."
        fi
        
        # Активируем окружение
        # shellcheck disable=SC1090
        source "$VENV_DIR/bin/activate"

        # Очищаем кэш pip для свежей установки
        print_status "Очищаем кэш pip..."
        pip cache purge 2>/dev/null || true

        # Обновляем pip, setuptools и wheel
        print_status "Обновляем pip, setuptools и wheel..."
        pip install -U pip setuptools wheel

        # Ищем requirements: сначала в backend/, затем в корне
        DEV_PRIMARY="$PROJECT_DIR/requirements-dev.txt"
        DEV_SECONDARY="$PROJECT_DIR/backend/requirements-dev.txt"

        if [ -f "$REQ_PRIMARY" ]; then
            print_status "Устанавливаем зависимости из $REQ_PRIMARY..."
            pip install -r "$REQ_PRIMARY" --upgrade
            # Сохраняем хеш файла
            sha256sum "$REQ_PRIMARY" > "$REQUIREMENTS_HASH_FILE" 2>/dev/null || true
        elif [ -f "$REQ_SECONDARY" ]; then
            print_status "Устанавливаем зависимости из $REQ_SECONDARY..."
            pip install -r "$REQ_SECONDARY" --upgrade
            # Сохраняем хеш файла
            sha256sum "$REQ_SECONDARY" > "$REQUIREMENTS_HASH_FILE" 2>/dev/null || true
        else
            print_warning "requirements.txt не найден ни в backend/, ни в корне — пропускаем установку основных зависимостей"
        fi

        if [ -f "$DEV_PRIMARY" ]; then
            print_status "Устанавливаем dev зависимости из $DEV_PRIMARY..."
            pip install -r "$DEV_PRIMARY" --upgrade
        elif [ -f "$DEV_SECONDARY" ]; then
            print_status "Устанавливаем dev зависимости из $DEV_SECONDARY..."
            pip install -r "$DEV_SECONDARY" --upgrade
        fi

        # Проверяем устаревшие пакеты
        print_status "Проверяем устаревшие пакеты..."
        pip list --outdated 2>/dev/null | head -10 || true

        print_success "Зависимости Python обновлены"
    else
        print_status "Зависимости Python актуальны, пропускаем обновление"
    fi
}

# Обновление зависимостей Node.js
update_nodejs_deps() {
    if [ -d "$PROJECT_DIR/frontend" ]; then
        cd "$PROJECT_DIR/frontend"
        
        # Проверяем, нужно ли обновлять зависимости Node.js
        PACKAGE_JSON="$PROJECT_DIR/frontend/package.json"
        PACKAGE_LOCK="$PROJECT_DIR/frontend/package-lock.json"
        NODE_HASH_FILE="$PROJECT_DIR/frontend/.node_deps_hash"
        
        NEED_UPDATE=false
        
        # Проверяем, изменились ли файлы зависимостей
        if [ ! -f "$NODE_HASH_FILE" ] || [ "$PACKAGE_JSON" -nt "$NODE_HASH_FILE" ] || [ "$PACKAGE_LOCK" -nt "$NODE_HASH_FILE" ]; then
            NEED_UPDATE=true
        fi
        
        if [ "$NEED_UPDATE" = true ]; then
            print_status "Обнаружены изменения в package.json/package-lock.json, обновляем зависимости Node.js..."
            npm update
            # Сохраняем хеш файлов
            sha256sum "$PACKAGE_JSON" "$PACKAGE_LOCK" > "$NODE_HASH_FILE" 2>/dev/null || true
            print_success "Зависимости Node.js обновлены"
        else
            print_status "Зависимости Node.js актуальны, пропускаем обновление"
        fi
    else
        print_warning "Директория frontend не найдена"
    fi
}

# Сборка фронтенда с PWA
build_frontend() {
    if [ -d "$PROJECT_DIR/frontend" ]; then
        print_status "Собираем фронтенд с PWA поддержкой..."
        
        cd "$PROJECT_DIR/frontend"
        
        # Устанавливаем зависимости для генерации иконок (если нужно)
        if [ -f "scripts/install-icon-deps.js" ] && [ ! -d "node_modules/sharp" ]; then
            print_status "Устанавливаем зависимости для генерации иконок..."
            node scripts/install-icon-deps.js || print_warning "Не удалось установить зависимости для иконок"
        fi
        
        # Генерируем иконки для PWA (только если нужно)
        if [ -f "scripts/generate-icons.js" ]; then
            print_status "Проверяем необходимость генерации иконок PWA..."
            node scripts/generate-icons.js || print_warning "Не удалось сгенерировать иконки PWA"
        fi
        
        # Собираем фронтенд для production
        print_status "Собираем фронтенд для production..."
        
        # Исправляем права доступа к webpack и другим инструментам
        if [ -d "node_modules/.bin" ]; then
            print_status "Исправляем права доступа к инструментам сборки..."
            find node_modules/.bin -type f -name "*" -exec chmod +x {} \; 2>/dev/null || true
        fi
        
        # Пробуем разные способы сборки
        if npm run build; then
            print_success "Фронтенд собран успешно"
        elif npx webpack --mode production; then
            print_success "Фронтенд собран через npx"
        elif node_modules/.bin/webpack --mode production; then
            print_success "Фронтенд собран через прямой вызов"
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
            # Используем быстрый скрипт исправления миграций
            if [ -f "../scripts/quick-migration-fix.sh" ]; then
                print_status "Используем быстрый скрипт исправления миграций..."
                bash ../scripts/quick-migration-fix.sh
            elif [ -f "../scripts/ubuntu-migration-fix.sh" ]; then
                print_status "Используем Ubuntu скрипт исправления миграций..."
                bash ../scripts/ubuntu-migration-fix.sh
            elif [ -f "../scripts/emergency-migration-fix.sh" ]; then
                print_status "Используем экстренный скрипт исправления миграций..."
                bash ../scripts/emergency-migration-fix.sh
            else
                # Резервный метод исправления
                print_status "Исправляем проблему с миграциями (резервный метод)..."
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
                
                # Удаляем проблемные записи миграций
                python manage.py dbshell << 'EOF' 2>/dev/null || true
DELETE FROM django_migrations 
WHERE app = 'app' AND (name LIKE '%0008%' OR name LIKE '%0009%');
EOF
                
                # Создаем отсутствующие таблицы
                python manage.py dbshell << 'EOF' 2>/dev/null || true
CREATE TABLE IF NOT EXISTS agent_ratings (
    id BIGSERIAL PRIMARY KEY,
    agent_id BIGINT NOT NULL,
    rated_by_id BIGINT NOT NULL,
    ticket_id BIGINT NOT NULL,
    professionalism_rating INTEGER NOT NULL CHECK (professionalism_rating >= 1 AND professionalism_rating <= 5),
    knowledge_rating INTEGER NOT NULL CHECK (knowledge_rating >= 1 AND knowledge_rating <= 5),
    communication_rating INTEGER NOT NULL CHECK (communication_rating >= 1 AND communication_rating <= 5),
    problem_solving_rating INTEGER NOT NULL CHECK (problem_solving_rating >= 1 AND problem_solving_rating <= 5),
    overall_rating INTEGER NOT NULL CHECK (overall_rating >= 1 AND overall_rating <= 5),
    comment TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (agent_id, rated_by_id, ticket_id)
);

CREATE TABLE IF NOT EXISTS incidents (
    id BIGSERIAL PRIMARY KEY,
    incident_id VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(10) NOT NULL CHECK (severity IN ('P1', 'P2', 'P3', 'P4')),
    status VARCHAR(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'identified', 'monitoring', 'resolved', 'closed')),
    category VARCHAR(20) NOT NULL CHECK (category IN ('infrastructure', 'application', 'security', 'data', 'integration', 'user_experience')),
    reported_by_id BIGINT NOT NULL,
    assigned_to_id BIGINT,
    tenant_id BIGINT NOT NULL,
    affected_services JSONB NOT NULL DEFAULT '[]',
    business_impact TEXT NOT NULL DEFAULT '',
    user_impact TEXT NOT NULL DEFAULT '',
    detected_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    response_time_minutes INTEGER,
    resolution_time_minutes INTEGER,
    sla_breached BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    custom_fields JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS incident_attachments (
    id BIGSERIAL PRIMARY KEY,
    incident_id BIGINT NOT NULL,
    uploaded_by_id BIGINT NOT NULL,
    file VARCHAR(100) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS incident_updates (
    id BIGSERIAL PRIMARY KEY,
    incident_id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    update_type VARCHAR(20) NOT NULL CHECK (update_type IN ('status_change', 'investigation', 'resolution', 'communication', 'escalation')),
    is_public BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS incident_timeline (
    id BIGSERIAL PRIMARY KEY,
    incident_id BIGINT NOT NULL,
    event_type VARCHAR(30) NOT NULL CHECK (event_type IN ('created', 'assigned', 'status_changed', 'escalated', 'resolved', 'closed', 'comment_added', 'attachment_added')),
    description TEXT NOT NULL,
    author_id BIGINT,
    metadata JSONB NOT NULL DEFAULT '{}',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS incident_escalations (
    id BIGSERIAL PRIMARY KEY,
    incident_id BIGINT NOT NULL,
    level INTEGER NOT NULL,
    reason TEXT NOT NULL,
    escalated_to_id BIGINT NOT NULL,
    escalated_by_id BIGINT NOT NULL,
    escalated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_acknowledged BOOLEAN NOT NULL DEFAULT FALSE,
    acknowledged_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS incident_slas (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    severity VARCHAR(10) NOT NULL CHECK (severity IN ('P1', 'P2', 'P3', 'P4')),
    response_time_minutes INTEGER NOT NULL,
    resolution_time_minutes INTEGER NOT NULL,
    tenant_id BIGINT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, severity)
);

CREATE TABLE IF NOT EXISTS app_incident_tags (
    id BIGSERIAL PRIMARY KEY,
    incident_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    UNIQUE (incident_id, tag_id)
);

-- Создаем запись о выполненной миграции 0008
INSERT INTO django_migrations (app, name, applied) 
VALUES ('app', '0008_agentrating_incident_incidentattachment_and_more', NOW())
ON CONFLICT (app, name) DO NOTHING;
EOF
                
                # Очищаем проблемные записи миграций и создаем новые
                python manage.py dbshell -c "DELETE FROM django_migrations WHERE app = 'app' AND name != '0001_initial';" 2>/dev/null || true
                python manage.py migrate app 0001 --fake 2>/dev/null || true
                python manage.py makemigrations app 2>/dev/null || true
                python manage.py migrate 2>/dev/null || true
            fi
            
            # Выполняем финальные миграции
            print_status "Выполняем финальные миграции..."
            python manage.py migrate || { print_error "Ошибка выполнения миграций"; return 1; }
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

    # Автоматическая проверка обновлений (если не отключена)
    auto_check_updates

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
        echo "  --force-deps   Принудительное обновление зависимостей"
        echo "  --branch BRANCH Указать ветку для обновления"
        echo "  --create-branch Создать локальную ветку из удаленной"
        echo "  --debug        Показать диагностическую информацию"
        echo "  --self-update  Обновить сам скрипт quick-update.sh"
        echo "  --check-scripts Проверить актуальность всех скриптов"
        echo "  --update-scripts Обновить все устаревшие скрипты"
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
    --force-deps)
        print_warning "Принудительное обновление зависимостей"
        find_project_directory
        FORCE_UPDATE_DEPS=true
        stop_services
        update_code
        update_python_deps --force
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
    --check-scripts)
        # Проверка всех скриптов на самообновление
        if [ -f "scripts/check-scripts-self-update.sh" ]; then
            bash scripts/check-scripts-self-update.sh check
        else
            print_error "Скрипт check-scripts-self-update.sh не найден"
            exit 1
        fi
        ;;
    --update-scripts)
        # Обновление всех скриптов
        if [ -f "scripts/check-scripts-self-update.sh" ]; then
            bash scripts/check-scripts-self-update.sh update
        else
            print_error "Скрипт check-scripts-self-update.sh не найден"
            exit 1
        fi
        ;;
    *)
        main "$@"
        ;;
esac
