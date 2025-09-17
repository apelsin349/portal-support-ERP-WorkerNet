# 🏗️ Архитектура WorkerNet Portal

## Обзор системы

WorkerNet Portal - это современная система технической поддержки, построенная на микросервисной архитектуре с использованием Django REST Framework, React и Docker. Система поддерживает мультитенантность, real-time обновления и масштабируемость.

## Высокоуровневая архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  Web App (React)  │  Mobile App  │  Admin Panel  │  API Clients │
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                      Load Balancer (Nginx)                     │
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React)  │  Backend API (Django)  │  WebSocket (Channels) │
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                      Service Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  Celery Workers  │  Celery Beat  │  Background Tasks  │  Notifications │
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                 │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL  │  Redis  │  Elasticsearch  │  File Storage (S3)  │
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                    Monitoring Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  Prometheus  │  Grafana  │  ELK Stack  │  AlertManager  │  Logs │
└─────────────────────────────────────────────────────────────────┘
```

## Компоненты системы

### 1. Frontend (React)

#### Технологии
- **React 18** - UI библиотека
- **TypeScript** - типизация
- **Material-UI** - компоненты UI
- **Redux Toolkit** - управление состоянием
- **React Query** - кэширование данных
- **React Router** - маршрутизация
- **WebSocket** - real-time обновления

#### Архитектура
```
src/
├── components/          # Переиспользуемые компоненты
│   ├── common/         # Общие компоненты
│   ├── forms/          # Формы
│   ├── layout/         # Макет
│   └── ui/             # UI компоненты
├── pages/              # Страницы приложения
│   ├── auth/           # Аутентификация
│   ├── dashboard/      # Дашборд
│   ├── tickets/        # Тикеты
│   ├── knowledge/      # База знаний
│   └── settings/       # Настройки
├── services/           # API сервисы
│   ├── api.ts         # API клиент
│   ├── auth.ts        # Аутентификация
│   ├── tickets.ts     # Тикеты
│   └── knowledge.ts   # База знаний
├── store/              # Redux store
│   ├── slices/        # Redux slices
│   ├── middleware/    # Middleware
│   └── index.ts       # Store конфигурация
├── hooks/              # Custom hooks
├── utils/              # Утилиты
│   ├── rum-monitor.js # Real User Monitoring
│   ├── ab-testing.js  # A/B тестирование
│   └── helpers.ts     # Вспомогательные функции
└── types/              # TypeScript типы
```

#### Ключевые особенности
- **Компонентная архитектура** - модульность и переиспользование
- **Типизация** - безопасность типов с TypeScript
- **State management** - централизованное управление состоянием
- **Real-time updates** - WebSocket для live обновлений
- **Responsive design** - адаптивный дизайн
- **PWA support** - поддержка Progressive Web App

### 2. Backend API (Django)

#### Технологии
- **Django 4.2** - веб-фреймворк
- **Django REST Framework** - API
- **Django Channels** - WebSocket
- **Celery** - фоновые задачи
- **PostgreSQL** - основная БД
- **Redis** - кэширование и очереди
- **JWT** - аутентификация

#### Архитектура
```
backend/
├── app/                    # Основное приложение
│   ├── core/              # Основные модули
│   │   ├── feature_flags.py      # A/B тестирование
│   │   ├── ab_testing.py         # Статистический анализ
│   │   ├── incident_management.py # Управление инцидентами
│   │   ├── performance_monitoring.py # Мониторинг производительности
│   │   └── api_versioning.py     # Управление версиями API
│   ├── api/               # API endpoints
│   │   ├── views.py       # API views
│   │   ├── serializers.py # API serializers
│   │   ├── urls.py        # API URLs
│   │   ├── routing.py     # WebSocket routing
│   │   └── consumers.py   # WebSocket consumers
│   ├── models/            # Модели данных
│   │   ├── tenant.py      # Мультитенантность
│   │   ├── ticket.py      # Тикеты поддержки
│   │   └── knowledge.py   # База знаний
│   ├── services/          # Бизнес-логика
│   ├── utils/             # Утилиты
│   └── tests/             # Тесты
├── config/                # Конфигурация Django
│   ├── settings.py        # Настройки
│   ├── urls.py           # URL конфигурация
│   ├── wsgi.py           # WSGI конфигурация
│   └── asgi.py           # ASGI конфигурация
└── migrations/            # Миграции БД
```

#### Ключевые особенности
- **RESTful API** - стандартизированные endpoints
- **Мультитенантность** - изоляция данных по клиентам
- **WebSocket** - real-time обновления
- **Фоновые задачи** - асинхронная обработка
- **Кэширование** - оптимизация производительности
- **Версионирование API** - поддержка множественных версий

### 3. База данных (PostgreSQL)

#### Схема данных
```sql
-- Основные таблицы
tenants                    # Тенанты (клиенты)
users                      # Пользователи
tickets                    # Тикеты поддержки
ticket_comments           # Комментарии к тикетам
ticket_attachments        # Вложения к тикетам
knowledge_articles        # Статьи базы знаний
knowledge_categories      # Категории базы знаний
knowledge_article_ratings # Оценки статей
tags                      # Теги
slas                      # SLA правила
ticket_slas              # Отслеживание SLA
incidents                # Инциденты
ab_tests                 # A/B тесты
performance_metrics      # Метрики производительности
audit_logs               # Аудит действий
```

#### Ключевые особенности
- **Нормализация** - оптимизированная структура данных
- **Индексы** - быстрый поиск и сортировка
- **Ограничения** - целостность данных
- **Триггеры** - автоматические действия
- **Партиционирование** - масштабируемость
- **Репликация** - отказоустойчивость

### 4. Кэширование (Redis)

#### Использование
- **Сессии** - хранение пользовательских сессий
- **Кэш** - кэширование часто используемых данных
- **Очереди** - Celery задачи
- **WebSocket** - Channels группы
- **Rate limiting** - ограничение запросов
- **Временные данные** - токены, коды подтверждения

#### Конфигурация
```python
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

