# 🚀 Развертывание WorkerNet Portal

## Продакшен развертывание

### 1. Подготовка сервера

#### Системные требования
- **OS**: Ubuntu 24.04 LTS (рекомендуется)
- **RAM**: 16+ GB (рекомендуется 32 GB для production)
- **CPU**: 8+ ядер (рекомендуется 16 для production)
- **Диск**: 200+ GB NVMe SSD
- **Сеть**: Статический IP, домен, SSL сертификат
- **Backup**: Автоматическое резервное копирование

#### Установка зависимостей
```bash
# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Установить дополнительные инструменты
sudo apt install -y nginx certbot python3-certbot-nginx ufw fail2ban htop iotop
```

### 2. Настройка домена и SSL

#### Настройка DNS
```bash
# Добавить A-записи в DNS
# yourdomain.com -> YOUR_SERVER_IP
# api.yourdomain.com -> YOUR_SERVER_IP
# admin.yourdomain.com -> YOUR_SERVER_IP
```

#### Получение SSL сертификата
```bash
# Установить Certbot
sudo apt install certbot python3-certbot-nginx

# Получить SSL сертификат
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com -d admin.yourdomain.com
```

### 3. Настройка Nginx

#### Создание конфигурации
```bash
sudo nano /etc/nginx/sites-available/workernet
```

```nginx
# HTTP redirect to HTTPS
server {
    listen 80;
    server_name yourdomain.com api.yourdomain.com admin.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# Main application
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    
    # API routes
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # WebSocket routes
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        alias /var/www/workernet/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/workernet/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# API subdomain
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Admin subdomain
server {
    listen 443 ssl http2;
    server_name admin.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000/admin/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Активация конфигурации
```bash
# Включить сайт
sudo ln -s /etc/nginx/sites-available/workernet /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Настройка файрвола

```bash
# Включить UFW
sudo ufw enable

# Разрешить необходимые порты
sudo ufw allow 22      # SSH
sudo ufw allow 80      # HTTP
sudo ufw allow 443     # HTTPS
sudo ufw allow 3000    # Frontend (временно)
sudo ufw allow 8000    # API (временно)
```

### 5. Развертывание приложения

#### Клонирование и настройка
```bash
# Создать директорию
sudo mkdir -p /var/www/workernet
cd /var/www/workernet

# Клонировать репозиторий
sudo git clone https://github.com/apelsin349/portal-support-ERP-WorkerNet.git .
sudo chown -R $USER:$USER /var/www/workernet

# Настроить переменные окружения
cp env.example .env
nano .env  # Настроить для продакшена
```

#### Продакшен конфигурация
```bash
# В файле .env установить:
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com,admin.yourdomain.com
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://workernet:secure_password@localhost:5432/worker_net
REDIS_URL=redis://:secure_redis_password@localhost:6379/0
EMAIL_HOST=smtp.your-provider.com
EMAIL_HOST_USER=your-email@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password
```

#### Запуск сервисов
```bash
# Запустить через Docker
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Или через systemd
sudo systemctl start workernet-backend workernet-frontend
sudo systemctl enable workernet-backend workernet-frontend
```

### 6. Настройка мониторинга

#### Prometheus
```bash
# Создать конфигурацию
sudo mkdir -p /etc/prometheus
sudo cp config/prometheus.yml /etc/prometheus/
sudo systemctl start prometheus
sudo systemctl enable prometheus
```

#### Grafana
```bash
# Установить Grafana
sudo apt install -y grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# Настроить дашборды
sudo cp -r config/grafana/* /etc/grafana/
sudo systemctl restart grafana-server
```

### 7. Настройка резервного копирования

#### Создание скрипта резервного копирования
```bash
sudo nano /usr/local/bin/workernet-backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backups/workernet"
DATE=$(date +%Y%m%d_%H%M%S)

# Создать директорию
mkdir -p $BACKUP_DIR

# Резервная копия базы данных
pg_dump -U workernet -d worker_net > $BACKUP_DIR/db_$DATE.sql

# Резервная копия файлов
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /var/www/workernet

# Резервная копия конфигурации
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /etc/nginx /etc/prometheus /etc/grafana

# Удалить старые резервные копии (старше 30 дней)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

# Отправить уведомление
echo "Backup completed: $DATE" | mail -s "WorkerNet Backup" admin@yourdomain.com
```

#### Настройка cron
```bash
# Добавить в crontab
sudo crontab -e

# Ежедневное резервное копирование в 2:00
0 2 * * * /usr/local/bin/workernet-backup.sh
```

### 8. Настройка логирования

#### ELK Stack
```bash
# Установить Elasticsearch
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list
sudo apt update
sudo apt install -y elasticsearch

# Установить Logstash
sudo apt install -y logstash

# Установить Kibana
sudo apt install -y kibana

# Запустить сервисы
sudo systemctl start elasticsearch logstash kibana
sudo systemctl enable elasticsearch logstash kibana
```

### 9. Настройка алертинга

#### Создание скрипта алертинга
```bash
sudo nano /usr/local/bin/workernet-alert.sh
```

