# 🚨 Быстрое исправление базы данных

## Проблема: Пользователь workernet не может подключиться к PostgreSQL

### Симптомы
```
FATAL: password authentication failed for user "workernet"
```

## 🚀 Быстрое решение

### Вариант 1: Автоматический скрипт
```bash
# Сделать скрипт исполняемым
chmod +x scripts/quick-db-fix.sh

# Запустить быстрое исправление
./scripts/quick-db-fix.sh
```

### Вариант 2: Ручные команды
```bash
# 1. Создать пользователя PostgreSQL
sudo -u postgres psql -c "DROP USER IF EXISTS workernet;"
sudo -u postgres psql -c "CREATE USER workernet WITH PASSWORD 'workernet123' CREATEDB SUPERUSER;"

# 2. Создать базу данных
sudo -u postgres psql -c "DROP DATABASE IF EXISTS workernet;"
sudo -u postgres psql -c "CREATE DATABASE workernet OWNER workernet;"

# 3. Создать файл .env
cat > .env << 'EOF'
SECRET_KEY=workernet-secret-key-2024-development-only
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DATABASE_URL=postgresql://workernet:workernet123@localhost:5432/workernet
REDIS_URL=redis://:redis123@localhost:6379/0
JWT_SECRET_KEY=workernet-jwt-secret-key-2024-development-only
EOF

# 4. Копировать в backend
cp .env backend/.env
```

### Вариант 3: Экстренное исправление
```bash
# Сделать скрипт исполняемым
chmod +x scripts/emergency-db-fix.sh

# Запустить экстренное исправление
./scripts/emergency-db-fix.sh
```

## 🔍 Проверка

### Проверить подключение к PostgreSQL
```bash
PGPASSWORD=workernet123 psql -h localhost -U workernet -d workernet -c '\q'
```

### Проверить Django
```bash
cd backend
source venv/bin/activate
python manage.py check --database default
```

## 🚀 После исправления

### Запустить миграции
```bash
cd backend
source venv/bin/activate
python manage.py migrate
```

### Создать суперпользователя
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@workernet.com
# Password: admin123
```

## ⚠️ Если проблемы продолжаются

### Проверить статус PostgreSQL
```bash
sudo systemctl status postgresql
sudo systemctl restart postgresql
```

### Проверить конфигурацию PostgreSQL
```bash
sudo -u postgres psql -c '\du'  # Список пользователей
sudo -u postgres psql -c '\l'   # Список баз данных
```

### Проверить файл .env
```bash
cat .env
cat backend/.env
```

## 🎯 Заключение

Быстрое исправление включает:
1. ✅ Удаление и пересоздание пользователя workernet
2. ✅ Удаление и пересоздание базы данных workernet
3. ✅ Создание файла .env с правильными настройками
4. ✅ Копирование .env в backend/

После этого миграции Django должны выполняться успешно!
