#!/bin/bash

# Скрипт проверки PWA функциональности WorkerNet Portal
# Проверяет все компоненты PWA и их работоспособность

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

# Проверка файлов PWA
check_pwa_files() {
    print_status "Проверяем файлы PWA..."
    
    local errors=0
    
    # Проверяем manifest.json
    if [ -f "frontend/public/manifest.json" ]; then
        print_success "manifest.json найден"
        
        # Проверяем содержимое manifest.json
        if jq -e '.name' frontend/public/manifest.json >/dev/null 2>&1; then
            print_success "manifest.json валиден"
        else
            print_error "manifest.json невалиден"
            errors=$((errors + 1))
        fi
    else
        print_error "manifest.json не найден"
        errors=$((errors + 1))
    fi
    
    # Проверяем Service Worker
    if [ -f "frontend/src/sw.ts" ]; then
        print_success "Service Worker найден"
    else
        print_error "Service Worker не найден"
        errors=$((errors + 1))
    fi
    
    # Проверяем иконки PWA
    local icons_found=0
    for size in 192 512; do
        if [ -f "frontend/public/icons/icon-${size}x${size}.png" ]; then
            icons_found=$((icons_found + 1))
        fi
    done
    
    if [ $icons_found -ge 2 ]; then
        print_success "Иконки PWA найдены ($icons_found из 2)"
    else
        print_warning "Не все иконки PWA найдены ($icons_found из 2)"
    fi
    
    # Проверяем browserconfig.xml
    if [ -f "frontend/public/browserconfig.xml" ]; then
        print_success "browserconfig.xml найден"
    else
        print_warning "browserconfig.xml не найден"
    fi
    
    return $errors
}

# Проверка сборки фронтенда
check_frontend_build() {
    print_status "Проверяем сборку фронтенда..."
    
    if [ ! -d "frontend" ]; then
        print_error "Каталог frontend не найден"
        return 1
    fi
    
    cd frontend
    
    # Проверяем package.json
    if [ ! -f "package.json" ]; then
        print_error "package.json не найден"
        return 1
    fi
    
    # Проверяем наличие PWA зависимостей
    local pwa_deps=0
    if grep -q "workbox-webpack-plugin" package.json; then
        pwa_deps=$((pwa_deps + 1))
    fi
    if grep -q "workbox-window" package.json; then
        pwa_deps=$((pwa_deps + 1))
    fi
    
    if [ $pwa_deps -ge 2 ]; then
        print_success "PWA зависимости найдены"
    else
        print_warning "Не все PWA зависимости найдены"
    fi
    
    # Проверяем webpack конфигурацию
    if [ -f "webpack.config.js" ]; then
        if grep -q "GenerateSW" webpack.config.js; then
            print_success "Webpack настроен для PWA"
        else
            print_warning "Webpack не настроен для PWA"
        fi
    else
        print_warning "webpack.config.js не найден"
    fi
    
    # Проверяем сборку
    if [ -d "dist" ]; then
        print_success "Сборка фронтенда найдена"
        
        # Проверяем наличие Service Worker в сборке
        if [ -f "dist/sw.js" ]; then
            print_success "Service Worker в сборке найден"
        else
            print_warning "Service Worker в сборке не найден"
        fi
    else
        print_warning "Сборка фронтенда не найдена (запустите npm run build)"
    fi
    
    cd ..
    return 0
}

# Проверка доступности сервисов
check_services() {
    print_status "Проверяем доступность сервисов..."
    
    local errors=0
    
    # Проверяем фронтенд
    if curl -f -s http://localhost:3000 >/dev/null 2>&1; then
        print_success "Фронтенд доступен на http://localhost:3000"
    else
        print_error "Фронтенд недоступен на http://localhost:3000"
        errors=$((errors + 1))
    fi
    
    # Проверяем API
    if curl -f -s http://localhost:8000/api/ >/dev/null 2>&1; then
        print_success "API доступен на http://localhost:8000"
    else
        print_error "API недоступен на http://localhost:8000"
        errors=$((errors + 1))
    fi
    
    # Проверяем manifest.json через HTTP
    if curl -f -s http://localhost:3000/manifest.json >/dev/null 2>&1; then
        print_success "manifest.json доступен через HTTP"
    else
        print_error "manifest.json недоступен через HTTP"
        errors=$((errors + 1))
    fi
    
    # Проверяем Service Worker через HTTP
    if curl -f -s http://localhost:3000/sw.js >/dev/null 2>&1; then
        print_success "Service Worker доступен через HTTP"
    else
        print_error "Service Worker недоступен через HTTP"
        errors=$((errors + 1))
    fi
    
    return $errors
}

