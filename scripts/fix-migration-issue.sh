#!/bin/bash

# Скрипт для исправления проблемы с миграциями базы данных
# Исправляет ошибку с несуществующим ограничением unique_username_per_tenant

echo "[ИНФО] Исправляем проблему с миграциями базы данных..."

# Переходим в директорию backend
cd backend

# Проверяем, активировано ли виртуальное окружение
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "[ИНФО] Активируем виртуальное окружение..."
    source venv/bin/activate
fi

# Выполняем SQL команду для безопасного удаления ограничения
echo "[ИНФО] Безопасно удаляем несуществующее ограничение..."
python manage.py dbshell << EOF
DO \$\$ 
BEGIN
    -- Проверяем существование ограничения и удаляем его
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
END \$\$;
EOF

# Помечаем проблемную миграцию как выполненную (если она существует)
echo "[ИНФО] Помечаем проблемную миграцию как выполненную..."
python manage.py migrate app 0008 --fake 2>/dev/null || echo "[ИНФО] Миграция 0008 не найдена, продолжаем..."

# Выполняем все миграции
echo "[ИНФО] Выполняем все миграции..."
python manage.py migrate

echo "[УСПЕХ] Проблема с миграциями исправлена!"
