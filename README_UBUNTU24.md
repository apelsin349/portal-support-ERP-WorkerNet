# WorkerNet Portal - Полная инструкция для Ubuntu 24

## 🚀 Быстрый старт на Ubuntu 24.04 LTS
### 0) Важно: запустите не под root
```bash
adduser workernet
usermod -aG sudo workernet
su - workernet
```

### 1) Авто-установка (рекомендуется)
```bash
# Если вы сейчас под root, создайте пользователя с sudo и войдите под ним:
# adduser workernet
# usermod -aG sudo workernet
# su - workernet

# Запустите установку. Скрипт откажется работать под root, это нормально.
# Также заменим URL репозитория внутри скрипта на актуальный:
curl -fsSL https://raw.githubusercontent.com/apelsin349/portal-support-ERP-WorkerNet/main/scripts/install-ubuntu.sh \
| sed 's|https://github.com/your-org/portal-support-ERP-WorkerNet.git|https://github.com/apelsin349/portal-support-ERP-WorkerNet.git|' \
| bash
```

### Если `docker compose` недоступен
```bash
sudo apt update
sudo apt install -y docker-compose-plugin || sudo apt install -y docker-compose
```

### 2) Системные требования
- Ubuntu 24.04 LTS (или новее)
- 4+ GB RAM
- 20+ GB свободного места
- Интернет соединение

## 📦 Установка зависимостей

### 1. Обновление системы
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Установка основных пакетов
```bash
sudo apt install -y curl wget git build-essential software-properties-common apt-transport-https ca-certificates gnupg lsb-release
```

### 3. Установка Python
```bash
# На Ubuntu 24.04 обычно доступен Python 3.12. Используйте доступный пакет.
sudo apt install -y python3 python3-venv python3-dev python3-pip
```

### 4. Установка Node.js 18+
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
# Если NodeSource недоступен или возникают конфликты — удалите источник и используйте NVM:
# sudo rm -f /etc/apt/sources.list.d/nodesource.list
# sudo apt update
# curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
# . ~/.nvm/nvm.sh && nvm install 18 && nvm use 18 && nvm alias default 18
# cd ~ && npm -v || echo "npm временно недоступен — повторите nvm install/use из домашней директории"
```

### 5. Установка PostgreSQL 15+
```bash
sudo apt install -y postgresql postgresql-contrib postgresql-client
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 6. Установка Redis
```bash
sudo apt install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 7. Установка Docker и Docker Compose
```bash
# Установка Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker
```

### 8. Установка дополнительных инструментов
```bash
# Git LFS
sudo apt install -y git-lfs
git lfs install

# Make
sudo apt install -y make

# Unzip
sudo apt install -y unzip
```

## 🔧 Настройка проекта

### 1. Клонирование репозитория
```bash
git clone https://github.com/apelsin349/portal-support-ERP-WorkerNet.git
cd portal-support-ERP-WorkerNet
```

### 2. Создание виртуального окружения Python
```bash
# Создаём окружение в каталоге backend
cd backend
python3 -m venv venv
source venv/bin/activate
python -m pip install -U pip setuptools wheel
```

### 3. Установка Python зависимостей
```bash
# Запускаем установку из корня репозитория, чтобы путь к файлам был корректный
python -m pip install -r ../requirements.txt
if [ -f ../requirements-dev.txt ]; then
  python -m pip install -r ../requirements-dev.txt
fi
```

### 4. Настройка базы данных PostgreSQL
```bash
# Переключение на пользователя postgres
sudo -u postgres psql

# В PostgreSQL консоли:
CREATE DATABASE worker_net;
CREATE DATABASE worker_net_test;
CREATE USER workernet WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE worker_net TO workernet;
GRANT ALL PRIVILEGES ON DATABASE worker_net_test TO workernet;
\q
```

### 5. Настройка Redis
```bash
# Редактирование конфигурации Redis
sudo nano /etc/redis/redis.conf

# Изменить:
# requirepass your_redis_password
# maxmemory 512mb
# maxmemory-policy allkeys-lru

# Перезапуск Redis
sudo systemctl restart redis-server
```

### 6. Создание файлов конфигурации
```bash
# Копирование примеров конфигурации
cp .env.example .env
cp .env.development.example .env.development
cp .env.production.example .env.production
cp docker-compose.override.yml.example docker-compose.override.yml

