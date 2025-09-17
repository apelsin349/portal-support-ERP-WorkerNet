# 🧪 Тестирование WorkerNet Portal

## Обзор тестирования

WorkerNet Portal использует многоуровневую стратегию тестирования для обеспечения качества и надежности системы.

## Типы тестов

### 1. Unit тесты (Модульные тесты)

#### Backend (Python/pytest)
```bash
# Запуск всех unit тестов
pytest

# Запуск с покрытием
pytest --cov=app --cov-report=html

# Запуск конкретного теста
pytest tests/test_models.py::TestTicketModel::test_ticket_creation
```

#### Frontend (Jest/React Testing Library)
```bash
# Запуск всех тестов
npm test

# Запуск с покрытием
npm run test:coverage

# Запуск в watch режиме
npm run test:watch
```

### 2. Integration тесты (Интеграционные тесты)

#### API тесты
```python
# tests/test_api.py
def test_ticket_creation_api(client, user, tenant):
    response = client.post('/api/v1/tickets/', {
        'title': 'Test Ticket',
        'description': 'Test Description',
        'priority': 'high'
    })
    assert response.status_code == 201
    assert response.data['title'] == 'Test Ticket'
```

#### Database тесты
```python
# tests/test_database.py
def test_ticket_creation_database():
    ticket = Ticket.objects.create(
        title='Test Ticket',
        description='Test Description',
        created_by=user,
        tenant=tenant
    )
    assert ticket.title == 'Test Ticket'
    assert ticket.status == 'open'
```

### 3. E2E тесты (End-to-End тесты)

#### Cypress тесты
```javascript
// cypress/integration/tickets.spec.js
describe('Ticket Management', () => {
  it('should create a new ticket', () => {
    cy.visit('/tickets')
    cy.get('[data-testid="create-ticket-btn"]').click()
    cy.get('[data-testid="ticket-title"]').type('Test Ticket')
    cy.get('[data-testid="ticket-description"]').type('Test Description')
    cy.get('[data-testid="submit-ticket"]').click()
    cy.get('[data-testid="ticket-list"]').should('contain', 'Test Ticket')
  })
})
```

## Настройка тестирования

### Backend тестирование

#### requirements-dev.txt
```
pytest==7.4.3
pytest-django==4.7.0
pytest-cov==4.1.0
factory-boy==3.3.0
faker==20.1.0
```

#### pytest.ini
```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
addopts = --cov=app --cov-report=html --cov-report=term-missing
```

### Frontend тестирование

#### package.json
```json
{
  "scripts": {
    "test": "jest",
    "test:coverage": "jest --coverage",
    "test:watch": "jest --watch"
  },
  "devDependencies": {
    "@testing-library/react": "^13.4.0",
    "@testing-library/jest-dom": "^5.17.0",
    "jest": "^29.7.0"
  }
}
```

## Примеры тестов

### Backend тесты

#### Модели
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
        self.assertEqual(ticket.priority, "medium")
    
    def test_ticket_str_representation(self):
        ticket = Ticket.objects.create(
            title="Test Ticket",
            description="Test Description",
            created_by=self.user,
            tenant=self.tenant
        )
        self.assertEqual(str(ticket), "Test Ticket")
```

#### API Views
```python
# tests/test_views.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from app.models import Ticket, User, Tenant

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(tenant):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        tenant=tenant
    )

@pytest.fixture
def tenant():
    return Tenant.objects.create(
        name="Test Tenant",
        slug="test",
        domain="test.com"
    )

def test_ticket_list_api(api_client, user, tenant):
    api_client.force_authenticate(user=user)
    response = api_client.get(reverse('ticket-list'))
    assert response.status_code == status.HTTP_200_OK

