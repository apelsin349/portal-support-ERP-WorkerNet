#!/bin/bash

# Скрипт для диагностики и исправления проблем с ветками Git
# Используется для решения проблем с лишними пробелами и некорректными названиями веток

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
SCRIPT_VERSION="2025-01-27.1"

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

# Диагностика проблем с ветками
diagnose_branch_issues() {
    print_status "Диагностика проблем с ветками Git..."
    
    cd "$PROJECT_DIR"
    
    echo
    print_status "=== Информация о репозитории ==="
    echo "Директория: $(pwd)"
    echo "Git версия: $(git --version 2>/dev/null || echo 'недоступна')"
    
    echo
    print_status "=== Удаленные репозитории ==="
    git remote -v 2>/dev/null || echo "недоступны"
    
    echo
    print_status "=== Текущая ветка ==="
    local current_branch
    current_branch=$(git branch --show-current 2>/dev/null || git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "недоступна")
    echo "Текущая ветка: '$current_branch'"
    
    # Проверяем на лишние пробелы в текущей ветке
    if [[ "$current_branch" =~ ^[[:space:]]+.* ]] || [[ "$current_branch" =~ .*[[:space:]]+$ ]]; then
        print_warning "Обнаружены лишние пробелы в названии текущей ветки!"
        echo "Исходное название: '$current_branch'"
        local clean_branch=$(echo "$current_branch" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
        echo "Очищенное название: '$clean_branch'"
    fi
    
    echo
    print_status "=== Локальные ветки ==="
    local local_branches
    local_branches=$(git branch 2>/dev/null || echo "недоступны")
    echo "$local_branches"
    
    # Проверяем локальные ветки на лишние пробелы
    echo "$local_branches" | while read -r branch; do
        if [[ "$branch" =~ ^[[:space:]]+.* ]] || [[ "$branch" =~ .*[[:space:]]+$ ]]; then
            print_warning "Обнаружены лишние пробелы в локальной ветке: '$branch'"
        fi
    done
    
    echo
    print_status "=== Удаленные ветки ==="
    local remote_branches
    remote_branches=$(git branch -r 2>/dev/null || echo "недоступны")
    echo "$remote_branches"
    
    # Проверяем удаленные ветки на лишние пробелы
    echo "$remote_branches" | while read -r branch; do
        if [[ "$branch" =~ ^[[:space:]]+.* ]] || [[ "$branch" =~ .*[[:space:]]+$ ]]; then
            print_warning "Обнаружены лишние пробелы в удаленной ветке: '$branch'"
        fi
    done
    
    echo
    print_status "=== Статус рабочей директории ==="
    git status --porcelain 2>/dev/null || echo "недоступен"
    
    echo
    print_status "=== Последний коммит ==="
    git log -1 --oneline 2>/dev/null || echo "недоступен"
}

# Исправление проблем с ветками
fix_branch_issues() {
    print_status "Исправление проблем с ветками..."
    
    cd "$PROJECT_DIR"
    
    # Обновляем удаленные ссылки
    print_status "Обновляем удаленные ссылки..."
    git fetch --all --prune --force 2>/dev/null || true
    git remote update 2>/dev/null || true
    
    # Получаем текущую ветку
    local current_branch
    current_branch=$(git branch --show-current 2>/dev/null || git rev-parse --abbrev-ref HEAD 2>/dev/null)
    
    # Проверяем, находимся ли мы в detached HEAD состоянии
    if [ "$current_branch" = "HEAD" ] || [[ "$current_branch" =~ ^[0-9a-f]{7,}$ ]]; then
        print_warning "Обнаружено состояние detached HEAD"
        print_status "Попытка переключения на ветку main..."
        
        if git checkout main 2>/dev/null; then
            print_success "Переключились на ветку main"
        elif git checkout new-frontend 2>/dev/null; then
            print_success "Переключились на ветку new-frontend"
        else
            print_error "Не удалось переключиться на стандартные ветки"
            print_status "Доступные ветки:"
            git branch -a 2>/dev/null || true
            return 1
        fi
    fi
    
    # Очищаем кэш Git
    print_status "Очищаем кэш Git..."
    git gc --prune=now 2>/dev/null || true
    
    print_success "Проблемы с ветками исправлены"
}

# Тестирование работы с ветками
test_branch_operations() {
    print_status "Тестирование операций с ветками..."
    
    cd "$PROJECT_DIR"
    
    # Получаем список веток с правильной обработкой
    print_status "Тестируем получение списка веток..."
    
    local available_branches
    available_branches=$(git branch -r | grep -v HEAD | sed 's/origin\///' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | grep -v '^[[:space:]]*$' | sort -u)
    
    print_status "Доступные ветки (обработанные):"
    echo "$available_branches" | nl -w2 -s') '
    
    # Тестируем проверку существования ветки
    if [ -n "$available_branches" ]; then
        local test_branch
        test_branch=$(echo "$available_branches" | head -1 | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
        
        if [ -n "$test_branch" ]; then
            print_status "Тестируем проверку ветки: '$test_branch'"
            
            if git show-ref --verify --quiet "refs/remotes/origin/$test_branch"; then
                print_success "Ветка '$test_branch' найдена на удаленном репозитории"
            else
                print_error "Ветка '$test_branch' не найдена на удаленном репозитории"
            fi
        fi
    fi
    
    print_success "Тестирование завершено"
}

# Основная функция
main() {
    print_status "Запуск диагностики и исправления проблем с ветками Git..."
    echo
    
    # Находим директорию проекта
    find_project_directory
    
    # Диагностируем проблемы
    diagnose_branch_issues
    
    echo
    print_warning "Обнаружены проблемы с ветками?"
    read -p "Выполнить автоматическое исправление? (y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        fix_branch_issues
        echo
        test_branch_operations
    else
        print_status "Автоматическое исправление пропущено"
    fi
    
    echo
    print_success "Диагностика завершена!"
    echo
    print_status "Рекомендации:"
    echo "1. Используйте обновленный скрипт quick-update.sh"
    echo "2. При выборе ветки вводите точное название без лишних пробелов"
    echo "3. Если проблемы повторяются, выполните: $0 --fix"
}

# Обработка аргументов
case "${1:-}" in
    --help|-h)
        echo "Скрипт диагностики и исправления проблем с ветками Git"
        echo
        echo "Использование: $0 [опции]"
        echo
        echo "Опции:"
        echo "  --help, -h     Показать эту справку"
        echo "  --diagnose     Только диагностика без исправления"
        echo "  --fix          Только исправление без диагностики"
        echo "  --test         Только тестирование операций с ветками"
        echo
        echo "Примеры:"
        echo "  $0              Полная диагностика с возможностью исправления"
        echo "  $0 --diagnose   Только диагностика проблем"
        echo "  $0 --fix        Автоматическое исправление"
        echo "  $0 --test       Тестирование операций с ветками"
        echo
        exit 0
        ;;
    --diagnose)
        find_project_directory
        diagnose_branch_issues
        ;;
    --fix)
        find_project_directory
        fix_branch_issues
        ;;
    --test)
        find_project_directory
        test_branch_operations
        ;;
    *)
        main "$@"
        ;;
esac
