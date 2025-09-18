# 📜 Скрипты WorkerNet Portal

## Обзор

Этот каталог содержит скрипты для установки, обновления и управления WorkerNet Portal.

## Основные скрипты

### 1. `install-ubuntu.sh` - Основной скрипт установки

**Назначение**: Полная установка WorkerNet Portal на Ubuntu 24.04 LTS

**Возможности**:
- ✅ Автоматическое определение существующей установки
- ✅ Выбор между обновлением и новой установкой
- ✅ Установка всех зависимостей
- ✅ Настройка базы данных и Redis
- ✅ Создание systemd сервисов
- ✅ Настройка автоматических обновлений

**Использование**:
```bash
# Интерактивная установка
./scripts/install-ubuntu.sh

# Неинтерактивная установка (для CI/CD)
export WORKERNET_NONINTERACTIVE=1
./scripts/install-ubuntu.sh

# Автоматическое обновление
export WORKERNET_AUTO_UPDATE=1
./scripts/install-ubuntu.sh

# Самообновление скрипта перед запуском
WORKERNET_SELF_UPDATE=1 ./scripts/install-ubuntu.sh
# или
./scripts/install-ubuntu.sh --self-update
```

**Режимы работы**:
- **Новая установка**: Полная установка с нуля
- **Обновление**: Обновление существующей установки
- **Неинтерактивный**: Автоматический выбор режима

### 2. `quick-update.sh` - Быстрое обновление

**Назначение**: Быстрое обновление существующей установки

**Возможности**:
- ✅ Проверка наличия обновлений
- ✅ Обновление кода из репозитория
- ✅ Обновление зависимостей
- ✅ Выполнение миграций
- ✅ Перезапуск сервисов

**Использование**:
```bash
# Быстрое обновление
./scripts/quick-update.sh

# Проверка обновлений
./scripts/quick-update.sh --check

# Принудительное обновление
./scripts/quick-update.sh --force

# Неинтерактивный режим
export WORKERNET_NONINTERACTIVE=1
./scripts/quick-update.sh

# Самообновление скрипта перед запуском
WORKERNET_SELF_UPDATE=1 ./scripts/quick-update.sh
# или
./scripts/quick-update.sh --self-update

# Если получаете "Permission denied"
chmod +x scripts/quick-update.sh scripts/install-ubuntu.sh
# или запускайте так
# Дополнительно: частые кейсы с правами

Сервисы и логи:

```bash
sudo systemctl restart workernet-backend workernet-frontend
sudo systemctl status workernet-backend workernet-frontend
sudo journalctl -u workernet-backend -f
sudo journalctl -u workernet-frontend -f
```

Папки статики/медиа:

```bash
sudo mkdir -p backend/staticfiles backend/media
sudo chown -R "$USER":"$USER" backend/staticfiles backend/media
sudo chmod -R u+rwX backend/staticfiles backend/media
```

Redis/Nginx/systemd:

```bash
echo "requirepass redis123" | sudo tee -a /etc/redis/redis.conf
sudo systemctl daemon-reload && sudo systemctl restart redis
```

PostgreSQL:

```bash
sudo -u postgres psql -c "ALTER USER workernet WITH PASSWORD 'workernet123';"
```
bash scripts/quick-update.sh
bash scripts/install-ubuntu.sh
```

### 3. `start-docker.sh` - Запуск в Docker

**Назначение**: Запуск WorkerNet Portal в Docker контейнерах

**Использование**:
```bash
# Запуск всех сервисов
./scripts/start-docker.sh

# Запуск с пересборкой
./scripts/start-docker.sh --build

# Остановка сервисов
./scripts/start-docker.sh --down
```

### 4. `ci-smoke-docker.sh` - Тестирование в Docker

**Назначение**: Быстрое тестирование в Docker окружении

**Использование**:
```bash
# Запуск тестов
./scripts/ci-smoke-docker.sh
```

### 5. `ci-smoke-ubuntu.sh` - Тестирование на Ubuntu

**Назначение**: Полное тестирование на Ubuntu сервере

**Использование**:
```bash
# Запуск тестов
./scripts/ci-smoke-ubuntu.sh
```

## Вспомогательные скрипты

### Скрипты исправления проблем

- `fix-npm-deps.sh` - Исправление проблем с npm
- `fix-django-imports.sh` - Исправление импортов Django
- `setup-database.sh` - Настройка базы данных
- `setup-redis.sh` - Настройка Redis
- `emergency-db-fix.sh` - Экстренное исправление БД
- `quick-db-fix.sh` - Быстрое исправление БД
- `check-database.sh` - Проверка базы данных

