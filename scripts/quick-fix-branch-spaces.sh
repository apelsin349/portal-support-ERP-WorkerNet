#!/bin/bash

# Быстрое исправление проблемы с лишними пробелами в названиях веток
# Этот скрипт исправляет конкретную проблему в quick-update.sh

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

# Применяем исправления к quick-update.sh
apply_fixes() {
    local script_path="$PROJECT_DIR/scripts/quick-update.sh"
    
    if [ ! -f "$script_path" ]; then
        print_error "Файл $script_path не найден"
        exit 1
    fi
    
    print_status "Применяем исправления к $script_path..."
    
    # Создаем резервную копию
    cp "$script_path" "$script_path.backup.$(date +%Y%m%d_%H%M%S)"
    print_status "Создана резервная копия: $script_path.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Исправление 1: Убираем пробел после скобки в команде nl
    sed -i "s/nl -w2 -s') '/nl -w2 -s')'/" "$script_path"
    
    # Исправление 2: Улучшаем обработку выбора ветки по номеру
    sed -i 's/SELECTED_BRANCH=$(echo "$available_branches" | sed -n "${choice}p")/SELECTED_BRANCH=$(echo "$available_branches" | sed -n "${choice}p" | sed "s\/^[[:space:]]*\/\/" | sed "s\/[[:space:]]*$\/\/")/' "$script_path"
    
    # Исправление 3: Добавляем проверку на пустые названия веток
    if ! grep -q "Проверяем, что название ветки не пустое" "$script_path"; then
        # Находим место после очистки названия ветки и добавляем проверку
        sed -i '/SELECTED_BRANCH=$(echo "$SELECTED_BRANCH" | sed/a\
    # Проверяем, что название ветки не пустое\
    if [ -z "$SELECTED_BRANCH" ] || [ "$SELECTED_BRANCH" = "" ]; then\
        print_error "Название ветки пустое или содержит только пробелы"\
        return 1\
    fi' "$script_path"
    fi
    
    print_success "Исправления применены к $script_path"
}

# Тестируем исправления
test_fixes() {
    print_status "Тестируем исправления..."
    
    cd "$PROJECT_DIR"
    
    # Тестируем получение списка веток
    local available_branches
    available_branches=$(git branch -r | grep -v HEAD | sed 's/origin\///' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | grep -v '^[[:space:]]*$' | sort -u)
    
    print_status "Доступные ветки (тест):"
    echo "$available_branches" | nl -w2 -s')'
    
    # Тестируем выбор ветки по номеру
    local test_choice="2"
    local selected_branch
    selected_branch=$(echo "$available_branches" | sed -n "${test_choice}p" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
    
    print_status "Тест выбора ветки по номеру $test_choice: '$selected_branch'"
    
    if [ -n "$selected_branch" ] && [ "$selected_branch" != "" ]; then
        print_success "Тест прошел успешно - ветка выбрана корректно"
    else
        print_error "Тест не прошел - ветка не выбрана"
        return 1
    fi
}

# Основная функция
main() {
    print_status "Запуск быстрого исправления проблемы с пробелами в названиях веток..."
    echo
    
    find_project_directory
    apply_fixes
    test_fixes
    
    echo
    print_success "Исправления применены успешно!"
    echo
    print_status "Теперь вы можете запустить:"
    echo "  bash $PROJECT_DIR/scripts/quick-update.sh"
    echo
    print_status "Или использовать конкретную ветку:"
    echo "  bash $PROJECT_DIR/scripts/quick-update.sh --branch new-frontend"
}

# Обработка аргументов
case "${1:-}" in
    --help|-h)
        echo "Быстрое исправление проблемы с лишними пробелами в названиях веток"
        echo
        echo "Использование: $0 [опции]"
        echo
        echo "Опции:"
        echo "  --help, -h     Показать эту справку"
        echo "  --test         Только тестирование без применения исправлений"
        echo
        echo "Этот скрипт исправляет проблему в quick-update.sh, где команда nl"
        echo "добавляет лишние пробелы в названия веток."
        echo
        exit 0
        ;;
    --test)
        find_project_directory
        test_fixes
        ;;
    *)
        main "$@"
        ;;
esac