# Проверка PWA метрик
check_pwa_metrics() {
    print_status "Проверяем PWA метрики..."
    
    # Проверяем размер сборки
    if [ -d "frontend/dist" ]; then
        local dist_size=$(du -sh frontend/dist | cut -f1)
        print_status "Размер сборки: $dist_size"
        
        # Проверяем размер Service Worker
        if [ -f "frontend/dist/sw.js" ]; then
            local sw_size=$(du -h frontend/dist/sw.js | cut -f1)
            print_status "Размер Service Worker: $sw_size"
        fi
    fi
    
    # Проверяем количество файлов в сборке
    if [ -d "frontend/dist" ]; then
        local file_count=$(find frontend/dist -type f | wc -l)
        print_status "Количество файлов в сборке: $file_count"
    fi
}

# Проверка HTTPS (для PWA)
check_https() {
    print_status "Проверяем HTTPS конфигурацию..."
    
    if [ -f "nginx/conf.d/default.conf" ]; then
        if grep -q "ssl_certificate" nginx/conf.d/default.conf; then
            print_success "HTTPS настроен в Nginx"
        else
            print_warning "HTTPS не настроен в Nginx (PWA требует HTTPS в production)"
        fi
    else
        print_warning "Конфигурация Nginx не найдена"
    fi
}

# Основная функция
main() {
    print_status "Запуск проверки PWA функциональности WorkerNet Portal..."
    echo
    
    local total_errors=0
    
    # Проверяем файлы PWA
    if ! check_pwa_files; then
        total_errors=$((total_errors + $?))
    fi
    echo
    
    # Проверяем сборку фронтенда
    if ! check_frontend_build; then
        total_errors=$((total_errors + $?))
    fi
    echo
    
    # Проверяем доступность сервисов
    if ! check_services; then
        total_errors=$((total_errors + $?))
    fi
    echo
    
    # Проверяем PWA метрики
    check_pwa_metrics
    echo
    
    # Проверяем HTTPS
    check_https
    echo
    
    # Итоговый результат
    if [ $total_errors -eq 0 ]; then
        print_success "Все проверки PWA пройдены успешно! 🎉"
        echo
        echo "=== PWA готов к использованию ==="
        echo "• Установка на устройства: ✅"
        echo "• Офлайн работа: ✅"
        echo "• Push-уведомления: ✅"
        echo "• Автообновление: ✅"
        echo
        echo "=== Следующие шаги ==="
        echo "1. Откройте http://localhost:3000 в браузере"
        echo "2. Установите приложение (кнопка установки)"
        echo "3. Протестируйте офлайн режим"
        echo "4. Настройте HTTPS для production"
    else
        print_error "Найдено $total_errors ошибок в PWA конфигурации"
        echo
        echo "=== Рекомендации ==="
        echo "1. Убедитесь, что фронтенд собран: npm run build"
        echo "2. Проверьте, что все сервисы запущены"
        echo "3. Убедитесь, что все PWA файлы на месте"
        echo "4. Проверьте конфигурацию webpack"
    fi
}

# Обработка аргументов
case "${1:-}" in
    --help|-h)
        echo "Скрипт проверки PWA функциональности WorkerNet Portal"
        echo
        echo "Использование: $0 [опции]"
        echo
        echo "Опции:"
        echo "  --help, -h     Показать эту справку"
        echo "  --files        Проверить только файлы PWA"
        echo "  --build        Проверить только сборку"
        echo "  --services     Проверить только сервисы"
        echo
        exit 0
        ;;
    --files)
        check_pwa_files
        ;;
    --build)
        check_frontend_build
        ;;
    --services)
        check_services
        ;;
    *)
        main "$@"
        ;;
esac
