#!/bin/bash

# WorkerNet Portal Frontend - Быстрый старт
echo "🚀 Запуск WorkerNet Portal Frontend..."

# Проверка Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не установлен. Пожалуйста, установите Node.js 18+"
    exit 1
fi

# Проверка версии Node.js
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Требуется Node.js версии 18 или выше. Текущая версия: $(node -v)"
    exit 1
fi

echo "✅ Node.js версия: $(node -v)"

# Установка зависимостей
echo "📦 Установка зависимостей..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при установке зависимостей"
    exit 1
fi

# Генерация иконок PWA
echo "🎨 Генерация иконок для PWA..."
npm run generate-icons

if [ $? -ne 0 ]; then
    echo "⚠️  Предупреждение: Не удалось сгенерировать иконки PWA"
fi

# Проверка линтера
echo "🔍 Проверка кода..."
npm run lint

if [ $? -ne 0 ]; then
    echo "⚠️  Предупреждение: Найдены ошибки линтера. Запуск 'npm run lint:fix' для исправления..."
    npm run lint:fix
fi

# Сборка проекта
echo "🔨 Сборка проекта..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при сборке проекта"
    exit 1
fi

echo "✅ Проект успешно собран!"

# Запуск в режиме разработки
echo "🚀 Запуск в режиме разработки..."
echo "📱 Откройте http://localhost:3001 в браузере"
echo "🔧 PWA функции доступны в production режиме"
echo "🌐 Для тестирования PWA используйте HTTPS"

npm run dev