### 5. Фоновые задачи (Celery)

#### Типы задач
- **Email уведомления** - отправка писем
- **SMS уведомления** - отправка SMS
- **Push уведомления** - мобильные уведомления
- **Обработка файлов** - загрузка и обработка
- **Аналитика** - генерация отчетов
- **Очистка данных** - удаление старых данных
- **Синхронизация** - интеграция с внешними системами

#### Конфигурация
```python
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/2'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/3'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
```

### 6. WebSocket (Channels)

#### Использование
- **Real-time обновления** - live обновления тикетов
- **Уведомления** - мгновенные уведомления
- **Чат поддержки** - live чат
- **Мониторинг** - real-time метрики
- **Коллаборация** - совместная работа

#### Конфигурация
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```

## Паттерны архитектуры

### 1. MVC (Model-View-Controller)

#### Model
```python
# app/models/ticket.py
class Ticket(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title
```

#### View
```python
# app/api/views.py
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Бизнес-логика создания тикета
        pass
```

#### Controller
```python
# app/api/serializers.py
class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'title', 'description', 'status', 'created_by']
    
    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters")
        return value
```

### 2. Repository Pattern

```python
# app/repositories/ticket_repository.py
class TicketRepository:
    def __init__(self):
        self.model = Ticket
    
    def get_by_id(self, ticket_id):
        return self.model.objects.get(id=ticket_id)
    
    def get_by_status(self, status):
        return self.model.objects.filter(status=status)
    
    def create(self, data):
        return self.model.objects.create(**data)
    
    def update(self, ticket_id, data):
        ticket = self.get_by_id(ticket_id)
        for key, value in data.items():
            setattr(ticket, key, value)
        ticket.save()
        return ticket
```

### 3. Service Layer

```python
# app/services/ticket_service.py
class TicketService:
    def __init__(self):
        self.repository = TicketRepository()
        self.notification_service = NotificationService()
    
    def create_ticket(self, data, user):
        # Создать тикет
        ticket = self.repository.create(data)
        
        # Отправить уведомления
        self.notification_service.notify_ticket_created(ticket)
        
        # Обновить метрики
        self.update_metrics(ticket)
        
        return ticket
    
    def assign_ticket(self, ticket_id, user_id):
        ticket = self.repository.get_by_id(ticket_id)
        ticket.assigned_to_id = user_id
        ticket.save()
        
        # Уведомить о назначении
        self.notification_service.notify_ticket_assigned(ticket)
        
        return ticket
```

### 4. Observer Pattern

```python
# app/observers/ticket_observer.py
class TicketObserver:
    def __init__(self):
        self.observers = []
    
    def attach(self, observer):
        self.observers.append(observer)
    
    def detach(self, observer):
        self.observers.remove(observer)
    
    def notify(self, event, data):
        for observer in self.observers:
            observer.update(event, data)

# app/observers/notification_observer.py
class NotificationObserver:
    def update(self, event, data):
        if event == 'ticket_created':
            self.send_ticket_created_notification(data)
        elif event == 'ticket_updated':
            self.send_ticket_updated_notification(data)
