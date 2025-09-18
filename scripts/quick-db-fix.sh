#!/bin/bash

# Быстрое исправление базы данных
# Выполняет только необходимые команды

set -e

echo "🔧 Быстрое исправление базы данных..."

# Создаем пользователя и базу данных
echo "Создаем пользователя workernet..."
sudo -u postgres psql -c "DROP USER IF EXISTS workernet;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER workernet WITH PASSWORD 'workernet123' CREATEDB SUPERUSER;"

echo "Создаем базу данных workernet..."
sudo -u postgres psql -c "DROP DATABASE IF EXISTS workernet;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE workernet OWNER workernet;"

# Создаем .env файл
echo "Создаем файл .env..."
cat > .env << 'EOF'
SECRET_KEY=workernet-secret-key-2024-development-only
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DATABASE_URL=postgresql://workernet:workernet123@localhost:5432/workernet
REDIS_URL=redis://:redis123@localhost:6379/0
JWT_SECRET_KEY=workernet-jwt-secret-key-2024-development-only
EOF

# Копируем в backend
if [ -d "backend" ]; then
    cp .env backend/.env
fi

echo "✅ База данных исправлена!"
echo "Теперь можно запустить: cd backend && source venv/bin/activate && python manage.py migrate"
