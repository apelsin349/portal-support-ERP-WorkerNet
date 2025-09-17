# 🔧 Устранение неполадок WorkerNet Portal

## Общие проблемы

### Проблемы с Docker

#### Сервисы не запускаются
```bash
# Проверить статус сервисов
docker-compose ps

# Просмотр логов
docker-compose logs -f

# Перезапуск всех сервисов
docker-compose down
docker-compose up -d --build
```

#### Ошибки с портами
```bash
# Проверить занятые порты
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :3000

# Освободить порты
sudo kill -9 <PID>

# Или изменить порты в docker-compose.yml
```

#### Проблемы с volumes
```bash
# Очистить volumes
docker-compose down -v
docker volume prune

# Пересоздать volumes
docker-compose up -d
```

### Проблемы с базой данных

#### Ошибки подключения
```bash
# Проверить статус PostgreSQL
sudo systemctl status postgresql

# Проверить подключение
psql -U workernet -d worker_net -h localhost

# Перезапустить PostgreSQL
sudo systemctl restart postgresql
```

#### Ошибки миграций
```bash
# Сбросить миграции
docker-compose exec backend python manage.py migrate --fake-initial

# Или создать новую миграцию
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

#### Проблемы с правами доступа
```bash
# Создать пользователя и базу данных
sudo -u postgres psql -c "CREATE USER workernet WITH PASSWORD 'workernet123';"
sudo -u postgres psql -c "CREATE DATABASE worker_net OWNER workernet;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE worker_net TO workernet;"
```

### Проблемы с Redis

#### Ошибки подключения
```bash
# Проверить статус Redis
sudo systemctl status redis-server

# Проверить подключение
redis-cli ping

# Перезапустить Redis
sudo systemctl restart redis-server
```

#### Проблемы с паролем
```bash
# Проверить конфигурацию
sudo nano /etc/redis/redis.conf

# Установить пароль
requirepass your_redis_password

# Перезапустить Redis
sudo systemctl restart redis-server
```

## Проблемы с Backend

### Django ошибки

#### Ошибки импорта
```bash
# Проверить виртуальное окружение
source venv/bin/activate
pip list

# Переустановить зависимости
pip install -r requirements.txt
```

#### Ошибки статических файлов
```bash
# Собрать статические файлы
python manage.py collectstatic --noinput

# Проверить настройки
python manage.py check
```

#### Ошибки миграций
```bash
# Создать миграции
python manage.py makemigrations

# Применить миграции
python manage.py migrate

# Сбросить миграции
python manage.py migrate --fake-initial
```

### API ошибки

#### Ошибки CORS
```python
# В settings.py добавить:
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

#### Ошибки аутентификации
```python
# Проверить JWT настройки
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

#### Ошибки сериализации
```python
# Проверить сериализаторы
class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
```

## Проблемы с Frontend

### React ошибки

#### Ошибки сборки
```bash
# Очистить кэш
npm cache clean --force

# Удалить node_modules
rm -rf node_modules package-lock.json

# Переустановить зависимости
npm install
```

#### Ошибки TypeScript
```bash
# Проверить типы
npm run type-check

# Исправить типы
npm run lint:fix
```

#### Ошибки Webpack
```bash
# Очистить кэш Webpack
rm -rf .next
rm -rf build

# Пересобрать
npm run build
```

### API ошибки

#### Ошибки подключения
```typescript
// Проверить URL API
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Проверить CORS настройки
const response = await fetch(`${API_URL}/api/tickets/`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  },
});
```

#### Ошибки WebSocket
```typescript
// Проверить WebSocket URL
const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

// Проверить подключение
const ws = new WebSocket(`${wsUrl}/ws/tickets/123/`);
ws.onopen = () => console.log('WebSocket connected');
ws.onerror = (error) => console.error('WebSocket error:', error);
```

## Проблемы с производительностью

### Медленные запросы

#### Оптимизация базы данных
```python
# Использовать select_related
tickets = Ticket.objects.select_related('created_by', 'assigned_to').all()

# Использовать prefetch_related
tickets = Ticket.objects.prefetch_related('tags').all()

# Использовать only
tickets = Ticket.objects.only('id', 'title', 'status').all()
```

#### Кэширование
```python
# Настроить кэширование
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Использовать кэширование
from django.core.cache import cache

def get_tickets():
    tickets = cache.get('tickets')
    if not tickets:
        tickets = Ticket.objects.all()
        cache.set('tickets', tickets, 300)  # 5 минут
    return tickets
```

### Медленная загрузка страниц

#### Оптимизация React
```typescript
// Lazy loading компонентов
const LazyComponent = React.lazy(() => import('./LazyComponent'));

// Мемоизация
const MemoizedComponent = React.memo(({ data }) => {
  return <div>{data.name}</div>;
});

// Виртуализация списков
import { FixedSizeList as List } from 'react-window';

const VirtualizedList = ({ items }) => (
  <List
    height={600}
    itemCount={items.length}
    itemSize={50}
    itemData={items}
  >
    {({ index, style, data }) => (
      <div style={style}>
        {data[index].name}
      </div>
    )}
  </List>
);
```

## Проблемы с мониторингом

### Prometheus ошибки

#### Ошибки подключения
```bash
# Проверить статус Prometheus
sudo systemctl status prometheus

# Проверить конфигурацию
promtool check config /etc/prometheus/prometheus.yml

