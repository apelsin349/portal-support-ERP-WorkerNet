@echo off
REM Скрипт для компиляции переводов Django в Windows
REM Создает .mo файлы из .po файлов для русской локализации

setlocal enabledelayedexpansion

echo [ИНФО] Компиляция переводов Django...

REM Переход в корень проекта
cd /d "%~dp0.."

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден
    exit /b 1
)

REM Активируем виртуальное окружение если есть
if exist "backend\venv\Scripts\activate.bat" (
    echo [ИНФО] Активируем виртуальное окружение...
    call backend\venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo [ИНФО] Активируем виртуальное окружение...
    call venv\Scripts\activate.bat
)

REM Устанавливаем переменные окружения Django
set DJANGO_SETTINGS_MODULE=backend.config.settings

REM Компилируем переводы
echo [ИНФО] Компилируем переводы для русского языка...
python backend\manage.py compilemessages -l ru

REM Проверяем результат
if exist "backend\locale\ru\LC_MESSAGES\django.mo" (
    echo [УСПЕХ] Переводы успешно скомпилированы!
    echo [ИНФО] Файл: backend\locale\ru\LC_MESSAGES\django.mo
) else (
    echo [ОШИБКА] Ошибка компиляции переводов
    exit /b 1
)

REM Создаем переводы для английского языка (базовый)
echo [ИНФО] Создаем базовые переводы для английского языка...
if not exist "backend\locale\en\LC_MESSAGES" mkdir "backend\locale\en\LC_MESSAGES"

REM Копируем .po файл для английского языка
if exist "backend\locale\ru\LC_MESSAGES\django.po" (
    copy "backend\locale\ru\LC_MESSAGES\django.po" "backend\locale\en\LC_MESSAGES\django.po" >nul
    python backend\manage.py compilemessages -l en
    echo [УСПЕХ] Базовые переводы для английского языка созданы!
)

echo [УСПЕХ] Все переводы готовы!
echo [ИНФО] Для применения изменений перезапустите Django сервер

pause
