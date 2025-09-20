#!/bin/bash

# Тестовый скрипт для проверки логики выбора репозитория

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

# Тестируем логику выбора репозитория
test_repo_selection() {
    print_status "=== ТЕСТ ЛОГИКИ ВЫБОРА РЕПОЗИТОРИЯ ==="
    echo
    
    # Тест 1: REPO_URL пустой
    print_status "Тест 1: REPO_URL пустой"
    REPO_URL=""
    if [ -z "$REPO_URL" ]; then
        print_success "REPO_URL пустой - должен спросить пользователя"
    else
        print_error "REPO_URL не пустой: $REPO_URL"
    fi
    echo
    
    # Тест 2: REPO_URL установлен
    print_status "Тест 2: REPO_URL установлен"
    REPO_URL="https://github.com/test/repo.git"
    if [ -z "$REPO_URL" ]; then
        print_error "REPO_URL пустой, но должен быть установлен"
    else
        print_success "REPO_URL установлен: $REPO_URL - пропускаем выбор"
    fi
    echo
    
    # Тест 3: Переменные окружения
    print_status "Тест 3: Переменные окружения"
    print_status "WORKERNET_REPO_URL = '${WORKERNET_REPO_URL:-}'"
    print_status "CI = '${CI:-}'"
    print_status "WORKERNET_NONINTERACTIVE = '${WORKERNET_NONINTERACTIVE:-}'"
    echo
    
    # Тест 4: Неинтерактивный режим
    print_status "Тест 4: Неинтерактивный режим"
    if [[ -n "${CI:-}" || -n "${WORKERNET_NONINTERACTIVE:-}" ]]; then
        print_success "Неинтерактивный режим - используем репозиторий по умолчанию"
    else
        print_success "Интерактивный режим - должен спросить пользователя"
    fi
    echo
}

# Тестируем интерактивный выбор
test_interactive_selection() {
    print_status "=== ТЕСТ ИНТЕРАКТИВНОГО ВЫБОРА ==="
    echo
    
    # Симулируем существующий репозиторий
    EXISTING_REPO="https://github.com/apelsin349/portal-support-ERP-WorkerNet.git"
    
    echo
    print_status "Обновление существующей установки"
    echo "Текущий репозиторий: $EXISTING_REPO"
    echo
    echo "Выберите действие:"
    echo "1) Обновить из текущего репозитория"
    echo "2) Сменить репозиторий"
    echo "3) Использовать текущий (по умолчанию)"
    echo
    
    while true; do
        read -p "Введите номер (1-3): " choice
        
        case "$choice" in
            1)
                print_success "Выбрано: Обновить из текущего репозитория"
                REPO_URL="$EXISTING_REPO"
                break
                ;;
            2)
                print_success "Выбрано: Сменить репозиторий"
                read -p "Введите URL нового репозитория: " new_repo
                if [ -n "$new_repo" ]; then
                    REPO_URL="$new_repo"
                    print_success "Установлен новый репозиторий: $REPO_URL"
                else
                    print_error "URL репозитория не может быть пустым"
                    continue
                fi
                break
                ;;
            3|"")
                print_success "Выбрано: Использовать текущий (по умолчанию)"
                REPO_URL="$EXISTING_REPO"
                break
                ;;
            *)
                print_error "Неверный выбор. Введите номер (1-3)"
                ;;
        esac
    done
    
    echo
    print_success "Финальный выбор репозитория: $REPO_URL"
}

# Запускаем тесты
echo "=== ТЕСТИРОВАНИЕ ЛОГИКИ ВЫБОРА РЕПОЗИТОРИЯ ==="
echo

test_repo_selection

echo
print_status "Хотите протестировать интерактивный выбор? (y/N)"
read -p "> " test_interactive

if [[ "$test_interactive" =~ ^[Yy]$ ]]; then
    test_interactive_selection
fi

echo
print_success "Тестирование завершено!"
