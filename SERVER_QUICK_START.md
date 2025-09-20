# 🚀 Быстрый старт на сервере Ubuntu

## 📋 Что нужно

- Сервер Ubuntu 24.04 LTS (рекомендуется)
- SSH доступ к серверу
- Права sudo для пользователя

## ⚡ Установка за 3 шага

### 1. Подключение к серверу

```bash
# Подключитесь к серверу по SSH
ssh user@your-server-ip
```

### 2. Клонирование и установка

```bash
# Клонируйте репозиторий
git clone https://github.com/apelsin349/portal-support-ERP-WorkerNet.git
cd portal-support-ERP-WorkerNet

# Запустите универсальную установку
bash scripts/universal-install-update.sh
```

### 3. Доступ к приложению

После установки WorkerNet Portal будет доступен по адресам:

- **Frontend (PWA)**: http://YOUR_SERVER_IP:3000
- **API**: http://YOUR_SERVER_IP:8000
- **Админ-панель**: http://YOUR_SERVER_IP:8000/admin
- **Grafana**: http://YOUR_SERVER_IP:3001

**Логин**: admin | **Пароль**: admin123

## 🔧 Полезные команды

### Управление сервисами

```bash
# Статус сервисов
sudo systemctl status workernet-backend workernet-frontend

# Перезапуск сервисов
sudo systemctl restart workernet-backend workernet-frontend

# Логи бэкенда
sudo journalctl -u workernet-backend -f

# Логи фронтенда
sudo journalctl -u workernet-frontend -f
```

### Обновление

```bash
# Обновление системы
bash scripts/universal-install-update.sh

# Проверка обновлений
bash scripts/universal-install-update.sh --check
```

## 🔥 Файрвол

Скрипт автоматически настроит файрвол, но можно проверить:

```bash
# Статус файрвола
sudo ufw status

# Открыть дополнительные порты (если нужно)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
```

## 🆘 Если что-то пошло не так

### Проблемы с правами

```bash
# Запуск без execute-бита
bash scripts/universal-install-update.sh

# Исправление прав
chmod +x scripts/universal-install-update.sh
dos2unix scripts/universal-install-update.sh
```

### Проблемы с Docker

```bash
# Проверка Docker
sudo systemctl status docker

# Перезапуск Docker
sudo systemctl restart docker

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker
```

### Быстрое исправление

```bash
# Исправление зависимостей
bash scripts/fix-npm-deps.sh

# Исправление базы данных
bash scripts/quick-db-fix.sh

# Проверка PWA
bash scripts/check-pwa.sh
```

## 🎯 Готово!

После выполнения всех шагов WorkerNet Portal будет полностью настроен и готов к работе на вашем сервере Ubuntu.

---

*Для получения дополнительной помощи см. [Полное руководство](WORKERNET_PORTAL_GUIDE.md)*
