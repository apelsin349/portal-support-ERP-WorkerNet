#!/bin/bash

# Быстрое исправление проблемы с переключением на ветку new-frontend
# Этот скрипт решает проблему, когда не удается переключиться на ветку

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Без цвета

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

# Быстрое исправление проблемы с переключением веток
quick_fix_branch_switch() {
    print_status "Быстрое исправление проблемы с переключением веток..."
    
    cd "$PROJECT_DIR"
    
    # Сохраняем текущую ветку
    local current_branch
    current_branch=$(git branch --show-current 2>/dev/null || git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
    
    print_status "Текущая ветка: $current_branch"
    
    # Обновляем удаленные ссылки
    print_status "Обновляем удаленные ссылки..."
    git fetch --all --prune --force 2>/dev/null || true
    git remote update 2>/dev/null || true
    
    # Проверяем, находимся ли мы в detached HEAD состоянии
    if [ "$current_branch" = "HEAD" ] || [[ "$current_branch" =~ ^[0-9a-f]{7,}$ ]]; then
        print_warning "Обнаружено состояние detached HEAD, переключаемся на main..."
        git checkout main 2>/dev/null || git checkout -b main origin/main 2>/dev/null || true
        current_branch="main"
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
        
        # Возвращаемся на исходную ветку
        if [ "$current_branch" != "new-frontend" ]; then
            print_status "Возвращаемся на исходную ветку: $current_branch"
            git checkout "$current_branch" 2>/dev/null || true
        fi
        
        print_success "Проблема с переключением веток исправлена"
        return 0
    else
        print_error "Не удалось создать ветку new-frontend"
        
        # Пытаемся альтернативный способ
        print_status "Пробуем альтернативный способ создания ветки..."
        
        # Создаем ветку без переключения
        if git branch new-frontend origin/new-frontend 2>/dev/null; then
            print_success "Успешно создали ветку new-frontend"
            
            # Устанавливаем upstream
            git branch --set-upstream-to=origin/new-frontend new-frontend 2>/dev/null || true
            
            print_success "Проблема с переключением веток исправлена"
            return 0
        else
            print_error "Не удалось создать ветку new-frontend альтернативным способом"
            return 1
        fi
    fi
}

# Тестирование исправления
test_fix() {
    print_status "Тестирование исправления..."
    
    cd "$PROJECT_DIR"
    
    # Пытаемся переключиться на new-frontend
    if git checkout new-frontend 2>/dev/null; then
        print_success "Тест прошел успешно - переключение на new-frontend работает"
        
        # Возвращаемся на main
        git checkout main 2>/dev/null || true
        return 0
    else
        print_error "Тест не прошел - переключение на new-frontend не работает"
        return 1
    fi
}

# Основная функция
main() {
    print_status "Запуск быстрого исправления проблемы с переключением веток..."
    echo
    
    find_project_directory
    quick_fix_branch_switch
    
    if [ $? -eq 0 ]; then
        echo
        test_fix
        
        if [ $? -eq 0 ]; then
            echo
            print_success "Исправление завершено успешно!"
            echo
            print_status "Теперь вы можете запустить:"
            echo "  bash scripts/quick-update.sh"
            echo
            print_status "Или использовать конкретную ветку:"
            echo "  bash scripts/quick-update.sh --branch new-frontend"
        else
            echo
            print_warning "Исправление применено, но тест не прошел"
            print_status "Попробуйте запустить диагностику:"
            echo "  bash scripts/diagnose-git-branch-issue.sh"
        fi
    else
        echo
        print_error "Исправление не удалось"
        print_status "Попробуйте запустить диагностику:"
        echo "  bash scripts/diagnose-git-branch-issue.sh"
        exit 1
    fi
}

# Обработка аргументов
case "${1:-}" in
    --help|-h)
        echo "Быстрое исправление проблемы с переключением веток Git"
        echo
        echo "Использование: $0 [опции]"
        echo
        echo "Опции:"
        echo "  --help, -h     Показать эту справку"
        echo "  --test         Только тестирование без исправления"
        echo
        echo "Этот скрипт исправляет проблему, когда не удается переключиться"
        echo "на ветку new-frontend в скрипте quick-update.sh."
        echo
        exit 0
        ;;
    --test)
        find_project_directory
        test_fix
        ;;
    *)
        main "$@"
        ;;
esac
