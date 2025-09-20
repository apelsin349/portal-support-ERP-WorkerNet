#!/bin/bash

# Диагностика проблем с переключением веток Git
# Используется для выявления причин, по которым не удается переключиться на ветку

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
        exit 1
    fi
    
    print_status "Найдена директория проекта: $PROJECT_DIR"
}

# Диагностика состояния Git
diagnose_git_status() {
    print_status "Диагностика состояния Git репозитория..."
    
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
    
    # Проверяем, находимся ли мы в detached HEAD состоянии
    if [ "$current_branch" = "HEAD" ] || [[ "$current_branch" =~ ^[0-9a-f]{7,}$ ]]; then
        print_warning "Обнаружено состояние detached HEAD"
        print_status "Текущий коммит: $(git rev-parse HEAD 2>/dev/null || echo 'недоступен')"
    fi
    
    echo
    print_status "=== Локальные ветки ==="
    git branch 2>/dev/null || echo "недоступны"
    
    echo
    print_status "=== Удаленные ветки ==="
    git branch -r 2>/dev/null || echo "недоступны"
    
    echo
    print_status "=== Статус рабочей директории ==="
    local git_status
    git_status=$(git status --porcelain 2>/dev/null || echo "недоступен")
    if [ "$git_status" = "недоступен" ]; then
        echo "$git_status"
    elif [ -z "$git_status" ]; then
        echo "Рабочая директория чистая"
    else
        echo "$git_status"
        print_warning "Обнаружены незафиксированные изменения"
    fi
    
    echo
    print_status "=== Последний коммит ==="
    git log -1 --oneline 2>/dev/null || echo "недоступен"
    
    echo
    print_status "=== Проверка ветки new-frontend ==="
    
    # Проверяем локальную ветку new-frontend
    if git show-ref --verify --quiet "refs/heads/new-frontend"; then
        print_success "Локальная ветка 'new-frontend' существует"
        echo "Коммит локальной ветки: $(git rev-parse refs/heads/new-frontend 2>/dev/null || echo 'недоступен')"
    else
        print_warning "Локальная ветка 'new-frontend' не существует"
    fi
    
    # Проверяем удаленную ветку new-frontend
    if git show-ref --verify --quiet "refs/remotes/origin/new-frontend"; then
        print_success "Удаленная ветка 'origin/new-frontend' существует"
        echo "Коммит удаленной ветки: $(git rev-parse refs/remotes/origin/new-frontend 2>/dev/null || echo 'недоступен')"
    else
        print_error "Удаленная ветка 'origin/new-frontend' не существует"
    fi
    
    # Проверяем, есть ли конфликты
    if [ -f ".git/MERGE_HEAD" ]; then
        print_warning "Обнаружен активный merge - возможно, есть конфликты"
    fi
    
    if [ -f ".git/CHERRY_PICK_HEAD" ]; then
        print_warning "Обнаружен активный cherry-pick"
    fi
    
    if [ -f ".git/REBASE_HEAD" ]; then
        print_warning "Обнаружен активный rebase"
    fi
}

# Тестирование переключения на ветку
test_branch_switch() {
    print_status "Тестирование переключения на ветку new-frontend..."
    
    cd "$PROJECT_DIR"
    
    # Сохраняем текущую ветку
    local original_branch
    original_branch=$(git branch --show-current 2>/dev/null || git rev-parse --abbrev-ref HEAD 2>/dev/null)
    
    print_status "Текущая ветка: $original_branch"
    
    # Пытаемся переключиться на new-frontend
    print_status "Попытка переключения на ветку new-frontend..."
    
    if git checkout new-frontend 2>&1; then
        print_success "Успешно переключились на ветку new-frontend"
        
        # Проверяем текущую ветку
        local new_branch
        new_branch=$(git branch --show-current 2>/dev/null || git rev-parse --abbrev-ref HEAD 2>/dev/null)
        print_status "Текущая ветка после переключения: $new_branch"
        
        # Возвращаемся на исходную ветку
        print_status "Возвращаемся на исходную ветку: $original_branch"
        git checkout "$original_branch" 2>/dev/null || true
        
    else
        print_error "Не удалось переключиться на ветку new-frontend"
        
        # Пытаемся создать ветку из удаленной
        print_status "Попытка создания локальной ветки из удаленной..."
        if git checkout -b new-frontend origin/new-frontend 2>&1; then
            print_success "Успешно создали и переключились на ветку new-frontend"
            
            # Возвращаемся на исходную ветку
            print_status "Возвращаемся на исходную ветку: $original_branch"
            git checkout "$original_branch" 2>/dev/null || true
        else
            print_error "Не удалось создать ветку new-frontend из origin/new-frontend"
        fi
    fi
}

