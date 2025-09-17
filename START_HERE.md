# 🚀 WorkerNet Portal - Начните здесь!

## Что это?

WorkerNet Portal - это современная система технической поддержки для ERP систем, построенная на Django REST Framework, React и Docker. Система поддерживает мультитенантность, real-time обновления, A/B тестирование и полный мониторинг.

## 🎯 Быстрый старт (5 минут)

### 1. Клонирование репозитория
```bash
git clone https://github.com/apelsin349/portal-support-ERP-WorkerNet.git
cd portal-support-ERP-WorkerNet
```

### 2. Запуск через Docker (рекомендуется)
```bash
# Сделать скрипты исполняемыми
chmod +x scripts/*.sh

# Запустить все сервисы
./scripts/start-docker.sh start
```

### 3. Доступ к приложению
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **Grafana**: http://localhost:3001

### 4. Вход в систему
- **Пользователь**: admin
- **Пароль**: admin123

## 📚 Документация

### Основные руководства
- **[QUICK_START.md](QUICK_START.md)** - Быстрый старт за 5 минут
- **[README_FULL.md](README_FULL.md)** - Полная документация
- **[README_UBUNTU24.md](README_UBUNTU24.md)** - Инструкции для Ubuntu 24.04
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Развертывание в продакшене

### Техническая документация
- **[API.md](API.md)** - API документация
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Архитектура системы
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Разработка
- **[TESTING.md](TESTING.md)** - Тестирование
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Устранение неполадок

## 🛠️ Альтернативные способы запуска

### Автоматическая установка на Ubuntu 24.04
```bash
# Важно: НЕ запускайте под root. Используйте обычного пользователя с sudo.
# Если вы сейчас под root, создайте пользователя и переключитесь на него:
# adduser workernet && usermod -aG sudo workernet && su - workernet

# Скачать и запустить установщик (с корректной ссылкой на репозиторий)
curl -fsSL https://raw.githubusercontent.com/apelsin349/portal-support-ERP-WorkerNet/main/scripts/install-ubuntu.sh \
| sed 's|https://github.com/apelsin349/portal-support-ERP-WorkerNet.git|https://github.com/apelsin349/portal-support-ERP-WorkerNet.git|' \
| bash
```

### Ручная установка
```bash
# 1. Установить зависимости
sudo apt update && sudo apt install -y python3.11 nodejs postgresql redis-server docker.io

# 2. Настроить базу данных
sudo -u postgres psql -c "CREATE DATABASE worker_net; CREATE USER workernet WITH PASSWORD 'workernet123'; GRANT ALL PRIVILEGES ON DATABASE worker_net TO workernet;"

# 3. Установить приложение
cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd ../frontend && npm install

# 4. Запустить
cd ../backend && source venv/bin/activate && python manage.py migrate && python manage.py runserver
cd ../frontend && npm start
```

## 🌟 Основные возможности

### Система тикетов
- ✅ Создание и управление тикетами
- ✅ Приоритизация и категоризация
- ✅ Назначение и эскалация
- ✅ Комментарии и вложения
- ✅ SLA управление
- ✅ Автоматические правила

### База знаний
- ✅ Статьи и категории
- ✅ Поиск и фильтрация
- ✅ Оценка и рейтинг
- ✅ Версионирование
- ✅ SEO оптимизация

### Мультитенантность
- ✅ Изоляция данных по клиентам
- ✅ Кастомизация интерфейса
- ✅ Управление пользователями
- ✅ Настройки по тенантам

### Real-time обновления
- ✅ WebSocket соединения
- ✅ Live уведомления
- ✅ Чат поддержки
- ✅ Коллаборация

### A/B тестирование
- ✅ Feature flags
- ✅ Статистический анализ
- ✅ Эксперименты
- ✅ Автоматические решения

### Мониторинг
- ✅ Prometheus метрики
- ✅ Grafana дашборды
- ✅ ELK Stack логирование
- ✅ Алертинг
- ✅ Performance мониторинг

## 🔧 Управление сервисами

### Docker команды
```bash
# Запуск
./scripts/start-docker.sh start

# Остановка
./scripts/start-docker.sh stop

# Перезапуск
./scripts/start-docker.sh restart

# Логи
./scripts/start-docker.sh logs

# Статус
./scripts/start-docker.sh status
```

### Прямые Docker Compose команды
```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Логи
docker-compose logs -f

# Выполнение команд
docker-compose exec backend python manage.py migrate
docker-compose exec frontend npm run build
```

## 📊 Мониторинг

### Доступные интерфейсы
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Admin Panel**: http://localhost:8000/admin
- **Grafana**: http://localhost:3001 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Kibana**: http://localhost:5601
- **Celery Flower**: http://localhost:5555

