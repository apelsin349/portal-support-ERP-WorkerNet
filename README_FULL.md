# WorkerNet Portal - Полная система технической поддержки для ERP

## 🚀 Быстрый старт

### 1) Важно: запускать не под root
```bash
adduser workernet
usermod -aG sudo workernet
su - workernet
```

### 2) Автоматическая установка на Ubuntu 24.04 LTS (рекомендуется)
```bash
# Скачать и запустить скрипт установки (с актуальным URL репозитория)
curl -fsSL https://raw.githubusercontent.com/apelsin349/portal-support-ERP-WorkerNet/main/scripts/install-ubuntu.sh \
| sed 's|https://github.com/your-org/portal-support-ERP-WorkerNet.git|https://github.com/apelsin349/portal-support-ERP-WorkerNet.git|' \
| bash
```

### 3) Запуск через Docker вручную

```bash
# Клонировать репозиторий
git clone https://github.com/apelsin349/portal-support-ERP-WorkerNet.git
cd portal-support-ERP-WorkerNet

# Установить Docker Compose (если команда docker compose недоступна)
sudo apt update
sudo apt install -y docker-compose-plugin || sudo apt install -y docker-compose

# Запустить все сервисы
chmod +x scripts/start-docker.sh
./scripts/start-docker.sh start
```

### 4) Быстрая проверка (smoke-тест) в Docker
```bash
chmod +x scripts/ci-smoke-docker.sh
./scripts/ci-smoke-docker.sh
```

## 📋 Системные требования

### Минимальные требования
- **OS**: Ubuntu 24.04 LTS (или новее)
- **RAM**: 4 GB
- **CPU**: 2 ядра
- **Диск**: 20 GB свободного места
- **Сеть**: Интернет соединение

### Рекомендуемые требования
- **OS**: Ubuntu 24.04 LTS
- **RAM**: 8 GB
- **CPU**: 4 ядра
- **Диск**: 50 GB SSD
- **Сеть**: Стабильное интернет соединение

## 🛠️ Установка

### Вариант 1: Автоматическая установка (Ubuntu 24.04)

```bash
# Скачать скрипт установки
wget https://raw.githubusercontent.com/apelsin349/portal-support-ERP-WorkerNet/main/scripts/install-ubuntu.sh

# Сделать исполняемым
chmod +x install-ubuntu.sh

# Запустить установку
# Важно: скрипт не должен выполняться под root.
# Если нужно, замените URL репозитория внутри скрипта на актуальный и запустите:
sed -i 's|https://github.com/your-org/portal-support-ERP-WorkerNet.git|https://github.com/apelsin349/portal-support-ERP-WorkerNet.git|' install-ubuntu.sh
./install-ubuntu.sh
```

### Вариант 2: Docker Compose (все ОС)

```bash
# Клонировать репозиторий
git clone https://github.com/apelsin349/portal-support-ERP-WorkerNet.git
cd portal-support-ERP-WorkerNet

# Настроить переменные окружения
cp env.example .env
nano .env  # Отредактировать настройки

# Запустить сервисы
docker-compose up -d --build

# Выполнить миграции
docker-compose exec backend python manage.py migrate

# Создать суперпользователя
docker-compose exec backend python manage.py createsuperuser
```

### Вариант 3: Ручная установка

#### 1. Установка зависимостей

```bash
# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить основные пакеты
sudo apt install -y curl wget git build-essential software-properties-common

# Установить Python (используйте доступный python3)
sudo apt install -y python3 python3-venv python3-dev python3-pip

# Установить Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Установить PostgreSQL 15
sudo apt install -y postgresql postgresql-contrib postgresql-client

# Установить Redis
sudo apt install -y redis-server

# Установить Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

#### 2. Настройка базы данных

```bash
# Создать базу данных и пользователя
sudo -u postgres psql -c "CREATE DATABASE worker_net;"
sudo -u postgres psql -c "CREATE DATABASE worker_net_test;"
sudo -u postgres psql -c "CREATE USER workernet WITH PASSWORD 'workernet123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE worker_net TO workernet;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE worker_net_test TO workernet;"
```

#### 3. Настройка Redis

```bash
# Настроить пароль для Redis
sudo sed -i 's/# requirepass foobared/requirepass redis123/' /etc/redis/redis.conf
sudo systemctl restart redis-server
```

#### 4. Установка приложения

```bash
# Клонировать репозиторий
git clone https://github.com/your-org/portal-support-ERP-WorkerNet.git
cd portal-support-ERP-WorkerNet