# Исправление проблем с ветками
fix_branch_issues() {
    print_status "Исправление проблем с ветками..."
    
    cd "$PROJECT_DIR"
    
    # Обновляем удаленные ссылки
    print_status "Обновляем удаленные ссылки..."
    git fetch --all --prune --force 2>/dev/null || true
    git remote update 2>/dev/null || true
    
    # Проверяем, находимся ли мы в detached HEAD состоянии
    local current_branch
    current_branch=$(git branch --show-current 2>/dev/null || git rev-parse --abbrev-ref HEAD 2>/dev/null)
    
    if [ "$current_branch" = "HEAD" ] || [[ "$current_branch" =~ ^[0-9a-f]{7,}$ ]]; then
        print_warning "Обнаружено состояние detached HEAD, переключаемся на main..."
        
        if git checkout main 2>/dev/null; then
            print_success "Переключились на ветку main"
        else
            print_error "Не удалось переключиться на ветку main"
            return 1
        fi
    fi
    
    # Удаляем проблемную локальную ветку new-frontend если она существует
    if git show-ref --verify --quiet "refs/heads/new-frontend"; then
        print_status "Удаляем проблемную локальную ветку new-frontend..."
        git branch -D new-frontend 2>/dev/null || true
    fi
    
    # Создаем новую локальную ветку из удаленной
    print_status "Создаем новую локальную ветку new-frontend из origin/new-frontend..."
    if git checkout -b new-frontend origin/new-frontend 2>/dev/null; then
        print_success "Успешно создали и переключились на ветку new-frontend"
        
        # Возвращаемся на main
        git checkout main 2>/dev/null || true
        print_success "Проблемы с ветками исправлены"
    else
        print_error "Не удалось создать ветку new-frontend"
        return 1
    fi
}

# Основная функция
main() {
    print_status "Запуск диагностики проблем с переключением веток Git..."
    echo
    
    find_project_directory
    diagnose_git_status
    
    echo
    print_warning "Обнаружены проблемы с ветками?"
    read -p "Выполнить автоматическое исправление? (y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        fix_branch_issues
        echo
        test_branch_switch
    else
        print_status "Автоматическое исправление пропущено"
        echo
        test_branch_switch
    fi
    
    echo
    print_success "Диагностика завершена!"
}

# Обработка аргументов
case "${1:-}" in
    --help|-h)
        echo "Диагностика проблем с переключением веток Git"
        echo
        echo "Использование: $0 [опции]"
        echo
        echo "Опции:"
        echo "  --help, -h     Показать эту справку"
        echo "  --diagnose     Только диагностика без исправления"
        echo "  --fix          Только исправление без диагностики"
        echo "  --test         Только тестирование переключения веток"
        echo
        echo "Примеры:"
        echo "  $0              Полная диагностика с возможностью исправления"
        echo "  $0 --diagnose   Только диагностика проблем"
        echo "  $0 --fix        Автоматическое исправление"
        echo "  $0 --test       Тестирование переключения веток"
        echo
        exit 0
        ;;
    --diagnose)
        find_project_directory
        diagnose_git_status
        ;;
    --fix)
        find_project_directory
        fix_branch_issues
        ;;
    --test)
        find_project_directory
        test_branch_switch
        ;;
    *)
        main "$@"
        ;;
esac
