#!/bin/bash

# Скрипт для компиляции переводов Django
# Создает .mo файлы из .po файлов для русской локализации

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

# Проверка наличия команды
require() {
    if ! command -v "$1" >/dev/null 2>&1; then
        print_error "Не найдена команда: $1"
        exit 1
    fi
}

# Переход в корень проекта
cd "$(dirname "$0")/.." || exit 1

print_status "Компиляция переводов Django..."

# Проверяем наличие Django
require python3

# Активируем виртуальное окружение если есть
if [ -f "backend/venv/bin/activate" ]; then
    print_status "Активируем виртуальное окружение..."
    source backend/venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    print_status "Активируем виртуальное окружение..."
    source venv/bin/activate
fi

# Устанавливаем переменные окружения Django
export DJANGO_SETTINGS_MODULE=backend.config.settings

# Компилируем переводы
print_status "Компилируем переводы для русского языка..."
python3 backend/manage.py compilemessages -l ru

# Проверяем результат
if [ -f "backend/locale/ru/LC_MESSAGES/django.mo" ]; then
    print_success "Переводы успешно скомпилированы!"
    print_status "Файл: backend/locale/ru/LC_MESSAGES/django.mo"
else
    print_error "Ошибка компиляции переводов"
    exit 1
fi

# Создаем переводы для английского языка (базовый)
print_status "Создаем базовые переводы для английского языка..."
mkdir -p backend/locale/en/LC_MESSAGES

# Копируем .po файл для английского языка
if [ -f "backend/locale/ru/LC_MESSAGES/django.po" ]; then
    cp backend/locale/ru/LC_MESSAGES/django.po backend/locale/en/LC_MESSAGES/django.po
    # Заменяем русские строки на английские
    sed -i 's/msgstr ".*"/msgstr ""/g' backend/locale/en/LC_MESSAGES/django.po
    sed -i 's/Language: ru/Language: en/g' backend/locale/en/LC_MESSAGES/django.po
    python3 backend/manage.py compilemessages -l en
    print_success "Базовые переводы для английского языка созданы!"
fi

print_success "Все переводы готовы!"
print_status "Для применения изменений перезапустите Django сервер"
