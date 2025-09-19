# 🚀 WorkerNet Portal - Скрипты установки и обновления

Полный набор скриптов для установки, обновления и управления WorkerNet Portal с поддержкой PWA.

## 📋 Содержание

- [Установка](#установка)
- [Обновление](#обновление)
- [Docker](#docker)
- [Проверка PWA](#проверка-pwa)
- [Устранение неполадок](#устранение-неполадок)

## 🛠 Установка

### **Ubuntu/Linux**

```bash
# Полная установка с нуля
./scripts/install-ubuntu.sh

# Установка с самообновлением скрипта
WORKERNET_SELF_UPDATE=1 ./scripts/install-ubuntu.sh

# Неинтерактивная установка
WORKERNET_NONINTERACTIVE=1 ./scripts/install-ubuntu.sh
```

### **Windows**

```cmd
# Запуск установки
scripts\install-ubuntu.sh
```

### **Переменные окружения**

```bash
# Основные настройки
export WORKERNET_DOMAIN_OR_IP="your-domain.com"
export WORKERNET_DB_PASS="your-secure-password"
export WORKERNET_REDIS_PASS="your-redis-password"
export WORKERNET_ADMIN_PASS="your-admin-password"

# Дополнительные настройки
export WORKERNET_INSTALL_MONITORING=1  # Установить Prometheus/Grafana
export WORKERNET_REQUIRE_FRONTEND=true  # Требовать фронтенд
export WORKERNET_ALLOWED_HOSTS_EXTRA="example.com,test.com"
```

## 🔄 Обновление

### **Быстрое обновление**

```bash
# Проверка обновлений
./scripts/quick-update.sh --check

# Обновление с подтверждением
./scripts/quick-update.sh

# Принудительное обновление
./scripts/quick-update.sh --force

# Неинтерактивное обновление
WORKERNET_NONINTERACTIVE=1 ./scripts/quick-update.sh
```

### **Windows**

```cmd
# Проверка обновлений
scripts\quick-update.sh --check

# Обновление
scripts\quick-update.sh
```

## 🐳 Docker

### **Запуск через Docker**

```bash
# Полный запуск всех сервисов
./scripts/start-docker.sh start

# Остановка сервисов
./scripts/start-docker.sh stop

# Перезапуск
./scripts/start-docker.sh restart

# Просмотр логов
./scripts/start-docker.sh logs

# Проверка статуса
./scripts/start-docker.sh status
```

### **Прямой запуск Docker Compose**

```bash
# Запуск всех сервисов
docker-compose up -d

# Сборка с PWA поддержкой
docker-compose build --no-cache frontend

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

## 🔍 Проверка PWA

### **Полная проверка PWA**

```bash
# Проверка всех компонентов PWA
./scripts/check-pwa.sh

# Проверка только файлов
./scripts/check-pwa.sh --files

# Проверка только сборки
./scripts/check-pwa.sh --build

# Проверка только сервисов
./scripts/check-pwa.sh --services
```

### **Windows**

```cmd
# Полная проверка PWA
scripts\check-pwa.bat
```

## 📊 Что проверяется

### **PWA компоненты**
- ✅ `manifest.json` - манифест приложения
- ✅ `sw.js` - Service Worker
- ✅ Иконки PWA (192x192, 512x512)
- ✅ `browserconfig.xml` - поддержка Windows
- ✅ Webpack конфигурация
- ✅ PWA зависимости

### **Сборка фронтенда**
- ✅ TypeScript компиляция
- ✅ Webpack сборка
- ✅ PWA генерация
- ✅ Иконки PWA
- ✅ Service Worker

### **Сервисы**
- ✅ Фронтенд (http://localhost:3000)
- ✅ API (http://localhost:8000)
- ✅ Manifest доступность
- ✅ Service Worker доступность

## 🚀 Быстрый старт

### **1. Установка**

```bash
# Клонируйте репозиторий
git clone https://github.com/apelsin349/portal-support-ERP-WorkerNet.git
cd portal-support-ERP-WorkerNet

# Запустите установку
./scripts/install-ubuntu.sh
```

### **2. Проверка PWA**

```bash
# Проверьте PWA функциональность
./scripts/check-pwa.sh
```

### **3. Доступ к приложению**

- **Фронтенд (PWA)**: http://localhost:3000
- **API**: http://localhost:8000
- **Админ-панель**: http://localhost:8000/admin
- **Grafana**: http://localhost:3001 (admin/admin123)

## 🔧 Устранение неполадок

### **Проблемы с установкой**

```bash
# Проверка зависимостей
./scripts/check-dependencies.sh

# Исправление npm
./scripts/fix-npm-deps.sh

# Сброс базы данных
./scripts/quick-db-fix.sh
```

### **Проблемы с PWA**

```bash
# Проверка PWA
./scripts/check-pwa.sh

# Пересборка фронтенда
cd frontend
npm run generate-icons
npm run build
```

### **Проблемы с Docker**

```bash
# Пересборка образов
docker-compose build --no-cache

# Очистка контейнеров
docker-compose down -v
docker system prune -f
```

## 📝 Логи и мониторинг

### **Логи сервисов**

```bash
# Логи бэкенда
sudo journalctl -u workernet-backend -f

# Логи фронтенда
sudo journalctl -u workernet-frontend -f

# Логи Docker
docker-compose logs -f [service]
```

### **Мониторинг**

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
- **Celery Flower**: http://localhost:5555

## 🔄 Автоматические обновления

### **Настройка cron**

```bash
# Автоматическое обновление ежедневно в 2:00
0 2 * * * /opt/update-workernet.sh >> /var/log/workernet-update.log 2>&1
```

### **Логи обновлений**

```bash
# Просмотр логов обновлений
tail -f /var/log/workernet-update.log
```

## 🆘 Поддержка

### **Частые проблемы**

1. **PWA не устанавливается**
   - Проверьте HTTPS (требуется для production)
   - Убедитесь в корректности manifest.json
   - Проверьте Service Worker

2. **Ошибки сборки фронтенда**
   - Очистите node_modules: `rm -rf node_modules && npm install`
   - Проверьте версию Node.js (требуется 18+)
   - Запустите `npm run generate-icons`

3. **Проблемы с базой данных**
   - Запустите `./scripts/quick-db-fix.sh`
   - Проверьте статус PostgreSQL: `sudo systemctl status postgresql`

### **Контакты**

- GitHub Issues: [Создать issue]
- Email: support@workernet.com
- Документация: [Ссылка на docs]

## 📄 Лицензия

MIT License - см. файл LICENSE для деталей.

---

## 🎉 Заключение

Все скрипты протестированы и готовы к production использованию. PWA функциональность полностью интегрирована в процесс установки и обновления.

**Готово к использованию!** 🚀
