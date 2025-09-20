# 📚 WorkerNet Portal - Полное руководство

## 📋 Оглавление

- [🚀 Быстрый старт](#-быстрый-старт)
- [🏗️ Архитектура системы](#-архитектура-системы)
- [💻 Разработка](#-разработка)
- [🔧 Развертывание](#-развертывание)
- [📚 API документация](#-api-документация)
- [🧪 Тестирование](#-тестирование)
- [🌐 Локализация](#-локализация)
- [🔍 Устранение неполадок](#-устранение-неполадок)
- [📦 Обновления](#-обновления)
- [🎯 Современные практики](#-современные-практики)

---

## 🚀 Быстрый старт

WorkerNet Portal - это современная система технической поддержки с web-интерфейсом и API.

### Быстрый запуск

```bash
# Клонировать репозиторий
git clone https://github.com/apelsin349/portal-support-ERP-WorkerNet.git
cd portal-support-ERP-WorkerNet

# Запуск с Docker (рекомендуется)
docker compose up -d

# Или установка на Ubuntu
./scripts/universal-install-update.sh
```

### Доступ к приложению

**⚠️ Замените `localhost` на ваш домен или IP-адрес сервера!**

- **Web интерфейс**: http://YOUR_DOMAIN_OR_IP:3000
- **API**: http://YOUR_DOMAIN_OR_IP:8000/api/v1/
- **Админ панель**: http://YOUR_DOMAIN_OR_IP:8000/admin/
- **Документация API**: http://YOUR_DOMAIN_OR_IP:8000/api/docs/

**Примеры:**
- `http://192.168.1.100:3000` - для локальной сети
- `http://yourdomain.com:3000` - для домена
- `https://portal.yourdomain.com` - с SSL и Nginx

### Первоначальные учетные данные

- **Логин**: admin
- **Пароль**: admin123

---

## 🏗️ Архитектура системы

### Компоненты

- **Frontend**: React 18+ с TypeScript и Material-UI
- **Backend**: Django 4.2+ с Django REST Framework
- **База данных**: PostgreSQL 15+
- **Кэш**: Redis 7+
- **Очереди**: Celery с Redis broker
- **Мониторинг**: Prometheus + Grafana
- **Логирование**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Reverse Proxy**: Nginx

### Технический стек

```
Frontend (React) ←→ Nginx ←→ API (Django) ←→ PostgreSQL
                        ↓                        ↓
                    Redis (Cache + Queue)    Elasticsearch
                        ↓                        ↓
                   Celery Workers            Kibana
                        ↓
                   Prometheus ←→ Grafana
```

### Мультитенантность

Система поддерживает несколько организаций (тенантов) с изоляцией данных на уровне базы данных.

---

## 💻 Разработка

### Настройка среды разработки

```bash
# Backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
pip install -r ../requirements-dev.txt

# Frontend  
cd frontend
npm install
npm run generate-icons

# Базы данных
sudo apt install postgresql redis-server
```

### Структура проекта

```
portal-support-ERP-WorkerNet/
├── backend/               # Django API
│   ├── app/              # Основное приложение
│   ├── config/           # Настройки Django
│   └── requirements.txt  # Python зависимости
├── frontend/             # React приложение
│   ├── src/             # Исходный код
│   └── package.json     # Node.js зависимости
├── scripts/             # Скрипты автоматизации
└── docker/              # Docker конфигурация
```

### Ключевые команды

```bash
# Backend
python manage.py runserver    # Запуск сервера
python manage.py migrate      # Миграции
python manage.py test         # Тесты
python manage.py collectstatic # Сбор статических файлов

# Frontend
npm run dev                   # Запуск dev сервера
npm test                      # Запуск тестов
npm run build                 # Сборка для продакшна
npm run lint                  # Проверка кода

# Docker
docker compose up -d          # Запуск всех сервисов
docker compose down           # Остановка сервисов
docker compose logs -f        # Просмотр логов
```

---

## 🔧 Развертывание

### Системные требования

- **ОС**: Ubuntu 22.04 LTS / 24.04 LTS (рекомендуется)
- **CPU**: 4+ ядра (рекомендуется 8 для production)
- **RAM**: 8+ GB (рекомендуется 16 GB для production)
- **Диск**: 50+ GB SSD (рекомендуется 100+ GB для production)
- **Сеть**: Интернет соединение

### Установка на Ubuntu

```bash
# Скачать и запустить скрипт установки
wget https://raw.githubusercontent.com/apelsin349/portal-support-ERP-WorkerNet/main/scripts/universal-install-update.sh
chmod +x universal-install-update.sh
./universal-install-update.sh
```

### Docker развертывание

```bash
# Создать .env файл
cp env.example .env

# Отредактировать .env файл
nano .env

# Запустить все сервисы
docker compose up -d

# Проверить статус
docker compose ps

# Просмотр логов
docker compose logs -f
```

### Настройка Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
    }
}
```

---

## 📚 API документация

### Базовый URL

```
http://localhost:8000/api/v1/
```

### Аутентификация

```bash
# Получить токен
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Использовать токен
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/v1/tickets/
```

### Основные endpoints

- `GET /api/v1/tickets/` - Список тикетов
- `POST /api/v1/tickets/` - Создать тикет
- `GET /api/v1/knowledge/articles/` - Статьи базы знаний
- `GET /api/v1/users/` - Пользователи

### Интерактивная документация

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

---

## 🧪 Тестирование

### Backend тесты

```bash
cd backend
source venv/bin/activate

# Все тесты
python manage.py test

# Конкретное приложение
python manage.py test app

# С покрытием кода
coverage run manage.py test
coverage report
```

### Frontend тесты

```bash
cd frontend

# Unit тесты
npm test

# E2E тесты
npm run cypress:run

# С покрытием
npm test -- --coverage
```

### Load тестирование

```bash
# С использованием Locust
cd backend
locust -f load_tests.py --host=http://localhost:8000
```

---

## 🌐 Локализация

### Django (Backend)

```python
# Создание переводов
python manage.py makemessages -l ru
python manage.py compilemessages

# В коде
from django.utils.translation import gettext as _
message = _("Hello, World!")
```

### React (Frontend)

```javascript
import { useTranslation } from 'react-i18next';

const Component = () => {
  const { t } = useTranslation();
  return <p>{t('hello_world')}</p>;
};
```

### Поддерживаемые языки

- Английский (en) - по умолчанию
- Русский (ru) - полная поддержка

---

## 🔍 Устранение неполадок

### Частые проблемы

#### 1. Ошибка подключения к базе данных

```bash
# Быстрое исправление
./scripts/quick-db-fix.sh

# Или ручное исправление
sudo -u postgres psql -c "CREATE USER workernet WITH PASSWORD 'workernet123';"
sudo -u postgres psql -c "CREATE DATABASE workernet OWNER workernet;"
```

#### 2. Проблемы с npm

```bash
# Сброс npm кэша
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

#### 3. Проблемы с Django импортами

```bash
# Исправление импортов
./scripts/fix-django-imports.sh
```

### Скрипты диагностики

- `./scripts/check-database.sh` - Проверка базы данных
- `./scripts/emergency-npm-reset.sh` - Экстренный сброс npm
- `./scripts/fix-django-imports.sh` - Исправление импортов Django

---

## 📦 Обновления

### Автоматические обновления

```bash
# Включить автообновления
echo "AUTO_UPDATE=true" >> .env

# Настроить расписание (crontab)
0 2 * * 0 /path/to/scripts/quick-update.sh
```

### Ручное обновление

```bash
# Быстрое обновление
./scripts/quick-update.sh

# Полное обновление
./scripts/universal-install-update.sh --update
```

### Откат обновлений

```bash
# Откат к предыдущей версии
git checkout HEAD~1
docker compose down && docker compose up -d
```

---

## 🎯 Современные практики

### Архитектурные паттерны

- **Clean Architecture** - разделение на слои
- **Domain-Driven Design** - доменно-ориентированная разработка
- **CQRS** - разделение команд и запросов

### Code Quality

- **Pre-commit hooks** - автоматическая проверка кода
- **ESLint/Prettier** - линтинг и форматирование
- **Type checking** - TypeScript и mypy

### CI/CD

```yaml
# GitHub Actions
- Автоматическое тестирование
- Сборка Docker образов
- Развертывание в продакшн
```

### Безопасность

- **JWT аутентификация**
- **RBAC авторизация**
- **HTTPS encryption**
- **Input validation**

---

## 📞 Поддержка

### Документация

- **Техническая документация**: в папке `docs/`
- **API документация**: http://localhost:8000/api/docs/
- **Видеоуроки**: ссылки в README

### Контакты

- **Email**: support@workernet.com
- **GitHub Issues**: https://github.com/apelsin349/portal-support-ERP-WorkerNet/issues
- **Telegram**: @workernet_support

### Лицензия

MIT License - см. файл LICENSE для деталей.

---

## 🔗 Быстрые ссылки

**⚠️ Замените `YOUR_DOMAIN_OR_IP` на ваш домен или IP-адрес!**

| Компонент | URL | Описание |
|-----------|-----|----------|
| Web App | http://YOUR_DOMAIN_OR_IP:3000 | Основное приложение |
| API | http://YOUR_DOMAIN_OR_IP:8000/api/v1/ | REST API |
| Admin | http://YOUR_DOMAIN_OR_IP:8000/admin/ | Админ панель |
| Docs | http://YOUR_DOMAIN_OR_IP:8000/api/docs/ | API документация |
| Grafana | http://YOUR_DOMAIN_OR_IP:3001 | Мониторинг |
| Prometheus | http://YOUR_DOMAIN_OR_IP:9090 | Метрики |
| Celery Flower | http://YOUR_DOMAIN_OR_IP:5555 | Мониторинг задач |
| Kibana | http://YOUR_DOMAIN_OR_IP:5601 | Логи и аналитика |

**Примеры для локальной сети:**
- `http://192.168.1.100:3000` - Web App
- `http://192.168.1.100:8000/api/v1/` - API

---

**Успешной работы с WorkerNet Portal! 🚀**