```

### 5. Factory Pattern

```python
# app/factories/ticket_factory.py
class TicketFactory:
    @staticmethod
    def create_ticket(ticket_type, data):
        if ticket_type == 'technical':
            return TechnicalTicket(**data)
        elif ticket_type == 'billing':
            return BillingTicket(**data)
        elif ticket_type == 'general':
            return GeneralTicket(**data)
        else:
            raise ValueError(f"Unknown ticket type: {ticket_type}")

# app/factories/notification_factory.py
class NotificationFactory:
    @staticmethod
    def create_notification(notification_type, data):
        if notification_type == 'email':
            return EmailNotification(**data)
        elif notification_type == 'sms':
            return SMSNotification(**data)
        elif notification_type == 'push':
            return PushNotification(**data)
        else:
            raise ValueError(f"Unknown notification type: {notification_type}")
```

## Масштабирование

### 1. Горизонтальное масштабирование

#### Load Balancer
```nginx
# nginx.conf
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

upstream frontend {
    server frontend1:3000;
    server frontend2:3000;
    server frontend3:3000;
}
```

#### Database Sharding
```python
# app/database/sharding.py
class DatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'app':
            return 'shard1' if model.id % 2 == 0 else 'shard2'
        return None
    
    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'app':
            return 'shard1' if model.id % 2 == 0 else 'shard2'
        return None
```

### 2. Вертикальное масштабирование

#### Увеличение ресурсов
```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

#### Оптимизация запросов
```python
# app/optimizations/query_optimization.py
class QueryOptimizer:
    @staticmethod
    def optimize_ticket_queries():
        return Ticket.objects.select_related(
            'created_by', 'assigned_to', 'tenant'
        ).prefetch_related(
            'tags', 'comments', 'attachments'
        )
```

## Безопасность

### 1. Аутентификация и авторизация

#### JWT токены
```python
# app/auth/jwt.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

#### RBAC (Role-Based Access Control)
```python
# app/permissions/rbac.py
class RoleBasedPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        required_role = getattr(view, 'required_role', None)
        if not required_role:
            return True
        
        return request.user.role == required_role
```

### 2. Защита данных

#### Шифрование
```python
# app/security/encryption.py
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self, key):
        self.cipher = Fernet(key)
    
    def encrypt(self, data):
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, encrypted_data):
        return self.cipher.decrypt(encrypted_data).decode()
```

#### Валидация данных
```python
# app/validators/data_validators.py
class DataValidator:
    @staticmethod
    def validate_ticket_data(data):
        if not data.get('title'):
            raise ValidationError("Title is required")
        
        if len(data.get('title', '')) < 5:
            raise ValidationError("Title must be at least 5 characters")
        
        return True
```

### 3. Защита от атак

#### Rate Limiting
```python
# app/middleware/rate_limiting.py
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h', method='POST')
def create_ticket(request):
    pass
```

#### CSRF Protection
```python
# settings.py
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
```

## Мониторинг и логирование

### 1. Метрики

#### Prometheus метрики
```python
# app/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
active_users = Gauge('active_users', 'Number of active users')
```

#### Custom метрики
```python
# app/monitoring/custom_metrics.py
class CustomMetrics:
    @staticmethod
    def track_ticket_creation():
        ticket_creation_counter.inc()
    
    @staticmethod
    def track_response_time(duration):
        response_time_histogram.observe(duration)
```

### 2. Логирование

#### Структурированные логи
```python
# app/logging/structured_logging.py
import structlog

logger = structlog.get_logger(__name__)

def log_ticket_creation(ticket, user):
    logger.info(
        "ticket_created",
        ticket_id=ticket.id,
        user_id=user.id,
        tenant_id=ticket.tenant.id,
        priority=ticket.priority
    )
```

#### ELK Stack
```yaml
# docker-compose.yml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
  
  logstash:
    image: docker.elastic.co/logstash/logstash:8.8.0
    volumes:
      - ./config/logstash/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
  
  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

## Развертывание

### 1. Docker контейнеризация

#### Multi-stage builds
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim as runtime
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: worker_net
      POSTGRES_USER: workernet
      POSTGRES_PASSWORD: workernet123
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass redis123
    volumes:
      - redis_data:/data
  
  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://workernet:workernet123@db:5432/worker_net
      REDIS_URL: redis://:redis123@redis:6379/0
    depends_on:
      - db
      - redis
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

### 2. CI/CD

#### GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

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
          pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v1
        with:
          file: ./backend/coverage.xml
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker images
        run: |
          docker-compose build
      
      - name: Push to registry
        run: |
          docker tag workernet-backend:latest ${{ secrets.REGISTRY_URL }}/workernet-backend:latest
          docker push ${{ secrets.REGISTRY_URL }}/workernet-backend:latest
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          # Deploy to production server
          ssh ${{ secrets.PROD_SERVER }} 'docker-compose pull && docker-compose up -d'
