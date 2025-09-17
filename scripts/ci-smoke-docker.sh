#!/bin/bash

set -euo pipefail

# Быстрый smoke‑тест в Docker‑окружении (локально или на сервере с Docker)

log() { echo -e "\033[0;34m[ИНФО]\033[0m $*"; }
ok() { echo -e "\033[0;32m[OK]\033[0m $*"; }
err() { echo -e "\033[0;31m[ОШИБКА]\033[0m $*"; }

# Проверка наличия команды
require() { command -v "$1" >/dev/null 2>&1 || { err "Не найдена команда: $1"; exit 1; }; }

require docker
docker compose version >/dev/null 2>&1 || alias docker-compose='docker compose'

log "Сборка и запуск сервисов (detached)"
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
docker compose up -d --build

log "Ожидание старта сервисов (15 секунд)"
sleep 15

log "Запуск миграций Django"
docker compose exec -T backend python manage.py migrate

log "Проверка эндпоинта /health/"
HTTP_CODE=$(curl -s -o /tmp/health.json -w "%{http_code}" http://localhost:8000/health/ || true)
if [ "$HTTP_CODE" != "200" ]; then err "Сервис нездоров: $HTTP_CODE"; cat /tmp/health.json || true; docker compose logs backend | tail -n 200; exit 1; fi
ok "Сервис здоров: 200"

log "Генерация токена и тест API"
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' | jq -r .access || true)
if [ -z "${TOKEN:-}" ] || [ "$TOKEN" = "null" ]; then
  ok "JWT пока недоступен (нет суперпользователя) — проверим список без токена (ожидаемо 401)"
  code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/tickets/)
  [ "$code" = "401" ] || { err "Ожидали 401 без токена, получили $code"; exit 1; }
else
  curl -sf -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/tickets/ >/dev/null
  ok "API доступен с JWT"
fi

ok "Smoke‑тест Docker завершён"

