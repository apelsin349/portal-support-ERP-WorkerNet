# 📚 API документация WorkerNet Portal

## Обзор API

WorkerNet Portal предоставляет RESTful API для управления системой технической поддержки. API построен на Django REST Framework и поддерживает версионирование, аутентификацию JWT и WebSocket соединения.

### Базовый URL
```
http://localhost:8000/api/v1/
```

### Аутентификация
API использует JWT (JSON Web Tokens) для аутентификации. Получите токен через endpoint `/api/auth/login/` и используйте его в заголовке `Authorization: Bearer <token>`.

## Аутентификация

### Вход в систему
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Ответ:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Обновление токена
```http
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Выход из системы
```http
POST /api/auth/logout/
Authorization: Bearer <access_token>
```

## Тикеты

### Получить список тикетов
```http
GET /api/v1/tickets/
Authorization: Bearer <access_token>
```

**Параметры запроса:**
- `status` - фильтр по статусу (open, in_progress, pending, resolved, closed, cancelled)
- `priority` - фильтр по приоритету (low, medium, high, urgent, critical)
- `category` - фильтр по категории (technical, billing, general, bug_report, feature_request, other)
- `assigned_to` - фильтр по назначенному пользователю
- `search` - поиск по названию и описанию
- `ordering` - сортировка (created_at, updated_at, priority, status)
- `page` - номер страницы
- `page_size` - размер страницы

**Ответ:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/tickets/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "ticket_id": "TK-12345678",
      "title": "Проблема с входом в систему",
      "description": "Не могу войти в систему с моими учетными данными",
      "priority": "high",
      "status": "open",
      "category": "technical",
      "created_by": {
        "id": 1,
        "username": "user1",
        "email": "user1@example.com",
        "first_name": "Иван",
        "last_name": "Иванов"
      },
      "assigned_to": {
        "id": 2,
        "username": "support1",
        "email": "support1@example.com",
        "first_name": "Петр",
        "last_name": "Петров"
      },
      "tenant": {
        "id": 1,
        "name": "Default Tenant",
        "slug": "default",
        "domain": "localhost"
      },
      "sla_hours": 24,
      "due_date": "2024-01-15T10:00:00Z",
      "resolved_at": null,
      "created_at": "2024-01-14T10:00:00Z",
      "updated_at": "2024-01-14T10:00:00Z",
      "custom_fields": {},
      "tags": [
        {
          "id": 1,
          "name": "urgent",
          "color": "#ff0000",
          "description": "Срочные тикеты"
        }
      ],
      "comments": [],
      "attachments": []
    }
  ]
}
```

### Создать тикет
```http
POST /api/v1/tickets/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Новый тикет",
  "description": "Описание проблемы",
  "priority": "medium",
  "category": "technical",
  "assigned_to_id": 2,
  "tag_ids": [1, 2],
  "custom_fields": {
    "department": "IT",
    "urgency": "high"
  }
}
```

### Получить тикет
```http
GET /api/v1/tickets/{id}/
Authorization: Bearer <access_token>
```

### Обновить тикет
```http
PUT /api/v1/tickets/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Обновленное название",
  "description": "Обновленное описание",
  "priority": "high",
  "status": "in_progress"
}
```

### Удалить тикет
```http
DELETE /api/v1/tickets/{id}/
Authorization: Bearer <access_token>
```

### Назначить тикет
```http
POST /api/v1/tickets/{id}/assign/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "user_id": 2
}
```

### Закрыть тикет
```http
POST /api/v1/tickets/{id}/close/
Authorization: Bearer <access_token>
```

### Переоткрыть тикет
```http
POST /api/v1/tickets/{id}/reopen/
Authorization: Bearer <access_token>
```

## Комментарии к тикетам

### Получить комментарии тикета
```http
GET /api/v1/tickets/{id}/comments/
Authorization: Bearer <access_token>
```

### Добавить комментарий
```http
POST /api/v1/tickets/{id}/add_comment/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "Текст комментария",
  "is_internal": false
}
```

### Обновить комментарий
```http
PUT /api/v1/tickets/{id}/comments/{comment_id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "Обновленный текст комментария"
}
```

### Удалить комментарий
```http
DELETE /api/v1/tickets/{id}/comments/{comment_id}/
Authorization: Bearer <access_token>
```

## Вложения к тикетам

### Получить вложения тикета
```http
GET /api/v1/tickets/{id}/attachments/
Authorization: Bearer <access_token>
```

### Добавить вложение
```http
POST /api/v1/tickets/{id}/add_attachment/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <file>
```

