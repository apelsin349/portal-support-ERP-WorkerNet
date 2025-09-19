# Универсальный скрипт установки и обновления WorkerNet Portal

## Описание

`universal-install-update.sh` - это объединенный скрипт, который заменяет несколько отдельных скриптов и предоставляет единую точку входа для установки и обновления WorkerNet Portal на Ubuntu 24.04 LTS.

## Объединенная функциональность

Этот скрипт объединяет функциональность следующих скриптов:
- `install-ubuntu.sh` - полная установка с нуля (заменен на `universal-install-update.sh`)
- `quick-update.sh` - быстрое обновление существующей установки
- `setup.sh` - настройка через Docker
- `force-update-deps.sh` - принудительное обновление зависимостей

## Ключевые особенности

### 🎯 Автоматическое определение режима
- **Установка с нуля**: Если система не содержит WorkerNet Portal
- **Обновление**: Если обнаружена существующая установка

### 🔄 Интеллектуальная логика
- Проверка существующих сервисов systemd
- Обнаружение директорий проекта
- Проверка базы данных
- Автоматический выбор режима работы
- Интерактивный выбор Git репозитория

### 🛡️ Надежность
- Самообновление скрипта
- Обработка ошибок сети
- Fallback стратегии для зависимостей
- Идемпотентные операции

### 🌐 Сетевая устойчивость
- Проверка доступности репозиториев
- Переключение на российские зеркала при необходимости
- Множественные стратегии установки npm пакетов
- Настройка прокси из переменных окружения

## Использование

### Базовое использование
```bash
# Запуск с автоматическим определением режима
./scripts/universal-install-update.sh

# Установка конкретной ветки
./scripts/universal-install-update.sh --branch develop

# Обновление самого скрипта
./scripts/universal-install-update.sh --self-update
```

### Переменные окружения

```bash
# Неинтерактивный режим
WORKERNET_NONINTERACTIVE=1 ./scripts/universal-install-update.sh

# Указание ветки
WORKERNET_BRANCH=feature/new ./scripts/universal-install-update.sh

# Указание репозитория
WORKERNET_REPO_URL=https://github.com/user/repo.git ./scripts/universal-install-update.sh

# Самообновление скрипта
WORKERNET_SELF_UPDATE=1 ./scripts/universal-install-update.sh

# Настройка паролей
WORKERNET_DB_PASS=mypassword123
WORKERNET_REDIS_PASS=redispass123
WORKERNET_ADMIN_PASS=adminpass123
```

### Параметры командной строки

| Параметр | Описание |
|----------|----------|
| `--help`, `-h` | Показать справку |
| `--branch BRANCH` | Указать ветку для установки |
| `--self-update` | Обновить сам скрипт |

## Режимы работы

### 1. Режим установки с нуля (Fresh Installation)

Выполняется когда:
- Не обнаружены сервисы systemd WorkerNet
- Отсутствует директория проекта
- Нет базы данных workernet

**Шаги установки:**
1. Проверка системы (Ubuntu 24.04, права пользователя)
2. Проверка сетевой доступности
3. Обновление системы
4. Установка базовых пакетов
5. Установка Python 3.12/3.11
6. Установка Node.js 18
7. Установка PostgreSQL и Redis
8. Установка Docker
9. Выбор ветки Git
10. Клонирование репозитория
11. Настройка окружения (.env)
12. Настройка Python виртуального окружения
13. Настройка Node.js окружения
14. Сборка фронтенда
15. Настройка базы данных
16. Настройка Redis
17. Выполнение миграций
18. Создание суперпользователя
19. Настройка systemd сервисов
20. Настройка файрвола
21. Запуск сервисов

### 2. Режим обновления (Update)

Выполняется когда:
- Обнаружены существующие сервисы systemd
- Найдена директория проекта
- Существует база данных workernet

**Шаги обновления:**
1. Остановка сервисов
2. Раннее обновление репозитория (если возможно)
3. Обновление кода из репозитория
4. Обновление Python зависимостей
5. Обновление Node.js зависимостей
6. Выполнение миграций базы данных
7. Перезапуск сервисов

## Конфигурация

