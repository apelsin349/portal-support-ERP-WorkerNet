#!/bin/bash

# Быстрое исправление проблем с миграциями
echo "🔧 Быстрое исправление миграций..."

cd backend

# Активируем виртуальное окружение
if [[ "$VIRTUAL_ENV" == "" ]]; then
    source venv/bin/activate
fi

echo "Очищаем проблемные записи миграций..."
python manage.py dbshell -c "DELETE FROM django_migrations WHERE app = 'app' AND name != '0001_initial';"

echo "Сбрасываем состояние миграций..."
python manage.py migrate app 0001 --fake

echo "Создаем новые миграции..."
python manage.py makemigrations app

echo "Применяем миграции..."
python manage.py migrate

echo "✅ Миграции исправлены!"
echo "Проверяем состояние:"
python manage.py showmigrations app