### Удалить вложение
```http
DELETE /api/v1/tickets/{id}/attachments/{attachment_id}/
Authorization: Bearer <access_token>
```

## База знаний

### Получить статьи
```http
GET /api/v1/knowledge/articles/
Authorization: Bearer <access_token>
```

**Параметры запроса:**
- `status` - фильтр по статусу (draft, published, archived)
- `category` - фильтр по категории
- `author` - фильтр по автору
- `search` - поиск по названию и содержанию
- `ordering` - сортировка (created_at, updated_at, view_count, helpful_count)

**Ответ:**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/v1/knowledge/articles/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Как войти в систему",
      "slug": "kak-voiti-v-sistemu",
      "content": "Подробное описание процесса входа в систему...",
      "excerpt": "Краткое описание статьи",
      "category": {
        "id": 1,
        "name": "Аутентификация",
        "description": "Статьи по аутентификации"
      },
      "author": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "first_name": "Администратор",
        "last_name": "Системы"
      },
      "status": "published",
      "meta_title": "Вход в систему - WorkerNet",
      "meta_description": "Инструкция по входу в систему WorkerNet",
      "keywords": "вход, аутентификация, логин",
      "view_count": 150,
      "helpful_count": 25,
      "not_helpful_count": 2,
      "published_at": "2024-01-14T10:00:00Z",
      "created_at": "2024-01-14T10:00:00Z",
      "updated_at": "2024-01-14T10:00:00Z",
      "custom_fields": {},
      "tags": [
        {
          "id": 1,
          "name": "аутентификация",
          "color": "#1976d2",
          "description": "Статьи по аутентификации"
        }
      ]
    }
  ]
}
```

### Создать статью
```http
POST /api/v1/knowledge/articles/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Новая статья",
  "content": "Содержание статьи",
  "excerpt": "Краткое описание",
  "category_id": 1,
  "status": "draft",
  "meta_title": "SEO заголовок",
  "meta_description": "SEO описание",
  "keywords": "ключевые, слова",
  "tag_ids": [1, 2],
  "custom_fields": {
    "difficulty": "beginner",
    "estimated_time": "5 minutes"
  }
}
```

### Получить статью
```http
GET /api/v1/knowledge/articles/{id}/
Authorization: Bearer <access_token>
```

### Обновить статью
```http
PUT /api/v1/knowledge/articles/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Обновленное название",
  "content": "Обновленное содержание",
  "status": "published"
}
```

### Удалить статью
```http
DELETE /api/v1/knowledge/articles/{id}/
Authorization: Bearer <access_token>
```

### Оценить статью
```http
POST /api/v1/knowledge/articles/{id}/rate/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "rating": 5,
  "comment": "Отличная статья!"
}
```

### Отметить просмотр статьи
```http
POST /api/v1/knowledge/articles/{id}/view/
Authorization: Bearer <access_token>
```

## Категории базы знаний

### Получить категории
```http
GET /api/v1/knowledge/categories/
Authorization: Bearer <access_token>
```

**Ответ:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Аутентификация",
      "description": "Статьи по аутентификации и безопасности",
      "parent": null,
      "children": [
        {
          "id": 2,
          "name": "Вход в систему",
          "description": "Инструкции по входу",
          "parent": 1,
          "children": [],
          "order": 0,
          "is_active": true,
          "created_at": "2024-01-14T10:00:00Z",
          "updated_at": "2024-01-14T10:00:00Z",
          "articles_count": 5
        }
      ],
      "order": 0,
      "is_active": true,
      "created_at": "2024-01-14T10:00:00Z",
      "updated_at": "2024-01-14T10:00:00Z",
      "articles_count": 15
    }
  ]
}
```

### Создать категорию
```http
POST /api/v1/knowledge/categories/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Новая категория",
  "description": "Описание категории",
  "parent": 1,
  "order": 0
}
```

## Пользователи

### Получить пользователей
```http
GET /api/v1/users/
Authorization: Bearer <access_token>
```

**Параметры запроса:**
- `is_active` - фильтр по активности
- `department` - фильтр по отделу
- `position` - фильтр по должности
- `search` - поиск по имени и email
- `ordering` - сортировка (username, first_name, last_name, date_joined)

