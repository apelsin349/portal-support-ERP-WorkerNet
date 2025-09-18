# 🚨 Экстренное исправление npm проблем

## Проблема: npm зависает с ошибками integrity

### Симптомы
```
npm error code EINTEGRITY
npm error sha512-xxx integrity checksum failed
npm warn tarball tarball data for nodemon@xxx seems to be corrupted
```

### Причины
1. **Поврежденный кэш npm** - файлы в кэше повреждены
2. **Несинхронизированный package-lock.json** - lock файл не соответствует package.json
3. **Сетевые проблемы** - прерванные загрузки повредили файлы

## 🚀 Экстренные решения

### 1. Быстрое решение (рекомендуется)

Запустите экстренный скрипт:

```bash
# Сделать скрипт исполняемым
chmod +x scripts/emergency-npm-reset.sh

# Запустить экстренный сброс
./scripts/emergency-npm-reset.sh
```

### 2. Агрессивное исправление

Если экстренный скрипт не помог:

```bash
# Сделать скрипт исполняемым
chmod +x scripts/force-fix-npm.sh

# Запустить агрессивное исправление
./scripts/force-fix-npm.sh
```

### 3. Ручное исправление

#### Шаг 1: Полная очистка
```bash
# Остановить все процессы npm
pkill -f npm >/dev/null 2>&1 || true

# Удалить ВСЕ кэши npm
npm cache clean --force
rm -rf ~/.npm
rm -rf /tmp/npm-*
rm -rf /tmp/.npm
rm -rf ~/.npm/_cacache
rm -rf ~/.npm/_logs

# Удалить все lock файлы
find . -name "package-lock.json" -delete
find . -name "yarn.lock" -delete
find . -name "pnpm-lock.yaml" -delete

# Удалить все node_modules
find . -name "node_modules" -type d -exec rm -rf {} +
```

#### Шаг 2: Сброс конфигурации npm
```bash
# Сбросить все настройки npm
npm config delete registry
npm config delete proxy
npm config delete https-proxy
npm config delete strict-ssl
npm config delete cafile

# Настроить npm заново
npm config set registry https://registry.npmjs.org/
npm config set strict-ssl true
npm config set fetch-retry-mintimeout 20000
npm config set fetch-retry-maxtimeout 120000
npm config set fetch-retries 3
```

#### Шаг 3: Минимальная установка
```bash
# Перейти в каталог frontend
cd frontend

# Создать минимальный package.json
cat > package.json << 'EOF'
{
  "name": "portal-support-frontend",
  "version": "1.0.0",
  "dependencies": {
    "express": "4.18.2"
  },
  "devDependencies": {
    "nodemon": "3.0.1"
  }
}
EOF

# Установить без lock файла
npm install --no-package-lock --no-audit --no-fund
```

## 🔧 Обновленные скрипты

### 1. Экстренный сброс (`scripts/emergency-npm-reset.sh`)
- Полностью удаляет все кэши npm
- Удаляет все lock файлы
- Удаляет все node_modules
- Сбрасывает конфигурацию npm
- Создает минимальную структуру

### 2. Агрессивное исправление (`scripts/force-fix-npm.sh`)
- Агрессивная очистка кэша
- Множественные стратегии установки
- Упрощение package.json
- Fallback на минимальную установку

### 3. Обновленный скрипт установки
- Проверка целостности кэша
- Агрессивная очистка при проблемах
- 4 стратегии установки:
  1. npm install без lock файла
  2. npm install с принудительным обновлением
  3. npm ci (если lock файл синхронизирован)
  4. Минимальная установка без lock файла

## 📋 Стратегии установки

### Стратегия 1: Без lock файла
```bash
npm install --omit=optional --no-audit --no-fund
```

### Стратегия 2: Принудительное обновление
```bash
npm install --omit=optional --no-audit --no-fund --force
```

### Стратегия 3: Clean install
```bash
npm ci --omit=optional --no-audit --no-fund
```

### Стратегия 4: Минимальная установка
```bash
npm install --omit=optional --no-audit --no-fund --no-package-lock
```

## ⚠️ Предупреждения

### Экстренный сброс удалит:
- ✅ Все кэши npm
- ✅ Все lock файлы
- ✅ Все node_modules
- ✅ Конфигурацию npm

### После сброса:
- npm будет загружать все пакеты заново
- Установка может занять больше времени
- Нужно будет переустановить все зависимости

## 🎯 Рекомендации

### Для предотвращения проблем:
1. **Регулярно очищайте кэш**: `npm cache clean --force`
2. **Не прерывайте установку**: дождитесь завершения
3. **Используйте стабильные версии**: избегайте `^` и `~` в package.json
4. **Проверяйте сеть**: убедитесь в стабильном подключении

### Если проблемы продолжаются:
1. Обновите Node.js до последней LTS версии
2. Переустановите npm: `npm install -g npm@latest`
3. Используйте альтернативные пакетные менеджеры (yarn, pnpm)

## 🚀 Быстрый старт после исправления

```bash
# 1. Запустить экстренный сброс
./scripts/emergency-npm-reset.sh

# 2. Запустить установку заново
./scripts/install-ubuntu.sh

# 3. Если проблемы продолжаются, использовать агрессивное исправление
./scripts/force-fix-npm.sh
```

## 📞 Поддержка

Если ни одно из решений не помогло:
1. Проверьте версию Node.js: `node --version`
2. Проверьте версию npm: `npm --version`
3. Проверьте сетевое подключение: `ping registry.npmjs.org`
4. Попробуйте другой реестр: `npm config set registry https://registry.npmmirror.com/`