### Пароли по умолчанию
- **База данных**: `workernet123`
- **Redis**: `redis123`
- **Администратор**: `admin123`
- **PostgreSQL superuser**: `postgres123`

### Порты
- **Frontend**: 3000
- **Backend API**: 8000
- **SSH**: 22
- **HTTP**: 80
- **HTTPS**: 443

### Директории
- **Проект**: `$HOME/portal-support-ERP-WorkerNet`
- **Логи**: `$WORKERNET_ROOT/backend/logs`
- **Статические файлы**: `$WORKERNET_ROOT/backend/staticfiles`
- **Медиа файлы**: `$WORKERNET_ROOT/backend/media`

## Управление сервисами

После установки/обновления:

```bash
# Статус сервисов
sudo systemctl status workernet-backend workernet-frontend

# Запуск сервисов
sudo systemctl start workernet-backend workernet-frontend

# Остановка сервисов
sudo systemctl stop workernet-backend workernet-frontend

# Перезапуск сервисов
sudo systemctl restart workernet-backend workernet-frontend

# Просмотр логов
sudo journalctl -u workernet-backend -f
sudo journalctl -u workernet-frontend -f
```

## Доступ к сервисам

После успешной установки:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API документация**: http://localhost:8000/api/docs
- **Админ-панель**: http://localhost:8000/admin

**Данные для входа:**
- Пользователь: `admin`
- Пароль: `admin123` (или значение `WORKERNET_ADMIN_PASS`)

## Устранение неполадок

### Проблемы с сетью
```bash
# Проверка доступности репозиториев
curl -I https://github.com/
curl -I https://registry.npmjs.org/

# Настройка прокси (если необходимо)
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

### Проблемы с зависимостями
```bash
# Принудительное обновление Python зависимостей
cd $WORKERNET_ROOT/backend
source venv/bin/activate
pip install -r ../requirements.txt --upgrade --force-reinstall

# Принудительное обновление Node.js зависимостей
cd $WORKERNET_ROOT/frontend
rm -rf node_modules package-lock.json
npm install
```

### Проблемы с базой данных
```bash
# Проверка подключения к PostgreSQL
sudo -u postgres psql -c '\l'

# Пересоздание базы данных
sudo -u postgres psql -c "DROP DATABASE IF EXISTS workernet;"
sudo -u postgres psql -c "CREATE DATABASE workernet OWNER workernet;"
```

## Безопасность

### Рекомендации для продакшена
1. Измените пароли по умолчанию
2. Настройте SSL сертификаты
3. Ограничьте доступ к админ-панели
4. Настройте регулярные бэкапы базы данных
5. Обновите настройки файрвола

### Переменные окружения для безопасности
```bash
# Генерация безопасных паролей
WORKERNET_DB_PASS=$(openssl rand -base64 32)
WORKERNET_REDIS_PASS=$(openssl rand -base64 32)
WORKERNET_ADMIN_PASS=$(openssl rand -base64 16)
```

## Логирование

Скрипт ведет подробное логирование всех операций с цветовой индикацией:
- 🔵 **ИНФО** - информационные сообщения
- 🟢 **УСПЕХ** - успешные операции
- 🟡 **ВНИМАНИЕ** - предупреждения
- 🔴 **ОШИБКА** - ошибки

## Совместимость

- **ОС**: Ubuntu 24.04 LTS (рекомендуется)
- **Python**: 3.12, 3.11, или системный python3
- **Node.js**: 18.x
- **PostgreSQL**: 14+
- **Redis**: 6+
- **Docker**: 20.10+

## Поддержка

При возникновении проблем:
1. Проверьте логи сервисов
2. Убедитесь в доступности всех зависимостей
3. Проверьте права доступа к файлам
4. Обратитесь к документации проекта

## Версия

**Текущая версия**: 2025-01-27.1

**История изменений**:
- v2025-01-27.1: Первая версия универсального скрипта
- Объединение функциональности install-ubuntu.sh, quick-update.sh, setup.sh, force-update-deps.sh в единый скрипт
- Добавление автоматического определения режима работы
- Улучшение обработки ошибок и сетевой устойчивости
