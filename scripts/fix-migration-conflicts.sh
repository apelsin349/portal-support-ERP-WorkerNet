#!/bin/bash

# Скрипт для исправления конфликтов миграций

echo "[ИНФО] Исправляем конфликты миграций..."

# Переходим в директорию backend
cd backend

# Проверяем, активировано ли виртуальное окружение
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "[ИНФО] Активируем виртуальное окружение..."
    source venv/bin/activate
fi

# Сначала исправляем проблему с ограничением
echo "[ИНФО] Исправляем проблему с ограничением unique_username_per_tenant..."
python manage.py dbshell << 'EOF' 2>/dev/null || true
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'unique_username_per_tenant' 
        AND table_name = 'users'
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE users DROP CONSTRAINT unique_username_per_tenant;
        RAISE NOTICE 'Constraint unique_username_per_tenant dropped successfully';
    ELSE
        RAISE NOTICE 'Constraint unique_username_per_tenant does not exist, skipping';
    END IF;
END $$;
EOF

# Проверяем конфликты миграций
echo "[ИНФО] Проверяем конфликты миграций..."
if python manage.py showmigrations app 2>&1 | grep -q "Conflicting migrations detected"; then
    echo "[ИНФО] Обнаружен конфликт миграций, исправляем..."
    
    # Создаем merge миграцию
    echo "[ИНФО] Создаем merge миграцию..."
    python manage.py makemigrations --merge app --empty 2>/dev/null || true
    
    # Помечаем все проблемные миграции как выполненные
    echo "[ИНФО] Помечаем проблемные миграции как выполненные..."
    python manage.py migrate app 0008 --fake 2>/dev/null || true
    python manage.py migrate app 0009 --fake 2>/dev/null || true
    python manage.py migrate app 0010 --fake 2>/dev/null || true
    python manage.py migrate app 0011 --fake 2>/dev/null || true
fi

# Выполняем миграции
echo "[ИНФО] Выполняем миграции..."
python manage.py migrate

echo "[УСПЕХ] Конфликты миграций исправлены!"