# Настроить переменные окружения
cp env.example .env
nano .env  # Отредактировать настройки

# Установить Python зависимости
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Если при миграциях увидите ошибку ModuleNotFoundError: django_filters
# установите пакет явно (или обновите файл requirements.txt из репозитория):
pip install django-filter==23.5

# Установить Node.js зависимости
cd ../frontend
npm install

# Выполнить миграции
cd ../backend
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 🚀 Запуск

### Запуск через Docker

```bash
# Запустить все сервисы
docker-compose up -d

# Проверить статус
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

### Запуск локально

```bash
# Запустить Redis
redis-server

# Запустить PostgreSQL
sudo systemctl start postgresql

# Запустить backend
cd backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# В новом терминале - запустить frontend
cd frontend
npm start
```

## 🎯 Smoke-тесты установки и работоспособности

### Полная проверка на новом сервере Ubuntu 24.04
```bash
chmod +x scripts/ci-smoke-ubuntu.sh
./scripts/ci-smoke-ubuntu.sh
```

Что выполняет автоматическая проверка:
- Устанавливает зависимости (Python/Node/PostgreSQL/Redis/Docker) — для Ubuntu
- Собирает и запускает контейнеры через Docker Compose
- Применяет миграции базы данных
- Создаёт суперпользователя (admin/admin123), если отсутствует
- Проверяет `/health/` (ожидается 200), выполняет запросы к API (JWT + /api/v1/tickets/)
- Проверяет доступность фронтенда (:3000) и базовых метрик
- При сбое выводит логи и завершает выполнение с ошибкой

## 🌐 Доступные интерфейсы

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Admin Panel**: http://localhost:8000/admin
- **Grafana**: http://localhost:3001 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Kibana**: http://localhost:5601
- **Celery Flower**: http://localhost:5555

## 🔧 Управление сервисами

### Docker команды

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Просмотр логов
docker-compose logs -f [service_name]

# Выполнение команд
docker-compose exec backend python manage.py migrate
docker-compose exec frontend npm run build
```

### Systemd команды (при локальной установке)

```bash
# Запуск
sudo systemctl start workernet-backend workernet-frontend

# Остановка
sudo systemctl stop workernet-backend workernet-frontend

# Перезапуск
sudo systemctl restart workernet-backend workernet-frontend

# Статус
sudo systemctl status workernet-backend workernet-frontend

# Логи
sudo journalctl -u workernet-backend -f
sudo journalctl -u workernet-frontend -f
```

## 📊 Мониторинг

### Prometheus метрики

- **Response time**: 95th percentile response time
- **Error rate**: HTTP error rate
- **Database performance**: Query duration, connections
- **Memory usage**: Application memory consumption
- **CPU usage**: Application CPU consumption

### Grafana дашборды

- **System Overview**: Общий обзор системы
- **Application Metrics**: Метрики приложения
- **Database Performance**: Производительность БД
- **Infrastructure**: Инфраструктурные метрики

### Логирование

- **Application logs**: Логи приложения
- **Access logs**: Логи доступа
- **Error logs**: Логи ошибок
- **Performance logs**: Логи производительности

## 🔐 Безопасность

### Настройка файрвола

```bash
# Включить UFW
sudo ufw enable

# Разрешить необходимые порты
sudo ufw allow 22      # SSH
sudo ufw allow 80      # HTTP
sudo ufw allow 443     # HTTPS
sudo ufw allow 3000    # Frontend
sudo ufw allow 8000    # API
```

### SSL сертификаты

```bash
# Установить Certbot
sudo apt install certbot python3-certbot-nginx

# Получить SSL сертификат
sudo certbot --nginx -d yourdomain.com
```

### Настройка паролей

