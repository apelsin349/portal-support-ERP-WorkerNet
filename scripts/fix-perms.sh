#!/usr/bin/env bash

# Fix execution permissions and line endings for project scripts
# Safe to run multiple times; does not fail if tools are missing

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[ИНФО]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[ВНИМАНИЕ]${NC} $1"
}

print_error() {
    echo -e "${RED}[ОШИБКА]${NC} $1"
}

main() {
    PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"

    print_status "Исправляем права на выполнение для скриптов в scripts/ ..."
    if [ -d "$PROJECT_ROOT/scripts" ]; then
        find "$PROJECT_ROOT/scripts" -maxdepth 1 -type f -name "*.sh" -print0 | xargs -0 -r chmod +x || true
        print_status "Права на выполнение установлены"
    else
        print_warning "Директория scripts не найдена"
    fi

    if command -v dos2unix >/dev/null 2>&1; then
        print_status "Преобразуем переводы строк в LF для *.sh ..."
        find "$PROJECT_ROOT/scripts" -maxdepth 1 -type f -name "*.sh" -print0 | xargs -0 -r dos2unix >/dev/null 2>&1 || true
        print_status "Переводы строк приведены к LF"
    else
        print_warning "dos2unix не установлен — пропускаем нормализацию переводов строк (рекомендуется установить: sudo apt install -y dos2unix)"
    fi

    if command -v git >/dev/null 2>&1 && [ -d "$PROJECT_ROOT/.git" ]; then
        print_status "Обновляем атрибуты git для *.sh (exec и LF) ..."
        ATTR_FILE="$PROJECT_ROOT/.gitattributes"
        # Ensure .gitattributes has LF policy for sh and mark as text
        if ! grep -q "^*.sh text eol=lf" "$ATTR_FILE" 2>/dev/null; then
            echo "*.sh text eol=lf" >> "$ATTR_FILE"
        fi
        # Stage exec bit for existing scripts
        git add --chmod=+x "$PROJECT_ROOT"/scripts/*.sh 2>/dev/null || true
        git add "$ATTR_FILE" 2>/dev/null || true
        print_status "Git атрибуты обновлены (не забудьте закоммитить изменения)"
    else
        print_warning "Git недоступен или репозиторий не обнаружен — пропускаем настройку .gitattributes"
    fi

    print_status "Готово ✓"
}

main "$@"


