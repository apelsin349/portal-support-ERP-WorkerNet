# 🔧 Устранение проблем с npm

## Проблема: npm ci не может установить пакеты

### Симптомы
```
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync.
npm error Missing: express@4.21.2 from lock file
```

### Причины
1. **Несинхронизированные файлы** - `package.json` и `package-lock.json` не соответствуют друг другу
2. **Отсутствие прокси** - проблемы с сетевым подключением к npm реестрам
3. **Поврежденный кэш** - npm кэш содержит устаревшие данные

## 🚀 Решения

### 1. Быстрое решение (рекомендуется)

Запустите скрипт исправления:

**Linux/macOS:**
```bash
chmod +x scripts/fix-npm-deps.sh
./scripts/fix-npm-deps.sh
```

**Windows:**
```cmd
scripts\fix-npm-deps.bat
```

### 2. Ручное исправление

#### Шаг 1: Очистка
```bash
# Перейти в каталог frontend
cd frontend

# Удалить старые файлы
rm -f package-lock.json
rm -rf node_modules

# Очистить npm кэш
npm cache clean --force
```

#### Шаг 2: Настройка npm
```bash
# Настроить реестр
npm config set registry https://registry.npmjs.org/

# Удалить настройки прокси (если есть)
npm config delete proxy
npm config delete https-proxy

# Включить строгую проверку SSL
npm config set strict-ssl true
```

#### Шаг 3: Установка зависимостей
```bash
# Установить зависимости
npm install --no-optional --no-audit --no-fund
```

### 3. Альтернативные реестры

Если основной реестр недоступен, попробуйте альтернативные:

```bash
# Китайский реестр
npm config set registry https://registry.npmmirror.com/

# Или временно
npm install --registry https://registry.npmmirror.com/
```

### 4. Работа за прокси

Если вы за корпоративным прокси:

```bash
# Настроить прокси
npm config set proxy http://proxy.company.com:8080
npm config set https-proxy http://proxy.company.com:8080

# Или через переменные окружения
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

## 🔍 Диагностика

### Проверка конфигурации npm
```bash
# Показать текущую конфигурацию
npm config list

# Проверить реестр
npm config get registry

# Проверить прокси
npm config get proxy
npm config get https-proxy
```

### Проверка сетевого подключения
```bash
# Проверить доступность реестра
curl -I https://registry.npmjs.org/

# Проверить DNS
nslookup registry.npmjs.org
```

### Проверка версий
```bash
# Версия Node.js
node --version

# Версия npm
npm --version

# Проверить совместимость
npm doctor
```

## 📋 Обновленный скрипт установки

Скрипт `scripts/install-ubuntu.sh` был обновлен для решения этих проблем:

1. **Приоритет npm install** - сначала пытается `npm install` для обновления lock файла
2. **Fallback на npm ci** - если `npm install` не сработал, пробует `npm ci`
3. **Множественные реестры** - пробует разные npm реестры
4. **Повторы с задержкой** - делает несколько попыток с увеличивающейся задержкой

## 🛠️ Дополнительные инструменты

### Скрипт исправления зависимостей
- `scripts/fix-npm-deps.sh` - для Linux/macOS
- `scripts/fix-npm-deps.bat` - для Windows

### Функции скрипта:
- Очистка npm кэша
- Удаление старых lock файлов
- Настройка npm без прокси
- Переустановка зависимостей
- Обработка как frontend, так и корневых зависимостей

## ⚠️ Частые проблемы

### 1. Политика выполнения PowerShell (Windows)
```
npm : Невозможно загрузить файл npm.ps1, так как выполнение сценариев отключено
```

**Решение:**
```powershell
# Временно разрешить выполнение скриптов
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Или использовать cmd вместо PowerShell
cmd /c "npm install"
```

### 2. Проблемы с правами доступа
```
EACCES: permission denied, access '/usr/local/lib/node_modules'
```

**Решение:**
```bash
# Использовать nvm для управления версиями Node.js
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
```

### 3. Проблемы с SSL сертификатами
```
npm error SSL Error: UNABLE_TO_VERIFY_LEAF_SIGNATURE
```

**Решение:**
```bash
# Временно отключить проверку SSL (не рекомендуется для продакшена)
npm config set strict-ssl false

# Или обновить сертификаты
npm config set cafile /etc/ssl/certs/ca-certificates.crt
```

## 📚 Полезные ссылки

- [npm Documentation](https://docs.npmjs.com/)
- [npm Configuration](https://docs.npmjs.com/cli/v8/configuring-npm)
- [Troubleshooting npm](https://docs.npmjs.com/troubleshooting)
- [Node.js Installation](https://nodejs.org/en/download/)

## 🎯 Заключение

Проблемы с npm обычно связаны с:
1. Несинхронизированными lock файлами
2. Сетевыми проблемами
3. Неправильной конфигурацией

Используйте предоставленные скрипты для автоматического исправления или следуйте ручным инструкциям для диагностики и решения проблем.