# Редактирование .env файла
nano .env
```

### 7. Настройка переменных окружения
```bash
# В файле .env установите:
DATABASE_URL=postgresql://workernet:your_secure_password@localhost:5432/worker_net
REDIS_URL=redis://:your_redis_password@localhost:6379/0
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

## 🚀 Запуск проекта

### Вариант 1: Запуск через Docker Compose (Рекомендуется)
```bash
# Сборка и запуск всех сервисов
docker-compose up -d --build

# Проверка статуса сервисов
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

### Вариант 2: Локальный запуск (для разработки)
```bash
# Запуск Redis
redis-server

# Запуск PostgreSQL (если не запущен)
sudo systemctl start postgresql

# Запуск backend
cd backend
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000

# В новом терминале - запуск frontend
cd frontend
npm install
npm start
```

## 📊 Мониторинг и управление

### 1. Проверка статуса сервисов
```bash
# Docker сервисы
docker-compose ps

# Системные сервисы
sudo systemctl status postgresql
sudo systemctl status redis-server
```

### 2. Просмотр логов
```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
docker-compose logs -f redis
```

### 3. Доступные интерфейсы
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Admin Panel**: http://localhost:8000/admin
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Celery Flower**: http://localhost:5555

## 🔧 Разработка

### 1. Backend разработка
```bash
cd backend
source venv/bin/activate

# Запуск тестов
pytest

# Запуск с hot reload
python manage.py runserver 0.0.0.0:8000

# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser
```

### 2. Frontend разработка
```bash
cd frontend

# Установка зависимостей
npm install

# Запуск в режиме разработки
npm start

# Сборка для продакшена
npm run build

# Запуск тестов
npm test
```

### 3. База данных
```bash
# Подключение к PostgreSQL
psql -U workernet -d worker_net -h localhost

# Создание резервной копии
pg_dump -U workernet -d worker_net > backup.sql

# Восстановление из резервной копии
psql -U workernet -d worker_net < backup.sql
```

## 🛠️ Устранение неполадок

### 1. NodeSource не качается / таймауты
```bash
# Очистить проблемный источник и обновить APT
sudo rm -f /etc/apt/sources.list.d/nodesource.list
sudo apt update

# Использовать NVM как резервный способ
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
. ~/.nvm/nvm.sh
nvm install 18 && nvm use 18 && nvm alias default 18

# Важно: выполнять npm из домашней директории, чтобы избежать ENOENT uv_cwd
cd ~ && npm -v
```

### 2. NPM падает с ошибкой ENOENT/uv_cwd
```bash
cd ~
. ~/.nvm/nvm.sh
nvm use 18
npm -v  # должна вывести версию
```

### 3. npm ETIMEDOUT / проблемы с прокси
```bash
# Настроить прокси, если используется
npm config set proxy "$HTTP_PROXY"   # либо http_proxy
npm config set https-proxy "$HTTPS_PROXY"  # либо https_proxy

# Увеличить таймауты и повторы
npm config set fetch-retries 3
npm config set fetch-retry-factor 2
npm config set fetch-retry-maxtimeout 120000
npm config set fetch-timeout 120000

# Поменять реестр и повторить установку
npm config set registry https://registry.npmjs.org
cd frontend && ( [ -f package-lock.json ] && npm ci || npm install )
```

### 4. Предупреждение APT: "Missing Signed-By ... for http://ru.archive.ubuntu.com/ubuntu"
- Это предупреждение допустимо для стандартных зеркал Ubuntu. Можно игнорировать.
- Чтобы вернуться на зеркала Ubuntu по умолчанию:
```bash
sudo cp -f /etc/apt/sources.list.bak /etc/apt/sources.list 2>/dev/null || true
sudo sed -i 's|http://ru.archive.ubuntu.com/ubuntu/|http://archive.ubuntu.com/ubuntu/|g' /etc/apt/sources.list
sudo sed -i 's|http://ru.archive.ubuntu.com/ubuntu|http://security.ubuntu.com/ubuntu|g' /etc/apt/sources.list
sudo apt update
```

### 5. Проблемы с Docker
```bash
# Очистка Docker
docker system prune -a
docker volume prune