```bash
#!/bin/bash
# Проверка статуса сервисов
if ! systemctl is-active --quiet workernet-backend; then
    echo "WorkerNet Backend is down!" | mail -s "ALERT: WorkerNet Backend Down" admin@yourdomain.com
fi

if ! systemctl is-active --quiet workernet-frontend; then
    echo "WorkerNet Frontend is down!" | mail -s "ALERT: WorkerNet Frontend Down" admin@yourdomain.com
fi

# Проверка дискового пространства
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Disk usage is ${DISK_USAGE}%" | mail -s "ALERT: High Disk Usage" admin@yourdomain.com
fi
```

### 10. Настройка обновлений

#### Создание скрипта обновления
```bash
sudo nano /usr/local/bin/workernet-update.sh
```

```bash
#!/bin/bash
cd /var/www/workernet

# Создать резервную копию
/usr/local/bin/workernet-backup.sh

# Обновить код
git pull origin main

# Обновить зависимости
docker-compose build --no-cache

# Перезапустить сервисы
docker-compose down
docker-compose up -d

# Выполнить миграции
docker-compose exec backend python manage.py migrate

# Собрать статические файлы
docker-compose exec backend python manage.py collectstatic --noinput

# Перезапустить Nginx
sudo systemctl reload nginx

echo "Update completed successfully"
```

## Масштабирование

### Горизонтальное масштабирование

#### Load Balancer
```bash
# Установить HAProxy
sudo apt install -y haproxy

# Настроить конфигурацию
sudo nano /etc/haproxy/haproxy.cfg
```

```haproxy
global
    daemon
    maxconn 4096

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend workernet_frontend
    bind *:80
    bind *:443 ssl crt /etc/ssl/certs/yourdomain.com.pem
    redirect scheme https if !{ ssl_fc }
    
    default_backend workernet_backend

backend workernet_backend
    balance roundrobin
    server web1 127.0.0.1:3000 check
    server web2 127.0.0.1:3001 check
    server web3 127.0.0.1:3002 check
```

### Вертикальное масштабирование

#### Увеличение ресурсов
```bash
# Увеличить лимиты для Docker
sudo nano /etc/docker/daemon.json
```

```json
{
    "default-ulimits": {
        "memlock": {
            "Hard": -1,
            "Name": "memlock",
            "Soft": -1
        }
    },
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    }
}
```

## Мониторинг производительности

### Настройка метрик
```bash
# Установить Node Exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xvfz node_exporter-1.6.1.linux-amd64.tar.gz
sudo mv node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
sudo useradd --no-create-home --shell /bin/false node_exporter
sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter
sudo systemctl start node_exporter
sudo systemctl enable node_exporter
```

### Настройка алертов
```bash
# Создать правила алертинга
sudo nano /etc/prometheus/alert_rules.yml
```

```yaml
groups:
  - name: workernet_alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
```

## Безопасность

### Настройка fail2ban
```bash
# Установить fail2ban
sudo apt install -y fail2ban

# Настроить для Nginx
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
ignoreip = 127.0.0.1/8 ::1

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3

[apache-auth]
enabled = false

[apache-badbots]
enabled = false

[apache-noscript]
enabled = false

[apache-overflows]
enabled = false
```

### Настройка автоматических обновлений
```bash
# Установить unattended-upgrades
sudo apt install -y unattended-upgrades

# Настроить автоматические обновления
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Резервное копирование и восстановление

### Создание полной резервной копии
```bash
#!/bin/bash
BACKUP_DIR="/backups/workernet-full"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Остановить сервисы
docker-compose down

# Резервная копия базы данных
pg_dump -U workernet -d worker_net > $BACKUP_DIR/db_$DATE.sql

# Резервная копия файлов
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /var/www/workernet

# Резервная копия конфигурации
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /etc/nginx /etc/prometheus /etc/grafana

# Резервная копия Docker volumes
docker run --rm -v workernet_postgres_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/postgres_$DATE.tar.gz -C /data .

# Запустить сервисы
docker-compose up -d

echo "Full backup completed: $DATE"
```

### Восстановление из резервной копии
```bash
#!/bin/bash
BACKUP_DATE=$1
BACKUP_DIR="/backups/workernet-full"

if [ -z "$BACKUP_DATE" ]; then
    echo "Usage: $0 <backup_date>"
    exit 1
fi

# Остановить сервисы
docker-compose down

# Восстановить базу данных
psql -U workernet -d worker_net < $BACKUP_DIR/db_$BACKUP_DATE.sql

# Восстановить файлы
tar -xzf $BACKUP_DIR/files_$BACKUP_DATE.tar.gz -C /

# Восстановить конфигурацию
tar -xzf $BACKUP_DIR/config_$BACKUP_DATE.tar.gz -C /

# Восстановить Docker volumes
docker run --rm -v workernet_postgres_data:/data -v $BACKUP_DIR:/backup alpine tar xzf /backup/postgres_$BACKUP_DATE.tar.gz -C /data

# Запустить сервисы
docker-compose up -d

echo "Restore completed from backup: $BACKUP_DATE"
```

---

## 🎯 Готово!

Ваш WorkerNet Portal развернут в продакшене и готов к работе!

**Следующие шаги:**
1. Настроить мониторинг в Grafana
2. Настроить алерты
3. Настроить резервное копирование
4. Настроить обновления
5. Настроить безопасность

**Нужна помощь?** Обратитесь к документации или создайте issue в репозитории!