```

### 3. Kubernetes

#### Deployment
```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: workernet-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: workernet-backend
  template:
    metadata:
      labels:
        app: workernet-backend
    spec:
      containers:
      - name: backend
        image: workernet-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: workernet-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: workernet-secrets
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

#### Service
```yaml
# k8s/backend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: workernet-backend-service
spec:
  selector:
    app: workernet-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Производительность

### 1. Оптимизация базы данных

#### Индексы
```sql
-- Создание индексов
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);
CREATE INDEX idx_tickets_assigned_to ON tickets(assigned_to_id);

-- Составные индексы
CREATE INDEX idx_tickets_status_priority ON tickets(status, priority);
CREATE INDEX idx_tickets_tenant_status ON tickets(tenant_id, status);
```

#### Партиционирование
```sql
-- Партиционирование по дате
CREATE TABLE tickets_2024_01 PARTITION OF tickets
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE tickets_2024_02 PARTITION OF tickets
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

### 2. Кэширование

#### Redis кэширование
```python
# app/caching/redis_cache.py
from django.core.cache import cache

class RedisCache:
    @staticmethod
    def get_or_set(key, func, timeout=300):
        result = cache.get(key)
        if result is None:
            result = func()
            cache.set(key, result, timeout)
        return result
    
    @staticmethod
    def invalidate_pattern(pattern):
        keys = cache.keys(pattern)
        if keys:
            cache.delete_many(keys)
```

#### CDN
```python
# settings.py
STATIC_URL = 'https://cdn.workernet.com/static/'
MEDIA_URL = 'https://cdn.workernet.com/media/'
```

### 3. Асинхронная обработка

#### Celery задачи
```python
# app/tasks/email_tasks.py
from celery import shared_task

@shared_task
def send_ticket_notification(ticket_id, user_id):
    ticket = Ticket.objects.get(id=ticket_id)
    user = User.objects.get(id=user_id)
    
    # Отправить email
    send_email.delay(
        to=user.email,
        subject=f"Новый тикет: {ticket.title}",
        body=f"Создан новый тикет: {ticket.description}"
    )
```

#### WebSocket
```python
# app/consumers/ticket_consumer.py
class TicketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ticket_id = self.scope['url_route']['kwargs']['ticket_id']
        self.room_group_name = f'ticket_{self.ticket_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
```

## Отказоустойчивость

### 1. Health Checks

#### Backend health check
```python
# app/views/health.py
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache

def health_check(request):
    health_data = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'services': {}
    }
    
    # Проверка базы данных
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_data['services']['database'] = {'status': 'healthy'}
    except Exception as e:
        health_data['services']['database'] = {'status': 'unhealthy', 'error': str(e)}
        health_data['status'] = 'unhealthy'
    
    # Проверка кэша
    try:
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
        health_data['services']['cache'] = {'status': 'healthy'}
    except Exception as e:
        health_data['services']['cache'] = {'status': 'unhealthy', 'error': str(e)}
        health_data['status'] = 'unhealthy'
    
    return JsonResponse(health_data)
```

### 2. Circuit Breaker

```python
# app/circuit_breaker/circuit_breaker.py
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e
    
    def on_success(self):
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
```

### 3. Graceful Shutdown

```python
# app/signals/graceful_shutdown.py
import signal
import sys

class GracefulShutdown:
    def __init__(self):
        self.shutdown = False
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        print(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown = True
        
        # Завершить активные соединения
        self.close_connections()
        
        # Завершить фоновые задачи
        self.stop_background_tasks()
        
        sys.exit(0)
    
    def close_connections(self):
        # Закрыть соединения с базой данных
        from django.db import connections
        connections.close_all()
        
        # Закрыть Redis соединения
        from django.core.cache import cache
        cache.close()
    
    def stop_background_tasks(self):
        # Остановить Celery workers
        from celery import current_app
        current_app.control.shutdown()
```

---

## 🎯 Готово!

Теперь вы понимаете архитектуру WorkerNet Portal!

**Ключевые принципы:**
1. **Модульность** - разделение на независимые компоненты
2. **Масштабируемость** - горизонтальное и вертикальное масштабирование
3. **Отказоустойчивость** - graceful degradation и recovery
4. **Безопасность** - многоуровневая защита
5. **Производительность** - оптимизация на всех уровнях
6. **Мониторинг** - полная видимость системы

**Следующие шаги:**
1. Изучить конкретные компоненты
2. Настроить мониторинг
3. Оптимизировать производительность
4. Настроить безопасность
5. Планировать масштабирование

**Нужна помощь?** Обратитесь к документации или создайте issue в репозитории!
