# 🗄️ Исправление проблем с базой данных

## Проблема: Ошибка подключения к PostgreSQL

### Симптомы
```
psycopg2.OperationalError: connection to server at "localhost" (127.0.0.1), port 5432 failed: 
FATAL: password authentication failed for user "workernet"
```

### Причины
1. **Отсутствует файл .env** - Django не знает параметры подключения к БД
2. **Пользователь workernet не существует** - в PostgreSQL нет пользователя
3. **База данных не создана** - отсутствует база данных workernet
4. **Неправильные пароли** - несоответствие паролей в конфигурации

## 🚀 Решения

### 1. Быстрое решение (рекомендуется)

Запустите скрипт настройки базы данных:

```bash
# Сделать скрипт исполняемым
chmod +x scripts/setup-database.sh

# Запустить настройку базы данных
./scripts/setup-database.sh
```

### 2. Настройка Redis

```bash
# Сделать скрипт исполняемым
chmod +x scripts/setup-redis.sh

# Запустить настройку Redis
./scripts/setup-redis.sh
```

### 3. Ручное исправление

#### Шаг 1: Создание пользователя PostgreSQL
```bash
# Подключиться к PostgreSQL как суперпользователь
sudo -u postgres psql

# Создать пользователя
CREATE USER workernet WITH PASSWORD 'workernet123';

# Создать базу данных
CREATE DATABASE workernet OWNER workernet;

# Предоставить права
GRANT ALL PRIVILEGES ON DATABASE workernet TO workernet;
ALTER USER workernet CREATEDB;

# Выйти
\q
```

#### Шаг 2: Создание файла .env
```bash
# Создать файл .env в корне проекта
cat > .env << 'EOF'
SECRET_KEY=workernet-secret-key-2024-development-only
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DATABASE_URL=postgresql://workernet:workernet123@localhost:5432/workernet
REDIS_URL=redis://:redis123@localhost:6379/0
JWT_SECRET_KEY=workernet-jwt-secret-key-2024-development-only
EOF

# Копировать в backend/
cp .env backend/.env
```

#### Шаг 3: Настройка Redis
```bash
# Добавить пароль в конфигурацию Redis
echo "requirepass redis123" | sudo tee -a /etc/redis/redis.conf

# Перезапустить Redis
sudo systemctl restart redis-server
```

#### Шаг 4: Проверка подключения
```bash
# Проверить PostgreSQL
PGPASSWORD=workernet123 psql -h localhost -U workernet -d workernet -c '\q'

# Проверить Redis
redis-cli -a redis123 ping
```

## 🔍 Диагностика

### Проверка статуса сервисов
```bash
# PostgreSQL
sudo systemctl status postgresql
sudo systemctl is-active postgresql

# Redis
sudo systemctl status redis-server
sudo systemctl is-active redis-server
```

### Проверка подключения
```bash
# PostgreSQL
sudo -u postgres psql -c '\l'  # Список баз данных
sudo -u postgres psql -c '\du' # Список пользователей

# Redis
redis-cli ping
redis-cli -a redis123 ping
```

### Проверка Django
```bash
cd backend
source venv/bin/activate
python manage.py check --database default
python manage.py dbshell
```

## 📋 Созданные скрипты

### 1. `scripts/setup-database.sh`
- Создает пользователя workernet в PostgreSQL
- Создает базу данных workernet
- Предоставляет необходимые права
- Создает файл .env с правильными настройками
- Проверяет подключение к базе данных

### 2. `scripts/setup-redis.sh`
- Настраивает пароль для Redis
- Перезапускает Redis для применения изменений
- Тестирует подключение с паролем
- Проверяет работу всех баз данных Redis

### 3. Обновленный `scripts/install-ubuntu.sh`
- Автоматически настраивает базу данных
- Создает .env файл с правильными параметрами
- Настраивает Redis с паролем
- Выполняет миграции после настройки

## ⚠️ Частые проблемы

### 1. PostgreSQL не запущен
```
psycopg2.OperationalError: connection to server at "localhost" (127.0.0.1), port 5432 failed: 
Connection refused
```

**Решение:**
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Пользователь уже существует
```
ERROR: role "workernet" already exists
```

**Решение:**
```bash
sudo -u postgres psql -c "ALTER USER workernet WITH PASSWORD 'workernet123';"
```

### 3. База данных уже существует
```
ERROR: database "workernet" already exists
```

**Решение:**
```bash
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE workernet TO workernet;"
```

### 4. Проблемы с правами доступа
```
FATAL: password authentication failed for user "workernet"
```

**Решение:**
```bash
# Проверить пароль
sudo -u postgres psql -c "ALTER USER workernet WITH PASSWORD 'workernet123';"

# Проверить подключение
PGPASSWORD=workernet123 psql -h localhost -U workernet -d workernet -c '\q'
```

## 🚀 После исправления

### Запуск миграций
```bash
cd backend
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

### Создание суперпользователя
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@workernet.com
# Password: admin123
```

### Проверка Django
```bash
python manage.py runserver
# Открыть http://localhost:8000
```

## 📚 Полезные команды

### PostgreSQL
```bash
# Подключение к базе данных
sudo -u postgres psql -d workernet

# Список таблиц
\dt

# Список пользователей
\du

# Выход
\q
```

### Redis
```bash
# Подключение к Redis
redis-cli -a redis123

# Проверка всех ключей
KEYS *

# Выход
exit
```

### Django
```bash
# Проверка Django
python manage.py check

# Создание миграций
python manage.py makemigrations

# Выполнение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser
```

## 🎯 Заключение

Проблемы с базой данных обычно связаны с:
1. Отсутствием пользователя или базы данных
2. Неправильными параметрами подключения
3. Отсутствием файла .env
4. Неправильными паролями

Используйте предоставленные скрипты для автоматического решения проблем или следуйте ручным инструкциям для диагностики и исправления.
