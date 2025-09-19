#!/bin/bash

# Скрипт для исправления проблемы с правами доступа к webpack

echo "[ИНФО] Исправляем права доступа к webpack..."

# Переходим в директорию frontend
cd frontend

# Проверяем, существует ли node_modules/.bin/webpack
if [ -f "node_modules/.bin/webpack" ]; then
    echo "[ИНФО] Устанавливаем права на выполнение для webpack..."
    chmod +x node_modules/.bin/webpack
    echo "[УСПЕХ] Права доступа к webpack установлены!"
else
    echo "[ВНИМАНИЕ] webpack не найден в node_modules/.bin/"
    echo "[ИНФО] Переустанавливаем зависимости..."
    npm install
    chmod +x node_modules/.bin/webpack 2>/dev/null || true
fi

# Проверяем права на другие важные файлы
echo "[ИНФО] Проверяем права доступа к другим инструментам..."
chmod +x node_modules/.bin/* 2>/dev/null || true

echo "[УСПЕХ] Права доступа исправлены!"