**Ответ:**
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "user1",
      "email": "user1@example.com",
      "first_name": "Иван",
      "last_name": "Иванов",
      "avatar": "http://localhost:8000/media/users/avatars/avatar1.jpg",
      "phone": "+7 (999) 123-45-67",
      "department": "IT",
      "position": "Разработчик",
      "is_active": true,
      "is_verified": true,
      "date_joined": "2024-01-14T10:00:00Z",
      "last_login": "2024-01-14T15:30:00Z"
    }
  ]
}
```

### Получить текущего пользователя
```http
GET /api/v1/users/me/
Authorization: Bearer <access_token>
```

### Обновить профиль
```http
PUT /api/v1/users/update_me/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "Иван",
  "last_name": "Иванов",
  "phone": "+7 (999) 123-45-67",
  "department": "IT",
  "position": "Разработчик"
}
```

## Тенанты

### Получить тенантов
```http
GET /api/v1/tenants/
Authorization: Bearer <access_token>
```

**Ответ:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Default Tenant",
      "slug": "default",
      "domain": "localhost",
      "is_active": true,
      "logo": "http://localhost:8000/media/tenants/logos/logo.png",
      "primary_color": "#1976d2",
      "secondary_color": "#dc004e",
      "features": {
        "tickets": true,
        "knowledge_base": true,
        "chat": true,
        "analytics": true
      },
      "created_at": "2024-01-14T10:00:00Z",
      "updated_at": "2024-01-14T10:00:00Z"
    }
  ]
}
```

### Получить конфигурацию тенанта
```http
GET /api/v1/tenants/{id}/configuration/
Authorization: Bearer <access_token>
```

**Ответ:**
```json
{
  "timezone": "Europe/Moscow",
  "language": "ru",
  "date_format": "%d.%m.%Y",
  "time_format": "24",
  "ticket_settings": {
    "auto_assign_tickets": true,
    "priority_levels": ["low", "medium", "high", "urgent", "critical"],
    "categories": ["technical", "billing", "general", "bug_report", "feature_request", "other"]
  },
  "sla_settings": {
    "default_sla_hours": 24,
    "escalation_rules": {
      "high": 4,
      "urgent": 2,
      "critical": 1
    }
  },
  "notification_settings": {
    "email_notifications": true,
    "sms_notifications": false,
    "push_notifications": true
  },
  "security_settings": {
    "password_policy": {
      "min_length": 8,
      "require_uppercase": true,
      "require_lowercase": true,
      "require_numbers": true,
      "require_symbols": false
    },
    "session_timeout": 3600,
    "two_factor_required": false
  },
  "integration_settings": {
    "ldap_enabled": false,
    "ldap_config": {},
    "sso_enabled": false,
    "sso_config": {}
  },
  "custom_fields": {
    "department": "string",
    "urgency": "choice",
    "estimated_time": "number"
  }
}
```

## Теги

### Получить теги
```http
GET /api/v1/tags/
Authorization: Bearer <access_token>
```

**Ответ:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "urgent",
      "color": "#ff0000",
      "description": "Срочные тикеты",
      "created_at": "2024-01-14T10:00:00Z"
    }
  ]
}
```

### Создать тег
```http
POST /api/v1/tags/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "bug",
  "color": "#ff5722",
  "description": "Ошибки в системе"
}
```

## WebSocket API

### Подключение к WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/tickets/123/');

ws.onopen = function(event) {
    console.log('WebSocket connected');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

ws.onclose = function(event) {
    console.log('WebSocket disconnected');
};

ws.onerror = function(error) {
    console.error('WebSocket error:', error);
};
```

### Отправка сообщений
```javascript
// Добавить комментарий
ws.send(JSON.stringify({
    type: 'comment',
    comment: {
        content: 'Новый комментарий',
        is_internal: false
    }
}));

// Обновить статус
ws.send(JSON.stringify({
    type: 'status_update',
    status: 'in_progress'
}));

// Назначить тикет
ws.send(JSON.stringify({
    type: 'assignment',
    user_id: 2
}));
```

### Получение уведомлений
```javascript
const notificationWs = new WebSocket('ws://localhost:8000/ws/notifications/');

notificationWs.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'notification_created') {
        console.log('New notification:', data.notification);
    }
};
```

## Обработка ошибок

### Коды ошибок
- `400` - Bad Request (неверный запрос)
- `401` - Unauthorized (не авторизован)
- `403` - Forbidden (доступ запрещен)
- `404` - Not Found (не найдено)
- `405` - Method Not Allowed (метод не разрешен)
- `429` - Too Many Requests (слишком много запросов)
- `500` - Internal Server Error (внутренняя ошибка сервера)

### Формат ошибки
```json
{
  "error": "Validation failed",
  "details": {
    "title": ["This field is required."],
    "priority": ["Invalid choice."]
  },
  "code": "VALIDATION_ERROR"
}
```

