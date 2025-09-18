# 🔧 Исправление проблем с импортами Django

## Проблема: ModuleNotFoundError при выполнении миграций

### Симптомы
```
ModuleNotFoundError: No module named 'rest_framework_simplejwt.urls'
```

### Причины
1. **Неправильный импорт JWT URLs** - в новых версиях SimpleJWT изменилась структура
2. **Отсутствующие импорты моделей** - циклические импорты между моделями
3. **Неправильная конфигурация URL patterns**

## 🚀 Решения

### 1. Быстрое решение (рекомендуется)

Запустите скрипт исправления:

```bash
# Сделать скрипт исполняемым
chmod +x scripts/fix-django-imports.sh

# Запустить исправление
./scripts/fix-django-imports.sh
```

### 2. Ручное исправление

#### Шаг 1: Исправление JWT URLs

В файле `backend/app/api/urls.py`:

**Было (неправильно):**
```python
path('auth/', include('rest_framework_simplejwt.urls')),
```

**Стало (правильно):**
```python
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# В urlpatterns:
path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
```

#### Шаг 2: Исправление импортов моделей

В файле `backend/app/models/knowledge.py`:
```python
# Добавить импорт
from .tenant import Tenant
```

В файле `backend/app/models/ticket.py`:
```python
# Добавить импорт
from .tenant import Tenant
```

#### Шаг 3: Проверка миграций

```bash
cd backend
source venv/bin/activate

# Создать миграции
python manage.py makemigrations

# Выполнить миграции
python manage.py migrate

# Проверить Django
python manage.py check
```

## 🔍 Диагностика

### Проверка импортов
```bash
cd backend
source venv/bin/activate

# Проверить Django
python manage.py check

# Проверить миграции
python manage.py showmigrations

# Проверить URL конфигурацию
python manage.py check --deploy
```

### Проверка зависимостей
```bash
# Проверить установленные пакеты
pip list | grep -i jwt
pip list | grep -i django

# Проверить версии
python -c "import rest_framework_simplejwt; print(rest_framework_simplejwt.__version__)"
```

## 📋 Исправленные файлы

### 1. `backend/app/api/urls.py`
- Исправлен импорт JWT views
- Добавлены правильные URL patterns для аутентификации

### 2. `backend/app/models/knowledge.py`
- Добавлен импорт модели Tenant
- Исправлены циклические импорты

### 3. `backend/app/models/ticket.py`
- Добавлен импорт модели Tenant
- Исправлены циклические импорты

## ⚠️ Частые проблемы

### 1. Циклические импорты
```
ImportError: cannot import name 'Tenant' from partially initialized module
```

**Решение:**
- Использовать строковые ссылки в ForeignKey: `'Tenant'`
- Импортировать модели в нужном порядке

### 2. Отсутствующие модули
```
ModuleNotFoundError: No module named 'rest_framework_simplejwt.urls'
```

**Решение:**
- Использовать правильные импорты из `rest_framework_simplejwt.views`
- Создать собственные URL patterns

### 3. Проблемы с миграциями
```
django.db.utils.ProgrammingError: relation "table_name" does not exist
```

**Решение:**
```bash
# Сбросить миграции
python manage.py migrate --fake-initial

# Или создать заново
python manage.py makemigrations --empty app_name
python manage.py migrate
```

## 🚀 После исправления

### Запуск Django
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

### Проверка API
```bash
# Проверить health endpoint
curl http://localhost:8000/api/v1/health/

# Проверить JWT endpoints
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## 📚 Полезные ссылки

- [Django REST Framework SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Django URL Configuration](https://docs.djangoproject.com/en/4.2/topics/http/urls/)
- [Django Migrations](https://docs.djangoproject.com/en/4.2/topics/migrations/)

## 🎯 Заключение

Проблемы с импортами в Django обычно связаны с:
1. Неправильными URL patterns
2. Циклическими импортами между моделями
3. Отсутствующими зависимостями

Используйте предоставленные исправления и скрипт для автоматического решения проблем.
