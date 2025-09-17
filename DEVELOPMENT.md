# 🛠️ Разработка WorkerNet Portal

## Настройка среды разработки

### 1. Клонирование репозитория

```bash
# Клонировать репозиторий
git clone https://github.com/your-org/portal-support-ERP-WorkerNet.git
cd portal-support-ERP-WorkerNet

# Создать ветку для разработки
git checkout -b feature/your-feature-name
```

### 2. Установка зависимостей

#### Backend (Python/Django)
```bash
cd backend

# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows

# Установить зависимости
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Настроить pre-commit hooks
pre-commit install
```

#### Frontend (React/TypeScript)
```bash
cd frontend

# Установить зависимости
npm install

# Установить дополнительные инструменты
npm install -g eslint prettier typescript
```

### 3. Настройка базы данных

```bash
# Создать базу данных
createdb worker_net
createdb worker_net_test

# Выполнить миграции
cd backend
source venv/bin/activate
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Загрузить тестовые данные
python manage.py loaddata fixtures/initial_data.json
```

### 4. Настройка Redis

```bash
# Запустить Redis
redis-server

# Проверить подключение
redis-cli ping
```

### 5. Запуск в режиме разработки

#### Backend
```bash
cd backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

#### Frontend
```bash
cd frontend
npm start
```

## Структура проекта

```
portal-support-ERP-WorkerNet/
├── backend/                    # Backend приложение (Python/Django)
│   ├── app/                    # Основное приложение
│   │   ├── core/              # Основные модули системы
│   │   │   ├── feature_flags.py      # A/B тестирование
│   │   │   ├── ab_testing.py         # Статистический анализ
│   │   │   ├── incident_management.py # Управление инцидентами
│   │   │   ├── performance_monitoring.py # Мониторинг производительности
│   │   │   └── api_versioning.py     # Управление версиями API
│   │   ├── api/               # API endpoints
│   │   │   ├── views.py       # API views
│   │   │   ├── serializers.py # API serializers
│   │   │   ├── urls.py        # API URLs
│   │   │   ├── routing.py     # WebSocket routing
│   │   │   └── consumers.py   # WebSocket consumers
│   │   ├── models/            # Модели данных
│   │   │   ├── tenant.py      # Мультитенантность
│   │   │   ├── ticket.py      # Тикеты поддержки
│   │   │   ├── knowledge.py   # База знаний
│   │   │   └── __init__.py
│   │   ├── services/          # Бизнес-логика
│   │   ├── utils/             # Утилиты
│   │   └── tests/             # Тесты
│   ├── config/                # Конфигурация Django
│   │   ├── settings.py        # Настройки
│   │   ├── urls.py           # URL конфигурация
│   │   ├── wsgi.py           # WSGI конфигурация
│   │   └── asgi.py           # ASGI конфигурация
│   ├── migrations/            # Миграции БД
│   ├── static/               # Статические файлы
│   ├── media/                # Медиа файлы
│   ├── logs/                 # Логи
│   ├── requirements.txt      # Python зависимости
│   ├── requirements-dev.txt  # Dev зависимости
│   ├── manage.py             # Django management
│   └── Dockerfile            # Docker конфигурация
├── frontend/                   # Frontend приложение (React)
│   ├── src/                   # Исходный код
│   │   ├── components/        # React компоненты
│   │   │   ├── common/        # Общие компоненты
│   │   │   ├── forms/         # Формы
│   │   │   ├── layout/        # Макет
│   │   │   └── ui/            # UI компоненты
│   │   ├── pages/            # Страницы
│   │   │   ├── auth/          # Аутентификация
│   │   │   ├── dashboard/     # Дашборд
│   │   │   ├── tickets/       # Тикеты
│   │   │   ├── knowledge/     # База знаний
│   │   │   └── settings/      # Настройки
│   │   ├── services/         # API сервисы
│   │   │   ├── api.ts        # API клиент
│   │   │   ├── auth.ts       # Аутентификация
│   │   │   ├── tickets.ts    # Тикеты
│   │   │   └── knowledge.ts  # База знаний
│   │   ├── utils/            # Утилиты
│   │   │   ├── rum-monitor.js        # Real User Monitoring
│   │   │   ├── ab-testing.js         # A/B тестирование
│   │   │   ├── helpers.ts    # Вспомогательные функции
│   │   │   └── constants.ts  # Константы
│   │   ├── hooks/            # React hooks
│   │   ├── store/            # Redux store
│   │   ├── types/            # TypeScript типы
│   │   ├── styles/           # Стили
│   │   ├── App.tsx           # Главный компонент
│   │   └── index.tsx         # Точка входа
│   ├── public/               # Статические файлы
│   ├── package.json          # Node.js зависимости
│   ├── tsconfig.json         # TypeScript конфигурация
│   ├── .eslintrc.js          # ESLint конфигурация
│   ├── .prettierrc           # Prettier конфигурация
│   └── Dockerfile            # Docker конфигурация
├── database/                  # База данных
│   ├── migrations/           # SQL миграции
│   │   └── 001_initial_schema.sql
│   └── queries/              # SQL запросы
│       └── performance_queries.sql
├── docker/                   # Docker конфигурации
│   └── docker-compose.yml    # Docker Compose
├── nginx/                    # Nginx конфигурации
│   ├── nginx.conf            # Основная конфигурация
│   └── conf.d/               # Конфигурации сайтов
│       └── default.conf
├── config/                   # Конфигурационные файлы
│   ├── prometheus.yml        # Prometheus
│   ├── alert_rules.yml       # Правила алертинга
│   └── grafana/              # Grafana дашборды
├── scripts/                  # Скрипты
│   ├── install-ubuntu.sh     # Установка на Ubuntu
│   ├── start-docker.sh       # Запуск Docker
│   └── deploy.sh             # Развертывание
├── docs/                     # Документация
│   ├── api.md                # API документация
│   ├── architecture.md       # Архитектура
│   └── deployment.md         # Развертывание
├── tests/                    # Интеграционные тесты
├── .env.example              # Пример переменных окружения
├── .gitignore                # Git ignore
├── .pre-commit-config.yaml   # Pre-commit конфигурация
├── docker-compose.yml        # Docker Compose
├── README.md                 # Основная документация
├── README_FULL.md            # Полная документация
├── README_UBUNTU24.md        # Ubuntu инструкции
├── QUICK_START.md            # Быстрый старт
├── DEPLOYMENT.md             # Развертывание
└── DEVELOPMENT.md            # Разработка
```

## Стандарты кода

### Python (Backend)

#### Форматирование
```bash
# Black для форматирования
black .