# Перезапуск всех сервисов
docker-compose down
docker-compose up -d --build
```

### 6. Проблемы с базой данных
```bash
# Проверка подключения
psql -U workernet -d worker_net -h localhost

# Сброс базы данных
dropdb -U workernet worker_net
createdb -U workernet worker_net
python manage.py migrate
```

### 7. Проблемы с Redis
```bash
# Проверка статуса
redis-cli ping

# Очистка Redis
redis-cli flushall
```

### 8. Проблемы с портами
```bash
# Проверка занятых портов
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :3000

# Освобождение портов
sudo kill -9 <PID>
```

## 📱 Мобильное приложение

### 1. Установка React Native CLI
```bash
npm install -g @react-native-community/cli
```

### 2. Запуск мобильного приложения
```bash
cd mobile
npm install
npx react-native run-android  # Для Android
npx react-native run-ios      # Для iOS
```

## 🔐 Безопасность

### 1. Настройка файрвола
```bash
sudo ufw enable
sudo ufw allow 22      # SSH
sudo ufw allow 80      # HTTP
sudo ufw allow 443     # HTTPS
sudo ufw allow 3000    # Frontend
sudo ufw allow 8000    # API
```

### 2. Настройка SSL (опционально)
```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение SSL сертификата
sudo certbot --nginx -d yourdomain.com
```

## 📈 Производительность

### 1. Оптимизация PostgreSQL
```bash
# Редактирование конфигурации
sudo nano /etc/postgresql/15/main/postgresql.conf

# Рекомендуемые настройки:
# shared_buffers = 256MB
# effective_cache_size = 1GB
# maintenance_work_mem = 64MB
# checkpoint_completion_target = 0.9
# wal_buffers = 16MB
# default_statistics_target = 100

# Перезапуск PostgreSQL
sudo systemctl restart postgresql
```

### 2. Оптимизация Redis
```bash
# Редактирование конфигурации
sudo nano /etc/redis/redis.conf

# Рекомендуемые настройки:
# maxmemory 512mb
# maxmemory-policy allkeys-lru
# save 900 1
# save 300 10
# save 60 10000

# Перезапуск Redis
sudo systemctl restart redis-server
```

## 🤝 Поддержка

### 1. Логи и диагностика
```bash
# Системные логи
sudo journalctl -u postgresql
sudo journalctl -u redis-server

# Логи приложения
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 2. Мониторинг ресурсов
```bash
# Использование CPU и памяти
htop

# Использование диска
df -h

# Использование сети
iftop
```

### 3. Резервное копирование
```bash
# Создание скрипта резервного копирования
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Создание директории
mkdir -p $BACKUP_DIR

# Резервная копия базы данных
pg_dump -U workernet -d worker_net > $BACKUP_DIR/worker_net_$DATE.sql

# Резервная копия файлов
tar -czf $BACKUP_DIR/worker_net_files_$DATE.tar.gz /path/to/worker_net

# Удаление старых резервных копий (старше 7 дней)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x backup.sh
```

## 📚 Дополнительные ресурсы

### Полезные команды
```bash
# Перезагрузка системы
sudo reboot

# Очистка кэша пакетов
sudo apt clean
sudo apt autoremove

# Обновление системы
sudo apt update && sudo apt upgrade -y

# Проверка места на диске
du -sh /var/lib/postgresql/
du -sh /var/lib/redis/
```

### Конфигурационные файлы
- **PostgreSQL**: `/etc/postgresql/15/main/postgresql.conf`
- **Redis**: `/etc/redis/redis.conf`
- **Nginx**: `/etc/nginx/sites-available/`
- **Docker**: `docker-compose.yml`

### Логи
- **PostgreSQL**: `/var/log/postgresql/`
- **Redis**: `/var/log/redis/`
- **Nginx**: `/var/log/nginx/`
- **Docker**: `docker-compose logs`

---

## 🎯 Готово!

Теперь у вас есть полная рабочая система WorkerNet Portal на Ubuntu 24! 

**Следующие шаги:**
1. Следуйте инструкциям выше для установки
2. Настройте переменные окружения
3. Запустите проект
4. Создайте первого пользователя
5. Настройте мониторинг

**Нужна помощь?** Создайте issue в репозитории или обратитесь к документации!
