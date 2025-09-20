# 🚀 WorkerNet Portal

Современная система технической поддержки с web-интерфейсом и API.

## 📚 Документация

**👉 [Полное руководство](WORKERNET_PORTAL_GUIDE.md)** - основной документ со всей информацией

### Специализированная документация

- [🌐 Настройка домена/IP](Настройка%20домена%20или%20IP-адреса.md) - **важно!** настройка для внешнего доступа
- [🏗️ Архитектура](АРХИТЕКТУРА.md) - детальное описание архитектуры системы
- [💻 Разработка](РАЗРАБОТКА.md) - руководство для разработчиков
- [🔧 Развертывание](РАЗВЕРТЫВАНИЕ.md) - инструкции по развертыванию
- [📚 API](API_ДОКУМЕНТАЦИЯ.md) - полная документация API
- [🧪 Тестирование](ТЕСТИРОВАНИЕ.md) - стратегии и инструменты тестирования
- [🔍 Устранение неполадок](УСТРАНЕНИЕ_НЕПОЛАДОК.md) - решения частых проблем
- [📦 Обновления](ОБНОВЛЕНИЯ.md) - процедуры обновления системы
- [🎯 Современные практики](СОВРЕМЕННЫЕ_ПРАКТИКИ.md) - лучшие практики разработки

## ⚡ Быстрый старт

```bash
# С Docker (рекомендуется)
git clone https://github.com/apelsin349/portal-support-ERP-WorkerNet.git
cd portal-support-ERP-WorkerNet

# Создать файл окружения
cp env.example .env

# Запустить все сервисы
docker compose up -d

# Или установка на Ubuntu
./scripts/universal-install-update.sh
```

### Если получаете «Permission denied» при запуске скриптов

На некоторых файловых системах (WSL/NTFS/SMB) может теряться execute-бит. Используйте один из вариантов:

```bash
# Запустить без execute-бита
bash ./scripts/universal-install-update.sh

# Или единоразово поправить права и переводы строк
bash ./scripts/fix-perms.sh

# После этого можно запускать обычно
./scripts/universal-install-update.sh
```

Рекомендуется также для WSL включить метаданные в `/etc/wsl.conf`:

```ini
[automount]
options = "metadata"
```
Затем выполните `wsl --shutdown` в Windows PowerShell и заново откройте WSL.

## 🌐 Доступ

**⚠️ Замените `localhost` на ваш домен или IP-адрес сервера!**

- **Web приложение**: http://YOUR_DOMAIN_OR_IP:3000
- **API**: http://YOUR_DOMAIN_OR_IP:8000/api/v1/
- **Админ панель**: http://YOUR_DOMAIN_OR_IP:8000/admin/
- **Документация API**: http://YOUR_DOMAIN_OR_IP:8000/api/docs/
- **Grafana**: http://YOUR_DOMAIN_OR_IP:3001
- **Prometheus**: http://YOUR_DOMAIN_OR_IP:9090
- **Celery Flower**: http://YOUR_DOMAIN_OR_IP:5555

**Примеры:**
- `http://192.168.1.100:3000` - для локальной сети
- `http://yourdomain.com:3000` - для домена

**Логин**: admin | **Пароль**: admin123

## 🆘 Поддержка

- 📖 [Полное руководство](WORKERNET_PORTAL_GUIDE.md)
- 🐛 [Issues](https://github.com/apelsin349/portal-support-ERP-WorkerNet/issues)
- 📧 support@workernet.com

---

**Лицензия**: MIT | **Версия**: 1.0.0
