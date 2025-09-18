@echo off
REM Скрипт для исправления проблем с npm зависимостями в Windows
REM Удаляет старые lock файлы и пересоздает их

setlocal enabledelayedexpansion

echo [ИНФО] Исправление проблем с npm зависимостями...

REM Переход в корень проекта
cd /d "%~dp0.."

REM Проверяем наличие Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Node.js не найден. Установите Node.js 18+ и повторите попытку.
    exit /b 1
)

echo [ИНФО] Версия Node.js: 
node --version
echo [ИНФО] Версия npm: 
npm --version

REM Очищаем npm кэш
echo [ИНФО] Очищаем npm кэш...
npm cache clean --force >nul 2>&1

REM Настраиваем npm для работы без прокси
echo [ИНФО] Настраиваем npm...
npm config set registry https://registry.npmjs.org/ >nul 2>&1
npm config delete proxy >nul 2>&1
npm config delete https-proxy >nul 2>&1
npm config set strict-ssl true >nul 2>&1

REM Обрабатываем frontend
if exist "frontend" (
    echo [ИНФО] Обрабатываем frontend...
    cd frontend
    
    REM Удаляем старые lock файлы
    if exist "package-lock.json" (
        echo [ИНФО] Удаляем старый package-lock.json...
        del /f /q package-lock.json >nul 2>&1
    )
    
    if exist "node_modules" (
        echo [ИНФО] Удаляем node_modules...
        rmdir /s /q node_modules >nul 2>&1
    )
    
    REM Устанавливаем зависимости
    echo [ИНФО] Устанавливаем зависимости frontend...
    npm install --no-optional --no-audit --no-fund
    if errorlevel 1 (
        echo [ВНИМАНИЕ] Не удалось установить зависимости frontend. Продолжаем...
    ) else (
        echo [УСПЕХ] Зависимости frontend установлены успешно!
    )
    
    cd ..
) else (
    echo [ВНИМАНИЕ] Каталог frontend не найден
)

REM Обрабатываем корневой package.json (если есть)
if exist "package.json" (
    echo [ИНФО] Обрабатываем корневой package.json...
    
    REM Удаляем старые lock файлы
    if exist "package-lock.json" (
        echo [ИНФО] Удаляем старый корневой package-lock.json...
        del /f /q package-lock.json >nul 2>&1
    )
    
    if exist "node_modules" (
        echo [ИНФО] Удаляем корневые node_modules...
        rmdir /s /q node_modules >nul 2>&1
    )
    
    REM Устанавливаем зависимости
    echo [ИНФО] Устанавливаем корневые зависимости...
    npm install --no-optional --no-audit --no-fund
    if errorlevel 1 (
        echo [ВНИМАНИЕ] Не удалось установить корневые зависимости. Продолжаем...
    ) else (
        echo [УСПЕХ] Корневые зависимости установлены успешно!
    )
)

echo [УСПЕХ] Исправление npm зависимостей завершено!
echo [ИНФО] Теперь можно запустить установку заново.

pause
