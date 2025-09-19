@echo off
REM Check Dependencies Script for WorkerNet Portal (Windows)
REM Проверяет актуальность и безопасность зависимостей

echo 🔍 Проверка зависимостей WorkerNet Portal...

REM Check if we're in the right directory
if not exist "requirements.txt" (
    echo ❌ Файл requirements.txt не найден. Запустите скрипт из корня проекта.
    pause
    exit /b 1
)

REM Backend dependencies check
echo 📦 Проверка Python зависимостей...

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo ⚠️  Виртуальная среда не активирована. Активируем...
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
    ) else (
        echo ❌ Виртуальная среда не найдена. Создайте её командой: python -m venv venv
        pause
        exit /b 1
    )
)

REM Install checking tools
echo 📋 Установка инструментов для проверки...
pip install --quiet pip-audit safety

REM Check for outdated packages
echo 🔄 Проверка устаревших пакетов...
pip list --outdated --format=freeze | findstr /R ".*" | head -20 || echo Нет устаревших пакетов

REM Security audit
echo 🔒 Проверка безопасности...
pip-audit --desc --fix-dry-run || echo ⚠️  Найдены уязвимости в зависимостях
safety check --json --output safety-report.json || echo ⚠️  Найдены уязвимости в зависимостях

REM Check frontend dependencies
if exist "frontend\package.json" (
    echo 📦 Проверка Node.js зависимостей...
    cd frontend
    
    if not exist "node_modules" (
        echo 📥 Установка npm зависимостей...
        npm install
    )
    
    echo 🔒 Аудит npm пакетов...
    npm audit --audit-level=moderate || echo ⚠️  Найдены уязвимости в npm пакетах
    
    echo 🔄 Проверка устаревших npm пакетов...
    npm outdated || echo Нет устаревших пакетов
    
    cd ..
)

REM Check Docker configuration
if exist "docker-compose.yml" (
    echo 🐳 Проверка Docker конфигурации...
    docker-compose config --quiet && echo ✅ Docker Compose конфигурация корректна || echo ❌ Ошибки в Docker Compose конфигурации
)

echo ✅ Проверка завершена!
echo 📄 Проверьте dependency-report.md для подробностей
echo 🔧 Рекомендации:
echo 1. Регулярно обновляйте зависимости
echo 2. Следите за уведомлениями о безопасности
echo 3. Тестируйте обновления в dev/staging среде

pause
