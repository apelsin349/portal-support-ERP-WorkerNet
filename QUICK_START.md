# 🚀 Быстрый старт WorkerNet Portal

## Установка за 5 минут

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-org/portal-support-ERP-WorkerNet.git
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

## Альтернативные способы запуска

### Автоматическая установка на Ubuntu 24.04
```bash
curl -fsSL https://raw.githubusercontent.com/your-org/portal-support-ERP-WorkerNet/main/scripts/install-ubuntu.sh | bash
```

### Ручная установка
```bash
# Установить зависимости
sudo apt update && sudo apt install -y python3.11 nodejs postgresql redis-server docker.io

# Настроить базу данных
sudo -u postgres psql -c "CREATE DATABASE worker_net; CREATE USER workernet WITH PASSWORD 'workernet123'; GRANT ALL PRIVILEGES ON DATABASE worker_net TO workernet;"

# Установить приложение
cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd ../frontend && npm install

# Запустить
cd ../backend && source venv/bin/activate && python manage.py migrate && python manage.py runserver
cd ../frontend && npm start
```

## Управление сервисами

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

## Первые шаги

1. **Вход в систему**: admin/admin123
2. **Создание тенанта**: Настройте вашу организацию
3. **Создание пользователей**: Добавьте команду поддержки
4. **Настройка SLA**: Определите правила обслуживания
5. **Создание тикетов**: Начните работу с поддержкой

## Проблемы?

### Проверка статуса
```bash
# Docker сервисы
docker-compose ps

# Логи
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Перезапуск
```bash
# Полный перезапуск
docker-compose down
docker-compose up -d --build
```

### Очистка
```bash
# Очистка Docker
docker system prune -a
docker volume prune
```

## Дополнительная информация

- **Полная документация**: [README_FULL.md](README_FULL.md)
- **Ubuntu инструкции**: [README_UBUNTU24.md](README_UBUNTU24.md)
- **API документация**: http://localhost:8000/api/docs
- **Grafana мониторинг**: http://localhost:3001

---

**Готово!** Ваш портал технической поддержки WorkerNet запущен и готов к работе! 🎉
