#!/bin/bash

# Тестовый скрипт для проверки порядка выполнения проверок в install-ubuntu.sh

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

# Тест 1: Проверка порядка выполнения
test_execution_order() {
    print_status "Тест 1: Проверка порядка выполнения в install-ubuntu.sh"
    
    # Извлекаем порядок вызовов функций из main()
    if grep -A 20 "main() {" scripts/install-ubuntu.sh | grep -q "check_existing_installation"; then
        print_success "✓ check_existing_installation вызывается в main()"
    else
        print_error "✗ check_existing_installation НЕ найден в main()"
        return 1
    fi
    
    # Проверяем, что check_existing_installation вызывается перед другими операциями
    local main_start=$(grep -n "main() {" scripts/install-ubuntu.sh | cut -d: -f1)
    local check_line=$(grep -n "check_existing_installation" scripts/install-ubuntu.sh | head -1 | cut -d: -f1)
    
    if [ "$check_line" -gt "$main_start" ]; then
        print_success "✓ check_existing_installation вызывается после начала main()"
    else
        print_error "✗ check_existing_installation вызывается до main()"
        return 1
    fi
    
    # Проверяем, что early_update_repository НЕ вызывается до check_existing_installation
    local early_line=$(grep -n "early_update_repository" scripts/install-ubuntu.sh | head -1 | cut -d: -f1)
    if [ "$early_line" -gt "$check_line" ]; then
        print_success "✓ early_update_repository вызывается ПОСЛЕ check_existing_installation"
    else
        print_error "✗ early_update_repository вызывается ДО check_existing_installation"
        return 1
    fi
}

# Тест 2: Проверка инициализации переменных
test_variable_initialization() {
    print_status "Тест 2: Проверка инициализации переменных"
    
    # Проверяем, что INSTALLATION_MODE инициализирована
    if grep -q 'INSTALLATION_MODE=""' scripts/install-ubuntu.sh; then
        print_success "✓ INSTALLATION_MODE инициализирована в начале скрипта"
    else
        print_error "✗ INSTALLATION_MODE НЕ инициализирована"
        return 1
    fi
    
    # Проверяем, что есть проверка на пустую переменную
    if grep -q 'if \[ -z "\$INSTALLATION_MODE" \]' scripts/install-ubuntu.sh; then
        print_success "✓ Есть проверка на пустую INSTALLATION_MODE"
    else
        print_error "✗ НЕТ проверки на пустую INSTALLATION_MODE"
        return 1
    fi
}

# Тест 3: Проверка логики выбора режима
test_mode_selection_logic() {
    print_status "Тест 3: Проверка логики выбора режима"
    
    # Проверяем, что есть проверка на существующую установку
    if grep -q "EXISTING_INSTALLATION=false" scripts/install-ubuntu.sh; then
        print_success "✓ Есть переменная EXISTING_INSTALLATION"
    else
        print_error "✗ НЕТ переменной EXISTING_INSTALLATION"
        return 1
    fi
    
    # Проверяем, что есть проверка на запущенные сервисы
    if grep -q "SERVICES_RUNNING=false" scripts/install-ubuntu.sh; then
        print_success "✓ Есть переменная SERVICES_RUNNING"
    else
        print_error "✗ НЕТ переменной SERVICES_RUNNING"
        return 1
    fi
    
    # Проверяем, что есть неинтерактивный режим
    if grep -q "WORKERNET_NONINTERACTIVE" scripts/install-ubuntu.sh; then
        print_success "✓ Есть поддержка неинтерактивного режима"
    else
        print_error "✗ НЕТ поддержки неинтерактивного режима"
        return 1
    fi
}

# Тест 4: Проверка комментариев и документации
test_documentation() {
    print_status "Тест 4: Проверка документации и комментариев"
    
    # Проверяем, что есть комментарии о порядке выполнения
    if grep -q "ПЕРВЫМ ДЕЛОМ" scripts/install-ubuntu.sh; then
        print_success "✓ Есть комментарии о порядке выполнения"
    else
        print_error "✗ НЕТ комментариев о порядке выполнения"
        return 1
    fi
    
    # Проверяем, что есть комментарии о режимах установки
    if grep -q "режим установки" scripts/install-ubuntu.sh; then
        print_success "✓ Есть комментарии о режимах установки"
    else
        print_error "✗ НЕТ комментариев о режимах установки"
        return 1
    fi
}

# Основная функция тестирования
main() {
    print_status "Запуск тестов проверки порядка выполнения в install-ubuntu.sh"
    echo
    
    local tests_passed=0
    local tests_total=4
    
    # Запускаем тесты
    if test_execution_order; then
        ((tests_passed++))
    fi
    echo
    
    if test_variable_initialization; then
        ((tests_passed++))
    fi
    echo
    
    if test_mode_selection_logic; then
        ((tests_passed++))
    fi
    echo
    
    if test_documentation; then
        ((tests_passed++))
    fi
    echo
    
    # Результаты
    print_status "Результаты тестирования: $tests_passed/$tests_total тестов пройдено"
    
    if [ $tests_passed -eq $tests_total ]; then
        print_success "Все тесты пройдены! Проверка выполняется в правильном порядке."
        exit 0
    else
        print_error "Некоторые тесты не пройдены. Проверьте скрипт install-ubuntu.sh"
        exit 1
    fi
}

# Запуск тестов
main "$@"
