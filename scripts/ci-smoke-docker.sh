#!/bin/bash

set -euo pipefail

# Быстрый smoke-тест в Docker окружении (локально или на сервере с Docker)

log() { echo -e "\033[0;34m[INFO]\033[0m $*"; }
ok() { echo -e "\033[0;32m[OK]\033[0m $*"; }
err() { echo -e "\033[0;31m[ERR]\033[0m $*"; }

require() { command -v "$1" >/dev/null 2>&1 || { err "Не найдено: $1"; exit 1; }; }

require docker
docker compose version >/dev/null 2>&1 || alias docker-compose='docker compose'

log "Сборка и запуск сервисов"
docker compose up -d --build

log "Ожидание старта"
sleep 15

log "Миграции"
docker compose exec -T backend python manage.py migrate

log "Health check"
HTTP_CODE=$(curl -s -o /tmp/health.json -w "%{http_code}" http://localhost:8000/health/ || true)
if [ "$HTTP_CODE" != "200" ]; then err "Health=$HTTP_CODE"; cat /tmp/health.json || true; docker compose logs backend | tail -n 200; exit 1; fi
ok "Health: 200"

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

ok "Smoke-тест Docker завершён"