## Пагинация

### Параметры пагинации
- `page` - номер страницы (начиная с 1)
- `page_size` - размер страницы (по умолчанию 20, максимум 100)

### Формат ответа с пагинацией
```json
{
  "count": 1000,
  "next": "http://localhost:8000/api/v1/tickets/?page=3",
  "previous": "http://localhost:8000/api/v1/tickets/?page=1",
  "results": [...]
}
```

## Фильтрация и поиск

### Параметры фильтрации
- `field__exact` - точное совпадение
- `field__icontains` - содержит (без учета регистра)
- `field__in` - входит в список
- `field__gt` - больше
- `field__gte` - больше или равно
- `field__lt` - меньше
- `field__lte` - меньше или равно
- `field__isnull` - пустое значение
- `field__date` - фильтр по дате
- `field__year` - фильтр по году
- `field__month` - фильтр по месяцу
- `field__day` - фильтр по дню

### Примеры фильтрации
```http
# Тикеты с высоким приоритетом
GET /api/v1/tickets/?priority=high

# Тикеты, созданные сегодня
GET /api/v1/tickets/?created_at__date=2024-01-14

# Тикеты, содержащие "ошибка" в названии
GET /api/v1/tickets/?title__icontains=ошибка

# Тикеты, назначенные пользователю с ID 2
GET /api/v1/tickets/?assigned_to=2

# Тикеты с тегами 1 и 2
GET /api/v1/tickets/?tags__in=1,2
```

## Сортировка

### Параметр ordering
```http
# Сортировка по дате создания (по убыванию)
GET /api/v1/tickets/?ordering=-created_at

# Сортировка по приоритету (по возрастанию), затем по дате
GET /api/v1/tickets/?ordering=priority,-created_at

# Сортировка по названию (без учета регистра)
GET /api/v1/tickets/?ordering=title
```

## Лимиты и квоты

### Лимиты запросов
- **Аутентифицированные пользователи**: 1000 запросов в час
- **Неаутентифицированные пользователи**: 100 запросов в час
- **API ключи**: 10000 запросов в час

### Лимиты размера
- **Максимальный размер запроса**: 10 MB
- **Максимальный размер файла**: 10 MB
- **Максимальная длина строки**: 1000 символов

## Версионирование API

### Поддержка версий
- **v1** - текущая версия (по умолчанию)
- **v2** - следующая версия (в разработке)

### Использование версий
```http
# Явное указание версии
GET /api/v1/tickets/

# Через заголовок
GET /api/tickets/
X-API-Version: v1

# Через параметр запроса
GET /api/tickets/?version=v1
```

## SDK и клиенты

### JavaScript/TypeScript
```bash
npm install workernet-api-client
```

```typescript
import { WorkerNetAPI } from 'workernet-api-client';

const api = new WorkerNetAPI({
  baseURL: 'http://localhost:8000/api/v1',
  token: 'your-jwt-token'
});

// Получить тикеты
const tickets = await api.tickets.list();

// Создать тикет
const ticket = await api.tickets.create({
  title: 'Новый тикет',
  description: 'Описание проблемы',
  priority: 'high'
});
```

### Python
```bash
pip install workernet-api-client
```

```python
from workernet_api import WorkerNetAPI

api = WorkerNetAPI(
    base_url='http://localhost:8000/api/v1',
    token='your-jwt-token'
)

# Получить тикеты
tickets = api.tickets.list()

# Создать тикет
ticket = api.tickets.create({
    'title': 'Новый тикет',
    'description': 'Описание проблемы',
    'priority': 'high'
})
```

## Дополнительные ресурсы

### Swagger UI
- **URL**: http://localhost:8000/api/docs/
- **Описание**: Интерактивная документация API

### ReDoc
- **URL**: http://localhost:8000/api/redoc/
- **Описание**: Альтернативная документация API

### OpenAPI Schema
- **URL**: http://localhost:8000/api/schema/
- **Описание**: JSON схема API

### Postman Collection
- **URL**: https://www.postman.com/workernet/collection/12345678
- **Описание**: Готовая коллекция для Postman

---

## 🎯 Готово!

Теперь вы знаете, как использовать API WorkerNet Portal!

**Следующие шаги:**
1. Получить токен аутентификации
2. Изучить доступные endpoints
3. Интегрировать API в ваше приложение
4. Использовать WebSocket для real-time обновлений

**Нужна помощь?** Обратитесь к Swagger UI или создайте issue в репозитории!
