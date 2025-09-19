#!/bin/bash

# Check Dependencies Script for WorkerNet Portal
# Проверяет актуальность и безопасность зависимостей

set -e

echo "🔍 Проверка зависимостей WorkerNet Portal..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${2}${1}${NC}"
}

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    print_status "❌ Файл requirements.txt не найден. Запустите скрипт из корня проекта." "$RED"
    exit 1
fi

# Backend dependencies check
print_status "📦 Проверка Python зависимостей..." "$BLUE"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    print_status "⚠️  Виртуальная среда не активирована. Активируем..." "$YELLOW"
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    else
        print_status "❌ Виртуальная среда не найдена. Создайте её командой: python -m venv venv" "$RED"
        exit 1
    fi
fi

# Install pip-audit for security checking
echo "📋 Установка инструментов для проверки..."
pip install --quiet pip-audit safety

# Check for outdated packages
print_status "🔄 Проверка устаревших пакетов..." "$BLUE"
pip list --outdated --format=freeze | head -20

# Security audit with pip-audit
print_status "🔒 Проверка безопасности с pip-audit..." "$BLUE"
pip-audit --desc --fix-dry-run || print_status "⚠️  Найдены уязвимости в зависимостях" "$YELLOW"

# Security audit with safety
print_status "🛡️  Проверка безопасности с safety..." "$BLUE"
safety check --json --output safety-report.json || print_status "⚠️  Найдены уязвимости в зависимостях" "$YELLOW"

# Check frontend dependencies
if [ -f "frontend/package.json" ]; then
    print_status "📦 Проверка Node.js зависимостей..." "$BLUE"
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "📥 Установка npm зависимостей..." "$BLUE"
        npm install
    fi
    
    # Audit npm packages
    print_status "🔒 Аудит npm пакетов..." "$BLUE"
    npm audit --audit-level=moderate || print_status "⚠️  Найдены уязвимости в npm пакетах" "$YELLOW"
    
    # Check for outdated npm packages
    print_status "🔄 Проверка устаревших npm пакетов..." "$BLUE"
    npm outdated || true
    
    cd ..
fi

# Check Docker configuration
if [ -f "docker-compose.yml" ]; then
    print_status "🐳 Проверка Docker конфигурации..." "$BLUE"
    
    # Check if docker-compose is available
    if command -v docker-compose &> /dev/null; then
        docker-compose config --quiet && print_status "✅ Docker Compose конфигурация корректна" "$GREEN" || print_status "❌ Ошибки в Docker Compose конфигурации" "$RED"
    else
        print_status "⚠️  docker-compose не найден" "$YELLOW"
    fi
fi

# Check for common security issues in settings
print_status "🔐 Проверка настроек безопасности..." "$BLUE"

if [ -f "backend/config/settings.py" ]; then
    # Check for DEBUG=True in production
    if grep -q "DEBUG.*=.*True" backend/config/settings.py; then
        print_status "⚠️  DEBUG=True найден в settings.py - убедитесь что это отключено в продакшене" "$YELLOW"
    fi
    
    # Check for SECRET_KEY exposure
    if grep -q "SECRET_KEY.*=.*['\"].*['\"]" backend/config/settings.py; then
        print_status "⚠️  SECRET_KEY может быть захардкожен в settings.py" "$YELLOW"
    fi
    
    # Check for ALLOWED_HOSTS
    if grep -q "ALLOWED_HOSTS.*=.*\[\]" backend/config/settings.py; then
        print_status "⚠️  ALLOWED_HOSTS пуст - это небезопасно для продакшена" "$YELLOW"
    fi
fi

# Generate dependency report
print_status "📊 Генерация отчёта о зависимостях..." "$BLUE"

cat > dependency-report.md << EOF
# Отчёт о зависимостях WorkerNet Portal

## Дата проверки
$(date)

## Python зависимости
\`\`\`
$(pip list --format=freeze | head -50)
\`\`\`

## Устаревшие Python пакеты
\`\`\`
$(pip list --outdated --format=freeze 2>/dev/null | head -20 || echo "Нет устаревших пакетов")
\`\`\`

EOF

if [ -f "frontend/package.json" ]; then
    cat >> dependency-report.md << EOF
## Node.js зависимости
\`\`\`
$(cd frontend && npm list --depth=0 2>/dev/null | head -30 || echo "Ошибка получения списка")
\`\`\`

EOF
fi

print_status "✅ Проверка завершена!" "$GREEN"
print_status "📄 Отчёт сохранён в dependency-report.md" "$BLUE"

if [ -f "safety-report.json" ]; then
    print_status "🛡️  Отчёт безопасности сохранён в safety-report.json" "$BLUE"
fi

print_status "🔧 Рекомендации:" "$BLUE"
echo "1. Регулярно обновляйте зависимости"
echo "2. Следите за уведомлениями о безопасности"
echo "3. Используйте dependabot или аналогичные инструменты"
echo "4. Тестируйте обновления в dev/staging среде"
echo "5. Проверьте переменные окружения в продакшене"