# isort для сортировки импортов
isort .

# flake8 для линтинга
flake8 .
```

#### Конфигурация Black
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

#### Конфигурация isort
```toml
# pyproject.toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_django = "django"
known_first_party = "app"
sections = ["FUTURE", "STDLIB", "DJANGO", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
```

#### Конфигурация flake8
```ini
# .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    .venv,
    venv,
    .eggs,
    *.egg,
    build,
    dist
```

### TypeScript/JavaScript (Frontend)

#### Форматирование
```bash
# Prettier для форматирования
npx prettier --write .

# ESLint для линтинга
npx eslint src --ext .ts,.tsx
```

#### Конфигурация Prettier
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false
}
```

#### Конфигурация ESLint
```json
{
  "extends": [
    "react-app",
    "react-app/jest",
    "prettier"
  ],
  "plugins": ["prettier"],
  "rules": {
    "prettier/prettier": "error",
    "no-unused-vars": "warn",
    "no-console": "warn"
  }
}
```

## Тестирование

### Backend тесты

#### Запуск тестов
```bash
cd backend
source venv/bin/activate

# Все тесты
pytest

# Конкретный тест
pytest tests/test_models.py

# С покрытием
pytest --cov=app --cov-report=html

# Параллельно
pytest -n auto
```

#### Структура тестов
```python
# tests/test_models.py
import pytest
from django.test import TestCase
from app.models import Ticket, User, Tenant

class TicketModelTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            slug="test",
            domain="test.com"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            tenant=self.tenant
        )
    
    def test_ticket_creation(self):
        ticket = Ticket.objects.create(
            title="Test Ticket",
            description="Test Description",
            created_by=self.user,
            tenant=self.tenant
        )
        self.assertEqual(ticket.title, "Test Ticket")
        self.assertEqual(ticket.status, "open")
```

### Frontend тесты

#### Запуск тестов
```bash
cd frontend

# Все тесты
npm test

# С покрытием
npm run test:coverage

# В watch режиме
npm run test:watch
```

#### Структура тестов
```typescript
// src/components/__tests__/TicketCard.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import { TicketCard } from '../TicketCard';

describe('TicketCard', () => {
  const mockTicket = {
    id: 1,
    title: 'Test Ticket',
    status: 'open',
    priority: 'high',
    created_at: '2024-01-01T00:00:00Z'
  };

  it('renders ticket information', () => {
    render(<TicketCard ticket={mockTicket} />);
    
    expect(screen.getByText('Test Ticket')).toBeInTheDocument();
    expect(screen.getByText('open')).toBeInTheDocument();
    expect(screen.getByText('high')).toBeInTheDocument();
  });
});
```

## API разработка

### Создание нового endpoint

#### 1. Создать модель
```python
# app/models/example.py
from django.db import models

class Example(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'examples'
```

#### 2. Создать сериализатор
```python
# app/api/serializers.py
class ExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Example
        fields = ['id', 'name', 'description', 'created_at']
```

#### 3. Создать ViewSet
```python
# app/api/views.py
class ExampleViewSet(viewsets.ModelViewSet):
    queryset = Example.objects.all()
    serializer_class = ExampleSerializer
    permission_classes = [IsAuthenticated]
```

#### 4. Добавить URL
```python
# app/api/urls.py
router.register(r'examples', ExampleViewSet, basename='example')
```

### WebSocket разработка

#### Создание нового consumer
```python
# app/api/consumers.py
class ExampleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'example_{self.room_name}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        # Обработка сообщения
        pass
```

## База данных

### Миграции

#### Создание миграции
```bash
# Создать миграцию
python manage.py makemigrations

# Применить миграцию
python manage.py migrate

# Откатить миграцию
python manage.py migrate app_name 0001
```

#### Создание данных
```python
# fixtures/initial_data.json
[
  {
    "model": "app.tenant",
    "pk": 1,
    "fields": {
      "name": "Default Tenant",
      "slug": "default",
      "domain": "localhost",
      "is_active": true
    }
  }
]
```

### Запросы к базе данных

#### Оптимизация запросов
```python
# Плохо - N+1 запросы
tickets = Ticket.objects.all()
for ticket in tickets:
    print(ticket.created_by.username)  # Дополнительный запрос для каждого тикета

# Хорошо - один запрос
tickets = Ticket.objects.select_related('created_by').all()
for ticket in tickets:
    print(ticket.created_by.username)  # Нет дополнительных запросов
```

#### Индексы
```python
# app/models/ticket.py
class Ticket(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    status = models.CharField(max_length=20, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['assigned_to', 'status']),
        ]
```

## Мониторинг и отладка

### Логирование

#### Настройка логов
```python
# app/utils/logging.py
import logging
import structlog

logger = structlog.get_logger(__name__)

def log_ticket_creation(ticket):
    logger.info(
        "ticket_created",
        ticket_id=ticket.id,
        user_id=ticket.created_by.id,
        tenant_id=ticket.tenant.id
    )
```

#### Использование логов
```python
# app/api/views.py
from app.utils.logging import log_ticket_creation

class TicketViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        log_ticket_creation(response.data)
        return response
```

### Профилирование

#### Django Debug Toolbar
```python
# settings.py
if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1']
```

#### Профилирование запросов
```python
# app/utils/profiling.py
from django.db import connection
from django.conf import settings

def log_queries():
    if settings.DEBUG:
        for query in connection.queries:
            print(f"Query: {query['sql']}")
            print(f"Time: {query['time']}")
```

## Развертывание

### Локальное развертывание

#### Docker Compose
```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Выполнение команд
docker-compose exec backend python manage.py migrate
```

#### Systemd сервисы
```bash
# Создать сервис
sudo nano /etc/systemd/system/workernet-backend.service

# Запустить сервис
sudo systemctl start workernet-backend
sudo systemctl enable workernet-backend
```

### CI/CD

#### GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          cd backend
          pytest
```

## Отладка

### Backend отладка

#### Django Debug Toolbar
```python
# settings.py
if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
```

#### Логирование SQL
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Frontend отладка

#### React Developer Tools
```bash
# Установить расширение для браузера
# Chrome: React Developer Tools
# Firefox: React Developer Tools
```

#### Redux DevTools
```typescript
// store/index.ts
import { createStore, applyMiddleware } from 'redux';
import { composeWithDevTools } from 'redux-devtools-extension';

const store = createStore(
  rootReducer,
  composeWithDevTools(applyMiddleware(thunk))
);
```

## Производительность

### Backend оптимизация

#### Кэширование
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

#### Оптимизация запросов
```python
# Использование select_related и prefetch_related
tickets = Ticket.objects.select_related('created_by', 'assigned_to').prefetch_related('tags').all()
```

### Frontend оптимизация

#### Lazy loading
```typescript
// Lazy loading компонентов
const LazyComponent = React.lazy(() => import('./LazyComponent'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LazyComponent />
    </Suspense>
  );
}
```

#### Мемоизация
```typescript
// Мемоизация компонентов
const MemoizedComponent = React.memo(({ data }) => {
  return <div>{data.name}</div>;
});

// Мемоизация вычислений
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data);
}, [data]);
```

## Безопасность

### Backend безопасность

#### Валидация данных
```python
# app/api/serializers.py
class TicketSerializer(serializers.ModelSerializer):
    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long")
        return value
