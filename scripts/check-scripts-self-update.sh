#!/bin/bash

# Скрипт для проверки самообновления всех скриптов WorkerNet Portal
# Проверяет, какие скрипты поддерживают самообновление и их актуальность

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для цветного вывода
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

# Конфигурация
REPO_URL="https://github.com/apelsin349/portal-support-ERP-WorkerNet"
REPO_BRANCH="${WORKERNET_BRANCH:-main}"
RAW_BASE_URL="https://raw.githubusercontent.com/apelsin349/portal-support-ERP-WorkerNet/${REPO_BRANCH}"

# Список скриптов для проверки
SCRIPTS_TO_CHECK=(
    "scripts/universal-install-update.sh"
    "scripts/start-docker.sh"
    "scripts/check-dependencies.sh"
    "scripts/check-database.sh"
    "scripts/setup-database.sh"
    "scripts/setup-redis.sh"
)

# Функция для проверки самообновления скрипта
check_script_self_update() {
    local script_path="$1"
    local script_name=$(basename "$script_path")
    
    print_status "Проверяем $script_name..."
    
    # Проверяем, существует ли скрипт
    if [ ! -f "$script_path" ]; then
        print_warning "$script_name не найден"
        return 1
    fi
    
    # Проверяем, поддерживает ли скрипт самообновление
    if ! grep -q "self_update\|self-update\|SELF_UPDATE" "$script_path"; then
        print_warning "$script_name не поддерживает самообновление"
        return 1
    fi
    
    # Проверяем версию скрипта
    local current_version=""
    if grep -q "SCRIPT_VERSION" "$script_path"; then
        current_version=$(grep "SCRIPT_VERSION" "$script_path" | head -1 | sed 's/.*SCRIPT_VERSION="\([^"]*\)".*/\1/')
        print_status "Текущая версия $script_name: $current_version"
    else
        print_warning "$script_name не имеет версии"
    fi
    
    # Проверяем актуальность скрипта
    local raw_url="${RAW_BASE_URL}/${script_path}"
    local tmp_file="/tmp/${script_name}.$$"
    
    if curl -fsSL "$raw_url" -o "$tmp_file" 2>/dev/null; then
        if cmp -s "$tmp_file" "$script_path"; then
            print_success "$script_name актуален"
        else
            print_warning "$script_name устарел - доступна новая версия"
            
            # Показываем различия (первые 5 строк)
            if command -v diff >/dev/null 2>&1; then
                print_status "Различия (первые 5 строк):"
                diff -u "$script_path" "$tmp_file" | head -10 || true
            fi
        fi
        rm -f "$tmp_file"
    else
        print_error "Не удалось загрузить $script_name с GitHub"
    fi
}

# Функция для обновления скрипта
update_script() {
    local script_path="$1"
    local script_name=$(basename "$script_path")
    
    print_status "Обновляем $script_name..."
    
    local raw_url="${RAW_BASE_URL}/${script_path}"
    local tmp_file="/tmp/${script_name}.$$"
    
    if curl -fsSL "$raw_url" -o "$tmp_file"; then
        chmod +x "$tmp_file" 2>/dev/null || true
        
        # Пытаемся сохранить с sudo, если нужно
        if sudo cp -f "$tmp_file" "$script_path" 2>/dev/null || cp -f "$tmp_file" "$script_path"; then
            print_success "$script_name обновлен успешно"
            rm -f "$tmp_file"
            return 0
        else
            print_error "Не удалось обновить $script_name"
            rm -f "$tmp_file"
            return 1
        fi
    else
        print_error "Не удалось загрузить $script_name с GitHub"
        return 1
    fi
}

# Функция для показа справки
show_help() {
    echo "Скрипт проверки самообновления WorkerNet Portal"
    echo
    echo "Использование: $0 [КОМАНДА]"
    echo
    echo "Команды:"
    echo "  check     Проверить актуальность всех скриптов (по умолчанию)"
    echo "  update    Обновить все устаревшие скрипты"
    echo "  list      Показать список скриптов для проверки"
    echo "  help      Показать эту справку"
    echo
    echo "Примеры:"
    echo "  $0                    # Проверить все скрипты"
    echo "  $0 check              # Проверить все скрипты"
    echo "  $0 update             # Обновить все скрипты"
    echo "  $0 list               # Показать список скриптов"
    echo
    echo "Переменные окружения:"
    echo "  WORKERNET_BRANCH      Ветка Git для проверки (по умолчанию: main)"
}

# Функция для показа списка скриптов
show_scripts_list() {
    print_status "Скрипты для проверки самообновления:"
    echo
    for script in "${SCRIPTS_TO_CHECK[@]}"; do
        local script_name=$(basename "$script")
        local has_self_update="❌"
        
        if [ -f "$script" ] && grep -q "self_update\|self-update\|SELF_UPDATE" "$script"; then
            has_self_update="✅"
        fi
        
        echo "  $has_self_update $script_name"
    done
    echo
    print_status "✅ - поддерживает самообновление"
    print_status "❌ - не поддерживает самообновление"
}

# Основная функция
main() {
    local command="${1:-check}"
    
    case "$command" in
        "check")
            print_status "Проверяем самообновление скриптов WorkerNet Portal..."
            echo
            
            local updated_count=0
            local total_count=0
            
            for script in "${SCRIPTS_TO_CHECK[@]}"; do
                if [ -f "$script" ]; then
                    total_count=$((total_count + 1))
                    if check_script_self_update "$script"; then
                        updated_count=$((updated_count + 1))
                    fi
                    echo
                fi
            done
            
            echo "=== Результат проверки ==="
            print_status "Проверено скриптов: $total_count"
            print_success "Актуальных скриптов: $updated_count"
            print_warning "Устаревших скриптов: $((total_count - updated_count))"
            ;;
            
        "update")
            print_status "Обновляем устаревшие скрипты..."
            echo
            
            local updated_count=0
            local total_count=0
            
            for script in "${SCRIPTS_TO_CHECK[@]}"; do
                if [ -f "$script" ]; then
                    total_count=$((total_count + 1))
                    if update_script "$script"; then
                        updated_count=$((updated_count + 1))
                    fi
                    echo
                fi
            done
            
            echo "=== Результат обновления ==="
            print_status "Обработано скриптов: $total_count"
            print_success "Обновлено скриптов: $updated_count"
            ;;
            
        "list")
            show_scripts_list
            ;;
            
        "help"|"-h"|"--help")
            show_help
            ;;
            
        *)
            print_error "Неизвестная команда: $command"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Запуск основной функции
main "$@"
