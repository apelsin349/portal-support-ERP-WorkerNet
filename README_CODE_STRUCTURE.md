Структура кода WorkerNet Portal

Этот документ описывает структуру кода проекта WorkerNet Portal и содержит ссылки на все файлы с кодом.

## 📁 Структура проекта

```
portal-support-ERP-WorkerNet/
├── backend/                    # Backend приложение (Python/Django)
│   ├── app/
│   │   ├── core/              # Основные модули системы
│   │   │   ├── feature_flags.py      # A/B тестирование и feature flags
│   │   │   ├── ab_testing.py         # Статистический анализ A/B тестов
│   │   │   ├── incident_management.py # Управление инцидентами
│   │   │   ├── performance_monitoring.py # APM и мониторинг производительности
│   │   │   └── api_versioning.py     # Управление версиями API
│   │   ├── api/               # API endpoints
│   │   ├── models/            # Модели данных
│   │   ├── services/          # Бизнес-логика
│   │   └── utils/             # Утилиты
│   ├── config/                # Конфигурация
│   ├── migrations/            # Миграции БД
│   ├── tests/                 # Тесты
│   └── requirements.txt       # Python зависимости
├── frontend/                   # Frontend приложение (React)
│   ├── src/
│   │   ├── components/        # React компоненты
│   │   ├── pages/            # Страницы
│   │   ├── services/         # API сервисы
│   │   └── utils/            # Утилиты
│   │       ├── rum-monitor.js        # Real User Monitoring
│   │       └── ab-testing.js         # A/B тестирование на frontend
│   ├── public/               # Статические файлы
│   └── package.json          # Node.js зависимости
├── database/                  # База данных
│   ├── migrations/           # SQL миграции
│   │   └── 001_initial_schema.sql    # Начальная схема БД
│   └── queries/              # SQL запросы
│       └── performance_queries.sql   # Запросы для мониторинга
├── docker/                   # Docker конфигурации
│   └── docker-compose.yml    # Docker Compose конфигурация
├── config/                   # Конфигурационные файлы
│   ├── prometheus.yml        # Конфигурация Prometheus
│   └── alert_rules.yml       # Правила алертинга
├── scripts/                  # Скрипты развертывания
│   └── setup.sh             # Скрипт установки
└── README.md                # Основная документация
```

## 🔧 Основные модули системы

### 1. A/B тестирование и Feature Flags

**Backend:**
- [`backend/app/core/feature_flags.py`](backend/app/core/feature_flags.py) - Система feature flags и экспериментов
- [`backend/app/core/ab_testing.py`](backend/app/core/ab_testing.py) - Статистический анализ A/B тестов

**Frontend:**
- [`frontend/src/utils/ab-testing.js`](frontend/src/utils/ab-testing.js) - A/B тестирование на клиенте
- [`frontend/src/utils/rum-monitor.js`](frontend/src/utils/rum-monitor.js) - Real User Monitoring

### 2. Управление инцидентами

**Backend:**
- [`backend/app/core/incident_management.py`](backend/app/core/incident_management.py) - Полная система управления инцидентами

**Функции:**
- Автоматическое обнаружение инцидентов
- Классификация по severity (P1-P4)
- Workflow управления инцидентами
- Система уведомлений
- Post-mortem анализ
- Метрики MTTR/MTTD

### 3. Мониторинг производительности

**Backend:**
- [`backend/app/core/performance_monitoring.py`](backend/app/core/performance_monitoring.py) - APM и мониторинг

**Функции:**
- Distributed tracing с OpenTelemetry
- Сбор метрик производительности
- Мониторинг базы данных
- Real User Monitoring (RUM)
- Synthetic monitoring
- Система алертинга
- Оптимизация кэширования

### 4. Управление версиями API

**Backend:**
- [`backend/app/core/api_versioning.py`](backend/app/core/api_versioning.py) - Система версионирования API

**Функции:**
- Поддержка множественных версий API
- Стратегии версионирования (URL, Header, Query)
- Backward compatibility
- Migration tools
- Deprecation management
- Feature flags per version

### 5. База данных

**Схема:**
- [`database/migrations/001_initial_schema.sql`](database/migrations/001_initial_schema.sql) - Полная схема БД

**Мониторинг:**
- [`database/queries/performance_queries.sql`](database/queries/performance_queries.sql) - Запросы для анализа производительности

**Таблицы:**
- `tenants` - Мультитенантность
- `users` - Пользователи системы
- `tickets` - Тикеты поддержки
- `knowledge_articles` - База знаний
- `incidents` - Инциденты
- `ab_tests` - A/B тесты
- `performance_metrics` - Метрики производительности
- `audit_logs` - Аудит действий

### 6. Инфраструктура

**Docker:**
- [`docker/docker-compose.yml`](docker/docker-compose.yml) - Полная конфигурация всех сервисов

**Мониторинг:**
- [`config/prometheus.yml`](config/prometheus.yml) - Конфигурация Prometheus
- [`config/alert_rules.yml`](config/alert_rules.yml) - Правила алертинга

**Развертывание:**
- [`scripts/setup.sh`](scripts/setup.sh) - Автоматический скрипт установки

## 🚀 Быстрый старт

### 1. Клонирование и настройка
```bash
git clone https://github.com/apelsin349/portal-support-ERP-WorkerNet.git
cd portal-support-ERP-WorkerNet
```

### 2. Автоматическая установка
```bash
# Linux/macOS
./scripts/setup.sh

# Windows
bash scripts/setup.sh
```

### 3. Ручная установка
```bash
# Копирование конфигурации
cp .env.example .env

# Запуск через Docker
docker-compose up -d --build

# Инициализация БД
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

## 📊 Мониторинг и метрики

### Доступные интерфейсы:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Celery Flower**: http://localhost:5555

### Основные метрики:
- Response time (95th percentile)
- Error rate
- Database query performance
- Memory usage
- CPU usage
- Active connections
- Queue length

## 🔧 Разработка

### Backend (Python/Django)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
python manage.py runserver
```

### Frontend (React)
```bash
cd frontend
npm install
npm start
```

### Тестирование
```bash
# Backend тесты
cd backend
pytest

# Frontend тесты
cd frontend
npm test
```

## 📝 Документация

- **Основная документация**: [README.md](README.md)
- **API документация**: http://localhost:8000/api/docs
- **Техническое задание**: [README.md](README.md#техническое-задание)

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE) для деталей.