def test_ticket_creation_api(api_client, user, tenant):
    api_client.force_authenticate(user=user)
    data = {
        'title': 'Test Ticket',
        'description': 'Test Description',
        'priority': 'high'
    }
    response = api_client.post(reverse('ticket-list'), data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['title'] == 'Test Ticket'
```

### Frontend тесты

#### Компоненты
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

  it('handles click events', () => {
    const mockOnClick = jest.fn();
    render(<TicketCard ticket={mockTicket} onClick={mockOnClick} />);
    
    screen.getByText('Test Ticket').click();
    expect(mockOnClick).toHaveBeenCalledWith(mockTicket);
  });
});
```

#### Hooks
```typescript
// src/hooks/__tests__/useTickets.test.ts
import { renderHook, act } from '@testing-library/react';
import { useTickets } from '../useTickets';

describe('useTickets', () => {
  it('should fetch tickets on mount', async () => {
    const { result } = renderHook(() => useTickets());
    
    expect(result.current.loading).toBe(true);
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 100));
    });
    
    expect(result.current.loading).toBe(false);
    expect(result.current.tickets).toBeDefined();
  });
});
```

## Тестовые данные

### Factory Boy (Backend)
```python
# tests/factories.py
import factory
from app.models import Ticket, User, Tenant

class TenantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tenant
    
    name = factory.Sequence(lambda n: f"Tenant {n}")
    slug = factory.Sequence(lambda n: f"tenant-{n}")
    domain = factory.Sequence(lambda n: f"tenant{n}.com")

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    tenant = factory.SubFactory(TenantFactory)

class TicketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ticket
    
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text', max_nb_chars=200)
    priority = factory.Iterator(['low', 'medium', 'high', 'urgent', 'critical'])
    status = factory.Iterator(['open', 'in_progress', 'pending', 'resolved', 'closed'])
    created_by = factory.SubFactory(UserFactory)
    tenant = factory.SubFactory(TenantFactory)
```

### Faker (Frontend)
```typescript
// src/utils/testData.ts
import { faker } from '@faker-js/faker';

export const createMockTicket = (overrides = {}) => ({
  id: faker.datatype.number(),
  title: faker.lorem.sentence(),
  description: faker.lorem.paragraph(),
  status: faker.helpers.arrayElement(['open', 'in_progress', 'pending', 'resolved', 'closed']),
  priority: faker.helpers.arrayElement(['low', 'medium', 'high', 'urgent', 'critical']),
  created_at: faker.date.past().toISOString(),
  ...overrides
});

export const createMockUser = (overrides = {}) => ({
  id: faker.datatype.number(),
  username: faker.internet.userName(),
  email: faker.internet.email(),
  first_name: faker.name.firstName(),
  last_name: faker.name.lastName(),
  ...overrides
});
```

## CI/CD тестирование

### GitHub Actions
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
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

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: 18
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage --watchAll=false
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## Покрытие кода

### Backend покрытие
```bash
# Генерация отчета покрытия
pytest --cov=app --cov-report=html --cov-report=term-missing

# Просмотр отчета
open htmlcov/index.html
```

### Frontend покрытие
```bash
# Генерация отчета покрытия
npm run test:coverage

# Просмотр отчета
open coverage/lcov-report/index.html
```

## Performance тестирование

### Load тестирование
```python
# tests/performance/test_load.py
import pytest
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model

User = get_user_model()

class LoadTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_ticket_list_performance(self):
        import time
        start_time = time.time()
        
        response = self.client.get('/api/v1/tickets/')
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 1.0)  # Должно быть меньше 1 секунды
```

### Memory тестирование
```python
# tests/performance/test_memory.py
import pytest
import tracemalloc
from app.services.ticket_service import TicketService

def test_ticket_service_memory_usage():
    tracemalloc.start()
    
    service = TicketService()
    # Выполнить операции
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Проверить, что использование памяти не превышает лимит
    assert peak < 50 * 1024 * 1024  # 50 MB
```

## Security тестирование

### SQL Injection тесты
```python
# tests/security/test_sql_injection.py
def test_sql_injection_protection(api_client, user):
    api_client.force_authenticate(user=user)
    
    malicious_input = "'; DROP TABLE tickets; --"
    
    response = api_client.get(f'/api/v1/tickets/?search={malicious_input}')
    
    # Должен вернуть 400 или безопасно обработать
    assert response.status_code in [200, 400]
    # Проверить, что таблица не была удалена
    assert Ticket.objects.count() > 0
```

### XSS тесты
```python
# tests/security/test_xss.py
def test_xss_protection(api_client, user):
    api_client.force_authenticate(user=user)
    
    malicious_input = "<script>alert('XSS')</script>"
    
    response = api_client.post('/api/v1/tickets/', {
        'title': malicious_input,
        'description': 'Test description'
    })
    
    assert response.status_code == 201
    # Проверить, что скрипт был экранирован
    assert '<script>' not in response.data['title']
```

## E2E тестирование

### Cypress тесты
```javascript
// cypress/integration/ticket_flow.spec.js
describe('Ticket Management Flow', () => {
  beforeEach(() => {
    cy.login('admin', 'admin123');
    cy.visit('/tickets');
  });

  it('should create, assign, and close a ticket', () => {
    // Создать тикет
    cy.get('[data-testid="create-ticket-btn"]').click();
    cy.get('[data-testid="ticket-title"]').type('E2E Test Ticket');
    cy.get('[data-testid="ticket-description"]').type('This is an E2E test ticket');
    cy.get('[data-testid="ticket-priority"]').select('high');
    cy.get('[data-testid="submit-ticket"]').click();
    
    // Проверить, что тикет создан
    cy.get('[data-testid="ticket-list"]').should('contain', 'E2E Test Ticket');
    
    // Назначить тикет
    cy.get('[data-testid="ticket-row"]').first().click();
    cy.get('[data-testid="assign-ticket-btn"]').click();
    cy.get('[data-testid="assignee-select"]').select('support1');
    cy.get('[data-testid="confirm-assignment"]').click();
    
    // Проверить назначение
    cy.get('[data-testid="assigned-to"]').should('contain', 'support1');
    
    // Закрыть тикет
    cy.get('[data-testid="close-ticket-btn"]').click();
    cy.get('[data-testid="close-reason"]').type('Resolved');
    cy.get('[data-testid="confirm-close"]').click();
    
    // Проверить закрытие
    cy.get('[data-testid="ticket-status"]').should('contain', 'closed');
  });
});
```

## Mocking и Stubbing

### Backend mocking
```python
# tests/mocks.py
from unittest.mock import patch, MagicMock

@patch('app.services.email_service.send_email')
def test_ticket_creation_sends_email(mock_send_email, api_client, user):
    api_client.force_authenticate(user=user)
    
    response = api_client.post('/api/v1/tickets/', {
        'title': 'Test Ticket',
        'description': 'Test Description'
    })
    
    assert response.status_code == 201
    mock_send_email.assert_called_once()
```

### Frontend mocking
```typescript
// src/__mocks__/api.ts
export const mockApi = {
  tickets: {
    list: jest.fn().mockResolvedValue({
      data: [createMockTicket()],
      total: 1
    }),
    create: jest.fn().mockResolvedValue({
      data: createMockTicket()
    })
  }
};
```

## Тестовые среды

### Docker тестирование
```yaml
# docker-compose.test.yml
version: '3.8'
services:
  test-db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: worker_net_test
      POSTGRES_USER: workernet
      POSTGRES_PASSWORD: workernet123
  
  test-redis:
    image: redis:7-alpine
    command: redis-server --requirepass redis123
  
  test-backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://workernet:workernet123@test-db:5432/worker_net_test
      REDIS_URL: redis://:redis123@test-redis:6379/0
    depends_on:
      - test-db
      - test-redis
    command: pytest
```

## Best Practices

### 1. Тестовые данные
- Используйте Factory Boy для создания тестовых данных
- Очищайте данные после каждого теста
- Используйте фикстуры для переиспользования

### 2. Изоляция тестов
- Каждый тест должен быть независимым
- Не полагайтесь на порядок выполнения тестов
- Используйте транзакции для изоляции

### 3. Покрытие кода
- Стремитесь к покрытию 80%+ для критических компонентов
- Не гонитесь за 100% покрытием
- Фокусируйтесь на тестировании бизнес-логики

### 4. Производительность
- Тесты должны выполняться быстро
- Используйте параллельное выполнение
- Оптимизируйте медленные тесты

---

## 🎯 Готово!

Теперь вы знаете, как тестировать WorkerNet Portal!

**Ключевые принципы:**
1. **Пирамида тестирования** - больше unit тестов, меньше E2E
2. **Изоляция** - независимые тесты
3. **Покрытие** - тестирование критических путей
4. **Производительность** - быстрые тесты
5. **Автоматизация** - CI/CD интеграция

**Следующие шаги:**
1. Настроить тестовую среду
2. Написать unit тесты
3. Добавить integration тесты
4. Настроить E2E тесты
5. Интегрировать в CI/CD

**Нужна помощь?** Обратитесь к документации или создайте issue в репозитории!
