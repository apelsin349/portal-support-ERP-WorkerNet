@echo off
chcp 65001 >nul

REM WorkerNet Portal Frontend - Быстрый старт
echo 🚀 Запуск WorkerNet Portal Frontend...

REM Проверка Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js не установлен. Пожалуйста, установите Node.js 18+
    pause
    exit /b 1
)

echo ✅ Node.js версия: 
node --version

REM Установка зависимостей
echo 📦 Установка зависимостей...
call npm install

if %errorlevel% neq 0 (
    echo ❌ Ошибка при установке зависимостей
    pause
    exit /b 1
)

REM Генерация иконок PWA
echo 🎨 Генерация иконок для PWA...
call npm run generate-icons

if %errorlevel% neq 0 (
    echo ⚠️  Предупреждение: Не удалось сгенерировать иконки PWA
)

REM Проверка линтера
echo 🔍 Проверка кода...
call npm run lint

if %errorlevel% neq 0 (
    echo ⚠️  Предупреждение: Найдены ошибки линтера. Запуск 'npm run lint:fix' для исправления...
    call npm run lint:fix
)

REM Сборка проекта
echo 🔨 Сборка проекта...
call npm run build

if %errorlevel% neq 0 (
    echo ❌ Ошибка при сборке проекта
    pause
    exit /b 1
)

echo ✅ Проект успешно собран!

REM Запуск в режиме разработки
echo 🚀 Запуск в режиме разработки...
echo 📱 Откройте http://localhost:3001 в браузере
echo 🔧 PWA функции доступны в production режиме
echo 🌐 Для тестирования PWA используйте HTTPS

call npm run dev
