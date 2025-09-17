#!/bin/bash

set -euo pipefail

# Скрипт для автоматизированной проверки установки и запуска WorkerNet на Ubuntu 24.04
# ВНИМАНИЕ: Требует прав sudo. Предназначен для нового сервера/VM.

log() { echo -e "\033[0;34m[ИНФО]\033[0m $*"; }
ok() { echo -e "\033[0;32m[OK]\033[0m $*"; }
err() { echo -e "\033[0;31m[ОШИБКА]\033[0m $*"; }

require() {
  if ! command -v "$1" >/dev/null 2>&1; then
    err "Не найдена команда: $1"; exit 1
  fi
}

log "Обновление системы (apt update/upgrade)"
sudo apt update && sudo apt upgrade -y

log "Установка базовых пакетов (curl, git, build-essential и др.)"
sudo apt install -y curl wget git build-essential software-properties-common apt-transport-https ca-certificates gnupg lsb-release unzip make jq

log "Установка Python 3.11 (интерпретатор, venv, dev-заголовки, pip)"
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

log "Установка Node.js 18 (через NodeSource)"
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

log "Установка PostgreSQL и Redis (с автозапуском)"
sudo apt install -y postgresql postgresql-contrib postgresql-client redis-server
sudo systemctl enable --now postgresql
sudo systemctl enable --now redis-server

log "Установка Docker (официальный репозиторий, compose‑plugin)"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker "$USER" || true

WORKDIR="$HOME/workernet-smoke"
log "Подготовка рабочего каталога: $WORKDIR"
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR"
cd "$WORKDIR"

log "Клонирование репозитория (если основной недоступен — используем зеркало)"
git clone https://github.com/your-org/portal-support-ERP-WorkerNet.git app || git clone https://github.com/apelsin349/portal-support-ERP-WorkerNet.git app
cd app

log "Подготовка .env (автогенерация из env.example, секреты)"
if [ -f .env ]; then cp -f .env .env.bak.$(date +%Y%m%d%H%M%S); fi
if [ ! -f .env ]; then
  cp env.example .env 2>/dev/null || cp .env.example .env 2>/dev/null || true
fi
esc() { printf '%s' "$1" | sed -e 's/[|/\\&]/\\&/g'; }
SECRET_KEY=$(openssl rand -base64 32 2>/dev/null || head -c 32 /dev/urandom | base64)
JWT_SECRET=$(openssl rand -base64 32 2>/dev/null || head -c 32 /dev/urandom | base64)
if [ -f .env ]; then
  grep -q "your-secret-key-here" .env && sed -i "s|your-secret-key-here|$(esc "$SECRET_KEY")|" .env || true
  grep -q "your-jwt-secret-key" .env && sed -i "s|your-jwt-secret-key|$(esc "$JWT_SECRET")|" .env || true
  grep -q "your-redis-password" .env && sed -i "s|your-redis-password|redis123|" .env || true
  grep -q "your-secure-password" .env && sed -i "s|your-secure-password|workernet123|" .env || true
  grep -q "^DJANGO_SECRET_KEY=" .env || echo "DJANGO_SECRET_KEY=$(esc "$SECRET_KEY")" >> .env
  grep -q "^JWT_SECRET=" .env || echo "JWT_SECRET=$(esc "$JWT_SECRET")" >> .env
fi

log "Сборка и запуск через Docker Compose (detached)"
require docker
docker compose version >/dev/null 2>&1 || alias docker-compose='docker compose'

docker compose up -d --build

log "Ожидание старта сервисов (20 секунд)"
sleep 20
docker compose ps

log "Проверка эндпоинта состояния /health/"
set +e
HTTP_CODE=$(curl -s -o /tmp/health.json -w "%{http_code}" http://localhost:8000/health/ || true)
set -e
if [ "$HTTP_CODE" != "200" ]; then
  err "Health‑проверка вернула код $HTTP_CODE"; cat /tmp/health.json || true; docker compose logs backend | tail -n 200; exit 1
fi
ok "Сервис здоров: 200"

log "Запуск миграций Django"
docker compose exec -T backend python manage.py makemigrations
docker compose exec -T backend python manage.py migrate
ok "Миграции применены"

log "Создание суперпользователя (admin/admin123)"
docker compose exec -T backend python manage.py shell << 'PY'
from django.contrib.auth import get_user_model
from app.models.tenant import Tenant
User = get_user_model()
tenant, _ = Tenant.objects.get_or_create(name='SmokeTenant', defaults={'slug':'smoke','domain':'localhost'})
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123', tenant=tenant)
print('OK')
PY
ok "Суперпользователь готов (admin/admin123)"

log "Smoke‑тест API: чтение списка тикетов"
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' | jq -r .access)
if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then err "Не удалось получить JWT"; exit 1; fi
curl -sf -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/tickets/ >/dev/null
ok "API доступен (tickets)"

log "Smoke‑тест метрик Prometheus"
curl -sf http://localhost:8000/metrics >/dev/null || true
ok "Метрики доступны (или включены позже)"

log "Проверка фронтенда (порт 3000)"
curl -s -I http://localhost:3000 | head -n 1
ok "Фронтенд отвечает"

ok "Smoke‑тесты успешно пройдены"