### Скрипты локализации

- `compile-translations.sh` - Компиляция переводов (Linux/macOS)
- `compile-translations.bat` - Компиляция переводов (Windows)

## Переменные окружения

### Основные переменные

```bash
# Режим работы
WORKERNET_NONINTERACTIVE=1    # Неинтерактивный режим
WORKERNET_AUTO_UPDATE=1       # Автоматическое обновление
CI=1                          # CI/CD режим

# Пароли
WORKERNET_DB_PASS=password    # Пароль базы данных
WORKERNET_REDIS_PASS=password # Пароль Redis
WORKERNET_POSTGRES_SUPER_PASS=password # Пароль суперпользователя PostgreSQL

# Пути
WORKERNET_ROOT=/opt/workernet # Корневая директория проекта
```

### Переменные для разработки

```bash
# Django
DJANGO_SETTINGS_MODULE=config.settings
DEBUG=True
SECRET_KEY=development-secret-key

# База данных
DATABASE_URL=postgresql://workernet:password@localhost:5432/workernet
REDIS_URL=redis://:password@localhost:6379/0

# Node.js
NODE_ENV=development
```

## Логи и отладка

### Логи установки
```bash
# Логи основного скрипта установки
tail -f /var/log/workernet-install.log

# Логи обновлений
tail -f /var/log/workernet-update.log

# Логи сервисов
sudo journalctl -u workernet-backend -f
sudo journalctl -u workernet-frontend -f
```

### Отладка
```bash
# Включить отладочный режим
export DEBUG=1
./scripts/install-ubuntu.sh

# Проверить статус сервисов
sudo systemctl status workernet-backend workernet-frontend

# Проверить подключение к базе данных
sudo -u postgres psql -c '\l'

# Проверить подключение к Redis
redis-cli ping
```

## Автоматизация

### Cron задачи
```bash
# Автоматическое обновление (ежедневно в 2:00)
0 2 * * * /opt/update-workernet.sh >> /var/log/workernet-update.log 2>&1

# Проверка обновлений (каждый час)
0 * * * * /opt/workernet/scripts/quick-update.sh --check

# Резервное копирование (ежедневно в 1:00)
0 1 * * * /opt/backup-workernet.sh
```

### Systemd сервисы
```bash
# Статус сервисов
sudo systemctl status workernet-backend workernet-frontend

# Управление сервисами
sudo systemctl start workernet-backend
sudo systemctl stop workernet-backend
sudo systemctl restart workernet-backend
sudo systemctl enable workernet-backend
sudo systemctl disable workernet-backend
```

## Безопасность

### Права доступа
```bash
# Установить правильные права на скрипты
chmod +x scripts/*.sh
chmod 600 scripts/*.sh  # Для скриптов с паролями

# Ограничить доступ к конфигурационным файлам
chmod 600 .env
chmod 600 /opt/workernet/.env
```

### Очистка логов
```bash
# Очистить старые логи
find /var/log -name "*workernet*" -mtime +30 -delete

# Ротация логов
logrotate /etc/logrotate.d/workernet
```

## Устранение проблем

### Частые проблемы

1. **Ошибка прав доступа**
   ```bash
   sudo chown -R $USER:$USER /opt/workernet
   chmod +x scripts/*.sh
   ```

2. **Проблемы с базой данных**
   ```bash
   ./scripts/quick-db-fix.sh
   ```

3. **Проблемы с npm**
   ```bash
   ./scripts/fix-npm-deps.sh
   ```

4. **Проблемы с импортами Django**
   ```bash
   ./scripts/fix-django-imports.sh
   ```

### Восстановление
```bash
# Полное восстановление
./scripts/install-ubuntu.sh

# Восстановление только сервисов
sudo systemctl daemon-reload
sudo systemctl restart workernet-backend workernet-frontend
```

---

## 🎯 Заключение

Скрипты WorkerNet Portal обеспечивают:

- ✅ **Простая установка** одной командой
- ✅ **Автоматические обновления** без вмешательства
- ✅ **Быстрое обновление** для обычных случаев
- ✅ **Исправление проблем** автоматически
- ✅ **Мониторинг и логирование** всех операций
- ✅ **Поддержка CI/CD** и автоматизации

**Основные команды:**
- `./scripts/install-ubuntu.sh` - Установка/обновление
- `./scripts/quick-update.sh` - Быстрое обновление
- `./scripts/quick-update.sh --check` - Проверка обновлений
- `sudo systemctl status workernet-backend` - Статус сервисов
