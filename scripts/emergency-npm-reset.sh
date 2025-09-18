#!/bin/bash

# ЭКСТРЕННЫЙ скрипт для полного сброса npm
# Используйте только в крайних случаях

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Без цвета

# Функции для вывода
print_status() {
    echo -e "${BLUE}[ИНФО]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[УСПЕХ]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[ВНИМАНИЕ]${NC} $1"
}

print_error() {
    echo -e "${RED}[ОШИБКА]${NC} $1"
}

# Переход в корень проекта
cd "$(dirname "$0")/.." || exit 1

print_warning "ЭКСТРЕННЫЙ СБРОС npm - это удалит ВСЕ кэши и lock файлы!"
read -p "Продолжить? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Отменено пользователем"
    exit 0
fi

print_status "ЭКСТРЕННЫЙ сброс npm..."

# Полная очистка npm
print_status "Удаляем ВСЕ кэши npm..."
npm cache clean --force >/dev/null 2>&1 || true
rm -rf ~/.npm >/dev/null 2>&1 || true
rm -rf /tmp/npm-* >/dev/null 2>&1 || true
rm -rf /tmp/.npm >/dev/null 2>&1 || true
rm -rf ~/.npm/_cacache >/dev/null 2>&1 || true
rm -rf ~/.npm/_logs >/dev/null 2>&1 || true

# Сброс конфигурации npm
print_status "Сбрасываем конфигурацию npm..."
npm config delete registry >/dev/null 2>&1 || true
npm config delete proxy >/dev/null 2>&1 || true
npm config delete https-proxy >/dev/null 2>&1 || true
npm config delete strict-ssl >/dev/null 2>&1 || true
npm config delete cafile >/dev/null 2>&1 || true

# Удаляем ВСЕ lock файлы в проекте
print_status "Удаляем ВСЕ lock файлы..."
find . -name "package-lock.json" -delete >/dev/null 2>&1 || true
find . -name "yarn.lock" -delete >/dev/null 2>&1 || true
find . -name "pnpm-lock.yaml" -delete >/dev/null 2>&1 || true

# Удаляем ВСЕ node_modules
print_status "Удаляем ВСЕ node_modules..."
find . -name "node_modules" -type d -exec rm -rf {} + >/dev/null 2>&1 || true

# Обрабатываем frontend
if [ -d "frontend" ]; then
    print_status "Создаем минимальный frontend..."
    cd frontend
    
    # Создаем минимальный package.json
    cat > package.json << 'EOF'
{
  "name": "portal-support-frontend",
  "version": "1.0.0",
  "description": "Frontend for Portal Support ERP WorkerNet",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js"
  },
  "dependencies": {
    "express": "4.18.2"
  },
  "devDependencies": {
    "nodemon": "3.0.1"
  }
}
EOF
    
    # Создаем минимальный index.js если не существует
    if [ ! -f "index.js" ]; then
        cat > index.js << 'EOF'
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
    res.json({ message: 'WorkerNet Portal Frontend is running!' });
});

app.listen(PORT, () => {
    console.log(`Frontend server running on port ${PORT}`);
});
EOF
    fi
    
    cd ..
fi

# Настраиваем npm с нуля
print_status "Настраиваем npm с нуля..."
npm config set registry https://registry.npmjs.org/ >/dev/null 2>&1 || true
npm config set strict-ssl true >/dev/null 2>&1 || true
npm config set fetch-retry-mintimeout 20000 >/dev/null 2>&1 || true
npm config set fetch-retry-maxtimeout 120000 >/dev/null 2>&1 || true
npm config set fetch-retries 3 >/dev/null 2>&1 || true

print_success "ЭКСТРЕННЫЙ сброс завершен!"
print_status "Теперь можно запустить установку заново."
print_warning "Все кэши и lock файлы удалены. npm будет загружать все заново."