# Перезапустить Prometheus
sudo systemctl restart prometheus
```

#### Ошибки метрик
```python
# Проверить метрики Django
from django_prometheus.models import PrometheusMetrics

metrics = PrometheusMetrics()
print(metrics.get_metrics())
```

### Grafana ошибки

#### Ошибки подключения к Prometheus
```bash
# Проверить конфигурацию Grafana
sudo nano /etc/grafana/grafana.ini

# Проверить подключение к Prometheus
curl http://localhost:9090/api/v1/query?query=up
```

#### Ошибки дашбордов
```bash
# Проверить права доступа
sudo chown -R grafana:grafana /var/lib/grafana

# Перезапустить Grafana
sudo systemctl restart grafana-server
```

## Проблемы с безопасностью

### Ошибки SSL

#### Проблемы с сертификатами
```bash
# Проверить сертификат
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/fullchain.pem -text -noout

# Обновить сертификат
sudo certbot renew

# Проверить конфигурацию Nginx
sudo nginx -t
```

#### Ошибки CORS
```python
# Настроить CORS
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]

CORS_ALLOW_CREDENTIALS = True
```

### Ошибки аутентификации

#### Проблемы с JWT
```python
# Проверить JWT настройки
SIMPLE_JWT = {
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}
```

## Проблемы с развертыванием

### Ошибки Nginx

#### Проблемы с конфигурацией
```bash
# Проверить синтаксис
sudo nginx -t

# Перезагрузить конфигурацию
sudo systemctl reload nginx

# Проверить логи
sudo tail -f /var/log/nginx/error.log
```

#### Ошибки проксирования
```nginx
# Проверить upstream
upstream backend {
    server 127.0.0.1:8000;
}

# Проверить proxy_pass
location /api/ {
    proxy_pass http://backend;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Ошибки systemd

#### Проблемы с сервисами
```bash
# Проверить статус
sudo systemctl status workernet-backend

# Проверить логи
sudo journalctl -u workernet-backend -f

# Перезапустить сервис
sudo systemctl restart workernet-backend
```

#### Ошибки конфигурации
```ini
# Проверить файл сервиса
sudo nano /etc/systemd/system/workernet-backend.service

[Unit]
Description=WorkerNet Backend
After=network.target

[Service]
Type=simple
User=workernet
WorkingDirectory=/var/www/workernet
ExecStart=/var/www/workernet/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## Проблемы с логированием

### Ошибки логов

#### Проблемы с правами доступа
```bash
# Создать директорию логов
sudo mkdir -p /var/log/workernet
sudo chown workernet:workernet /var/log/workernet

# Проверить права доступа
ls -la /var/log/workernet
```

#### Ошибки ротации логов
```bash
# Настроить logrotate
sudo nano /etc/logrotate.d/workernet

/var/log/workernet/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 workernet workernet
}
```

## Проблемы с резервным копированием

### Ошибки резервного копирования

#### Проблемы с PostgreSQL
```bash
# Проверить подключение
pg_dump -U workernet -d worker_net > /tmp/test_backup.sql

# Проверить права доступа
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE worker_net TO workernet;"
```

#### Проблемы с файлами
```bash
# Проверить права доступа
sudo chown -R workernet:workernet /var/www/workernet

# Проверить место на диске
df -h
```

## Полезные команды

### Диагностика

```bash
# Проверить статус всех сервисов
docker-compose ps
sudo systemctl status postgresql redis-server nginx

# Проверить логи
docker-compose logs -f
sudo journalctl -u workernet-backend -f

# Проверить подключения
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000

# Проверить место на диске
df -h
du -sh /var/www/workernet

# Проверить память
free -h
top
```

### Очистка

```bash
# Очистить Docker
docker system prune -a
docker volume prune

# Очистить логи
sudo journalctl --vacuum-time=7d

# Очистить кэш
sudo apt clean
sudo apt autoremove
```

### Восстановление

```bash
# Восстановить из резервной копии
pg_restore -U workernet -d worker_net backup.sql

# Восстановить файлы
tar -xzf backup.tar.gz -C /var/www/workernet

# Восстановить конфигурацию
sudo cp -r backup/config/* /etc/
```

## Получение помощи

### Логи и диагностика

```bash
# Собрать информацию о системе
uname -a
lsb_release -a
docker --version
python --version
node --version

# Собрать логи
docker-compose logs > logs.txt
sudo journalctl -u workernet-backend > systemd.log
```

### Создание issue

При создании issue в GitHub включите:
1. Описание проблемы
2. Шаги для воспроизведения
3. Ожидаемое поведение
4. Фактическое поведение
5. Логи и скриншоты
6. Информацию о системе

### Контакты

- **GitHub Issues**: [Создать issue](https://github.com/your-org/portal-support-ERP-WorkerNet/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/portal-support-ERP-WorkerNet/discussions)
- **Email**: support@workernet.com
- **Документация**: [docs.workernet.com](https://docs.workernet.com)

---

## 🎯 Готово!

Теперь вы знаете, как устранить большинство проблем с WorkerNet Portal!

**Следующие шаги:**
1. Проверить логи и диагностику
2. Применить соответствующие исправления
3. Создать issue, если проблема не решена
4. Обратиться за помощью к сообществу

**Нужна помощь?** Создайте issue в репозитории или обратитесь к документации!