```bash
# Изменить пароли по умолчанию
# В файле .env:
DB_PASSWORD=your_secure_password
REDIS_PASSWORD=your_secure_redis_password
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
```

## 🛠️ Разработка

### Backend разработка

```bash
cd backend
source venv/bin/activate

# Запуск в режиме разработки
python manage.py runserver 0.0.0.0:8000

# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Запуск тестов
pytest

# Линтинг
flake8 .
black .
isort .
```

### Frontend разработка

```bash
cd frontend

# Запуск в режиме разработки
npm start

# Сборка для продакшена
npm run build

# Запуск тестов
npm test

# Линтинг
npm run lint
```

### База данных

```bash
# Подключение к PostgreSQL
psql -U workernet -d worker_net -h localhost

# Создание резервной копии
pg_dump -U workernet -d worker_net > backup.sql

# Восстановление из резервной копии
psql -U workernet -d worker_net < backup.sql
```

## 📱 Мобильное приложение

### Установка React Native CLI

```bash
npm install -g @react-native-community/cli
```

### Запуск мобильного приложения

```bash
cd mobile

# Android
npx react-native run-android

# iOS
npx react-native run-ios
```

## 🔧 Конфигурация

### Переменные окружения

Основные переменные в файле `.env`:

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://workernet:password@localhost:5432/worker_net

# Redis
REDIS_URL=redis://:password@localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security
CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000
```

### Настройка мониторинга

Файлы конфигурации:
- `config/prometheus.yml` - Prometheus
- `config/alert_rules.yml` - Правила алертинга
- `config/grafana/` - Дашборды Grafana

## 🚨 Устранение неполадок

### Проблемы с Docker

```bash
# Очистка Docker
docker system prune -a
docker volume prune

# Перезапуск всех сервисов
docker-compose down
docker-compose up -d --build
```

### Проблемы с базой данных

```bash
# Проверка подключения
psql -U workernet -d worker_net -h localhost

# Сброс базы данных
dropdb -U workernet worker_net
createdb -U workernet worker_net
python manage.py migrate
```

### Проблемы с Redis

```bash
# Проверка статуса
redis-cli ping

# Очистка Redis
redis-cli flushall
```

### Проблемы с портами

```bash
# Проверка занятых портов
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :3000

# Освобождение портов
sudo kill -9 <PID>
```

## 📚 Документация

### API документация

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Техническая документация

- **Архитектура**: [docs/architecture.md](docs/architecture.md)
- **API Reference**: [docs/api.md](docs/api.md)
- **Deployment**: [docs/deployment.md](docs/deployment.md)
- **Troubleshooting**: [docs/troubleshooting.md](docs/troubleshooting.md)

## 🤝 Вклад в проект

### Установка для разработки

```bash
# Форк репозитория
git clone https://github.com/your-username/portal-support-ERP-WorkerNet.git
cd portal-support-ERP-WorkerNet

# Создать ветку
git checkout -b feature/your-feature

# Установить зависимости
cd backend && pip install -r requirements-dev.txt
cd ../frontend && npm install

# Запустить тесты
cd ../backend && pytest
cd ../frontend && npm test

# Создать Pull Request
```

### Стандарты кода

- **Python**: PEP 8, Black, isort, flake8
- **JavaScript**: ESLint, Prettier
- **Git**: Conventional Commits
- **Testing**: pytest, Jest

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 📞 Поддержка

- **Issues**: [GitHub Issues](https://github.com/apelsin349/portal-support-ERP-WorkerNet/issues)
- **Discussions**: [GitHub Discussions](https://github.com/apelsin349/portal-support-ERP-WorkerNet/discussions)
- **Email**: support@workernet.com
- **Documentation**: [docs.workernet.com](https://docs.workernet.com)

---

## 🎯 Готово!

Теперь у вас есть полная рабочая система WorkerNet Portal! 

**Следующие шаги:**
1. Доступ к приложению: http://localhost:3000
2. Вход в систему: admin/admin123
3. Настройка вашего тенанта
4. Настройка мониторинга в Grafana
5. Настройка SSL для продакшена

**Нужна помощь?** Создайте issue в репозитории или обратитесь к документации!
