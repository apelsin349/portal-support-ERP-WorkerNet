# 🌐 Настройка домена или IP-адреса

## ⚠️ Важно!

По умолчанию WorkerNet Portal настроен для работы с `localhost`. Для доступа извне необходимо указать ваш домен или IP-адрес.

## 🚀 Быстрая настройка

### 1. Для Docker развертывания

```bash
# Установить переменную окружения и запустить
DOMAIN_OR_IP=192.168.1.100 docker compose up -d

# Или создать файл .env
echo "DOMAIN_OR_IP=192.168.1.100" > .env
docker compose up -d
```

### 2. Для Ubuntu установки

```bash
# Установить переменную и запустить скрипт
WORKERNET_DOMAIN_OR_IP=192.168.1.100 ./scripts/universal-install-update.sh

# Или экспортировать переменную
export WORKERNET_DOMAIN_OR_IP=192.168.1.100
./scripts/universal-install-update.sh
```

### 3. Ручная настройка

```bash
# В файле .env измените:
DOMAIN_OR_IP=192.168.1.100

# В файле backend/.env измените:
ALLOWED_HOSTS=192.168.1.100,127.0.0.1,0.0.0.0
```

## 📋 Примеры конфигурации

### Локальная сеть
```bash
# IP-адрес сервера в локальной сети
DOMAIN_OR_IP=192.168.1.100

# Доступ:
# http://192.168.1.100:3000 - Frontend
# http://192.168.1.100:8000 - API
```

### Домен с поддоменом
```bash
# Поддомен для портала
DOMAIN_OR_IP=portal.yourdomain.com

# Доступ:
# https://portal.yourdomain.com - Frontend (с Nginx)
# https://portal.yourdomain.com/api - API
```

### Основной домен
```bash
# Основной домен
DOMAIN_OR_IP=yourdomain.com

# Доступ:
# https://yourdomain.com - Frontend
# https://yourdomain.com/api - API
```

## 🔧 Настройка Nginx для домена

### 1. Создать конфигурацию Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Настроить SSL с Let's Encrypt

```bash
# Установить Certbot
sudo apt install certbot python3-certbot-nginx

# Получить сертификат
sudo certbot --nginx -d yourdomain.com

# Автоматическое обновление
sudo crontab -e
# Добавить: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔍 Проверка настройки

### 1. Проверить доступность

```bash
# Проверить Frontend
curl -I http://YOUR_DOMAIN_OR_IP:3000

# Проверить API
curl -I http://YOUR_DOMAIN_OR_IP:8000/api/

# Проверить через домен (с Nginx)
curl -I http://yourdomain.com
```

### 2. Проверить переменные окружения

```bash
# В Docker
docker exec workernet_backend env | grep ALLOWED_HOSTS

# В Ubuntu
systemctl show workernet-backend | grep Environment
```

## 🚨 Частые проблемы

### 1. CORS ошибки
```bash
# Убедитесь, что CORS настроен правильно
CORS_ALLOWED_ORIGINS=http://YOUR_DOMAIN_OR_IP:3000
```

### 2. CSRF ошибки
```bash
# Добавьте домен в CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS=http://YOUR_DOMAIN_OR_IP:3000
```

### 3. ALLOWED_HOSTS ошибки
```bash
# Убедитесь, что домен в ALLOWED_HOSTS
ALLOWED_HOSTS=YOUR_DOMAIN_OR_IP,127.0.0.1,0.0.0.0
```

## 📚 Дополнительные ресурсы

- [Docker Environment Variables](https://docs.docker.com/compose/environment-variables/)
- [Django ALLOWED_HOSTS](https://docs.djangoproject.com/en/stable/ref/settings/#allowed-hosts)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

---

**Успешной настройки! 🚀**
