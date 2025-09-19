#!/bin/bash

# Скрипт для исправления проблем с зависимостями миграций
echo "[ИСПРАВЛЕНИЕ] Начинаем исправление зависимостей миграций..."

cd backend

# Активируем виртуальное окружение
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "[ИНФО] Активируем виртуальное окружение..."
    source venv/bin/activate
fi

echo "[ИНФО] Шаг 1: Очищаем проблемные записи миграций из базы данных..."
python manage.py dbshell << 'EOF'
-- Удаляем все записи миграций приложения app, кроме базовой
DELETE FROM django_migrations 
WHERE app = 'app' AND name != '0001_initial';

-- Проверяем результат
SELECT app, name, applied FROM django_migrations WHERE app = 'app' ORDER BY name;
EOF

echo "[ИНФО] Шаг 2: Сбрасываем состояние миграций..."
python manage.py migrate app 0001 --fake

echo "[ИНФО] Шаг 3: Проверяем текущее состояние миграций..."
python manage.py showmigrations app

echo "[ИНФО] Шаг 4: Создаем новые миграции на основе текущих моделей..."
python manage.py makemigrations app

echo "[ИНФО] Шаг 5: Применяем новые миграции..."
python manage.py migrate

echo "[ИНФО] Шаг 6: Проверяем финальное состояние..."
python manage.py showmigrations app

echo "[УСПЕХ] Исправление зависимостей миграций завершено!"