### Основные метрики
- Response time (95th percentile)
- Error rate
- Database query performance
- Memory usage
- CPU usage
- Active connections
- Queue length

## 🚨 Устранение неполадок

### Частые проблемы
```bash
# Проверить статус сервисов
docker-compose ps

# Просмотр логов
docker-compose logs -f backend
docker-compose logs -f frontend

# Перезапуск
docker-compose restart

# Полный перезапуск
docker-compose down
docker-compose up -d --build
```

### Проблемы с портами
```bash
# Проверить занятые порты
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :3000

# Освободить порты
sudo kill -9 <PID>
```

### Проблемы с базой данных
```bash
# Проверить подключение
docker-compose exec backend python manage.py dbshell

# Выполнить миграции
docker-compose exec backend python manage.py migrate

# Создать суперпользователя
docker-compose exec backend python manage.py createsuperuser
```

## 🔐 Безопасность

### Настройка паролей
```bash
# Изменить пароли по умолчанию
# В файле .env:
DB_PASSWORD=your_secure_password
REDIS_PASSWORD=your_secure_redis_password
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
```

### SSL сертификаты
```bash
# Установить Certbot
sudo apt install certbot python3-certbot-nginx

# Получить SSL сертификат
sudo certbot --nginx -d yourdomain.com
```

## 📱 Мобильное приложение

### Установка React Native CLI
```bash
npm install -g @react-native-community/cli
```

### Запуск мобильного приложения
```bash
cd mobile

# Android
npx react-native run-android

# iOS
npx react-native run-ios
```

## 🤝 Вклад в проект

### Установка для разработки
```bash
# Форк репозитория
git clone https://github.com/your-username/portal-support-ERP-WorkerNet.git
cd portal-support-ERP-WorkerNet

# Создать ветку
git checkout -b feature/your-feature

# Установить зависимости
cd backend && pip install -r requirements-dev.txt
cd ../frontend && npm install

# Запустить тесты
cd ../backend && pytest
cd ../frontend && npm test

# Создать Pull Request
```

### Стандарты кода
- **Python**: PEP 8, Black, isort, flake8
- **JavaScript**: ESLint, Prettier
- **Git**: Conventional Commits
- **Testing**: pytest, Jest

## 📞 Поддержка

### Получение помощи
- **GitHub Issues**: [Создать issue](https://github.com/your-org/portal-support-ERP-WorkerNet/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/portal-support-ERP-WorkerNet/discussions)
- **Email**: support@workernet.com
- **Документация**: [docs.workernet.com](https://docs.workernet.com)

### Полезные ссылки
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/
- **Postman Collection**: https://www.postman.com/workernet/collection/12345678

## 🎯 Следующие шаги

### После запуска
1. **Вход в систему**: admin/admin123
2. **Создание тенанта**: Настройте вашу организацию
3. **Создание пользователей**: Добавьте команду поддержки
4. **Настройка SLA**: Определите правила обслуживания
5. **Создание тикетов**: Начните работу с поддержкой

### Для разработки
1. Изучить архитектуру системы
2. Настроить среду разработки
3. Создать первую фичу
4. Написать тесты
5. Создать Pull Request

### Для продакшена
1. Настроить SSL сертификаты
2. Настроить мониторинг
3. Настроить резервное копирование
4. Настроить алерты
5. Настроить обновления

---

## 🎉 Готово!

Ваш портал технической поддержки WorkerNet запущен и готов к работе!

**Нужна помощь?** Обратитесь к документации или создайте issue в репозитории!

**Удачной работы!** 🚀

## ✅ Быстрые проверочные тесты (smoke)

### Проверка в Docker-окружении (локально)
```bash
chmod +x scripts/ci-smoke-docker.sh
./scripts/ci-smoke-docker.sh
```

### Полная проверка на новом сервере Ubuntu 24.04
```bash
chmod +x scripts/ci-smoke-ubuntu.sh
./scripts/ci-smoke-ubuntu.sh
```

Что выполняет автоматическая проверка (оба скрипта):
- Устанавливает/проверяет зависимости (Docker; для Ubuntu — Python/Node/PostgreSQL/Redis/Docker)
- Собирает и запускает сервисы через Docker Compose
- Применяет миграции базы данных
- Создаёт суперпользователя (admin/admin123), если отсутствует
- Проверяет здоровье сервисов (GET /health/ → 200)
- Делает пробный запрос к API (JWT + /api/v1/tickets/)
- Проверяет доступность фронтенда (:3000)
- Запрашивает базовые метрики (если включены)
- При любом сбое выводит логи и завершает выполнение с ошибкой
