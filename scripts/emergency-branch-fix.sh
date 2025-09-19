#!/bin/bash

# Экстренное исправление проблемы с пробелами в названиях веток
# Простое решение для быстрого применения

# Находим скрипт quick-update.sh
SCRIPT_PATH=""
if [ -f "scripts/quick-update.sh" ]; then
    SCRIPT_PATH="scripts/quick-update.sh"
elif [ -f "../scripts/quick-update.sh" ]; then
    SCRIPT_PATH="../scripts/quick-update.sh"
elif [ -f "/home/worker/portal-support-ERP-WorkerNet/scripts/quick-update.sh" ]; then
    SCRIPT_PATH="/home/worker/portal-support-ERP-WorkerNet/scripts/quick-update.sh"
else
    echo "ОШИБКА: Файл quick-update.sh не найден"
    exit 1
fi

echo "ИНФО: Найден скрипт: $SCRIPT_PATH"

# Создаем резервную копию
cp "$SCRIPT_PATH" "$SCRIPT_PATH.backup.$(date +%Y%m%d_%H%M%S)"
echo "ИНФО: Создана резервная копия"

# Применяем исправления
echo "ИНФО: Применяем исправления..."

# Исправление 1: Убираем пробел после скобки в команде nl
sed -i "s/nl -w2 -s') '/nl -w2 -s')'/" "$SCRIPT_PATH"

# Исправление 2: Улучшаем обработку выбора ветки по номеру
sed -i 's/SELECTED_BRANCH=$(echo "$available_branches" | sed -n "${choice}p")/SELECTED_BRANCH=$(echo "$available_branches" | sed -n "${choice}p" | sed "s\/^[[:space:]]*\/\/" | sed "s\/[[:space:]]*$\/\/")/' "$SCRIPT_PATH"

echo "УСПЕХ: Исправления применены!"
echo "ИНФО: Теперь запустите: bash $SCRIPT_PATH"