```

#### Аутентификация
```python
# app/api/permissions.py
from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.created_by == request.user
```

### Frontend безопасность

#### Санитизация данных
```typescript
// Утилита для санитизации
import DOMPurify from 'dompurify';

const sanitizeHtml = (html: string): string => {
  return DOMPurify.sanitize(html);
};
```

#### Валидация форм
```typescript
// Валидация с помощью react-hook-form
const schema = yup.object({
  title: yup.string().min(5).required(),
  description: yup.string().required(),
});

const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: yupResolver(schema)
});
```

## Документация

### API документация

#### Swagger/OpenAPI
```python
# app/api/schemas.py
from drf_spectacular.utils import extend_schema, OpenApiParameter

@extend_schema(
    summary="Create ticket",
    description="Create a new support ticket",
    parameters=[
        OpenApiParameter(
            name="title",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Ticket title"
        )
    ]
)
class TicketViewSet(viewsets.ModelViewSet):
    pass
```

### Код документация

#### Docstrings
```python
def create_ticket(title: str, description: str, user: User) -> Ticket:
    """
    Create a new support ticket.
    
    Args:
        title: The title of the ticket
        description: The description of the ticket
        user: The user creating the ticket
        
    Returns:
        The created ticket instance
        
    Raises:
        ValidationError: If the ticket data is invalid
    """
    pass
```

---

## 🎯 Готово!

Теперь вы готовы к разработке WorkerNet Portal!

**Следующие шаги:**
1. Настроить среду разработки
2. Изучить структуру проекта
3. Создать первую фичу
4. Написать тесты
5. Создать Pull Request

**Нужна помощь?** Обратитесь к документации или создайте issue в репозитории!
