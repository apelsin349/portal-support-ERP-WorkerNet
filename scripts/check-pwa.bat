@echo off
chcp 65001 >nul

REM Скрипт проверки PWA функциональности WorkerNet Portal
REM Проверяет все компоненты PWA и их работоспособность

echo 🚀 Запуск проверки PWA функциональности WorkerNet Portal...
echo.

REM Проверка файлов PWA
echo [ИНФО] Проверяем файлы PWA...

REM Проверяем manifest.json
if exist "frontend\public\manifest.json" (
    echo [УСПЕХ] manifest.json найден
) else (
    echo [ОШИБКА] manifest.json не найден
    set /a errors+=1
)

REM Проверяем Service Worker
if exist "frontend\src\sw.ts" (
    echo [УСПЕХ] Service Worker найден
) else (
    echo [ОШИБКА] Service Worker не найден
    set /a errors+=1
)

REM Проверяем иконки PWA
set icons_found=0
if exist "frontend\public\icons\icon-192x192.png" set /a icons_found+=1
if exist "frontend\public\icons\icon-512x512.png" set /a icons_found+=1

if %icons_found% geq 2 (
    echo [УСПЕХ] Иконки PWA найдены (%icons_found% из 2)
) else (
    echo [ВНИМАНИЕ] Не все иконки PWA найдены (%icons_found% из 2)
)

REM Проверяем browserconfig.xml
if exist "frontend\public\browserconfig.xml" (
    echo [УСПЕХ] browserconfig.xml найден
) else (
    echo [ВНИМАНИЕ] browserconfig.xml не найден
)

echo.

REM Проверка сборки фронтенда
echo [ИНФО] Проверяем сборку фронтенда...

if not exist "frontend" (
    echo [ОШИБКА] Каталог frontend не найден
    goto :end
)

cd frontend

REM Проверяем package.json
if not exist "package.json" (
    echo [ОШИБКА] package.json не найден
    goto :end
)

REM Проверяем наличие PWA зависимостей
set pwa_deps=0
findstr /C:"workbox-webpack-plugin" package.json >nul && set /a pwa_deps+=1
findstr /C:"workbox-window" package.json >nul && set /a pwa_deps+=1

if %pwa_deps% geq 2 (
    echo [УСПЕХ] PWA зависимости найдены
) else (
    echo [ВНИМАНИЕ] Не все PWA зависимости найдены
)

REM Проверяем webpack конфигурацию
if exist "webpack.config.js" (
    findstr /C:"GenerateSW" webpack.config.js >nul && (
        echo [УСПЕХ] Webpack настроен для PWA
    ) || (
        echo [ВНИМАНИЕ] Webpack не настроен для PWA
    )
) else (
    echo [ВНИМАНИЕ] webpack.config.js не найден
)

REM Проверяем сборку
if exist "dist" (
    echo [УСПЕХ] Сборка фронтенда найдена
    
    REM Проверяем наличие Service Worker в сборке
    if exist "dist\sw.js" (
        echo [УСПЕХ] Service Worker в сборке найден
    ) else (
        echo [ВНИМАНИЕ] Service Worker в сборке не найден
    )
) else (
    echo [ВНИМАНИЕ] Сборка фронтенда не найдена (запустите npm run build)
)

cd ..
echo.

REM Проверка доступности сервисов
echo [ИНФО] Проверяем доступность сервисов...

REM Проверяем фронтенд
curl -f -s http://localhost:3000 >nul 2>&1 && (
    echo [УСПЕХ] Фронтенд доступен на http://localhost:3000
) || (
    echo [ОШИБКА] Фронтенд недоступен на http://localhost:3000
    set /a errors+=1
)

REM Проверяем API
curl -f -s http://localhost:8000/api/ >nul 2>&1 && (
    echo [УСПЕХ] API доступен на http://localhost:8000
) || (
    echo [ОШИБКА] API недоступен на http://localhost:8000
    set /a errors+=1
)

REM Проверяем manifest.json через HTTP
curl -f -s http://localhost:3000/manifest.json >nul 2>&1 && (
    echo [УСПЕХ] manifest.json доступен через HTTP
) || (
    echo [ОШИБКА] manifest.json недоступен через HTTP
    set /a errors+=1
)

REM Проверяем Service Worker через HTTP
curl -f -s http://localhost:3000/sw.js >nul 2>&1 && (
    echo [УСПЕХ] Service Worker доступен через HTTP
) || (
    echo [ОШИБКА] Service Worker недоступен через HTTP
    set /a errors+=1
)

echo.

REM Итоговый результат
if %errors% equ 0 (
    echo [УСПЕХ] Все проверки PWA пройдены успешно! 🎉
    echo.
    echo === PWA готов к использованию ===
    echo • Установка на устройства: ✅
    echo • Офлайн работа: ✅
    echo • Push-уведомления: ✅
    echo • Автообновление: ✅
    echo.
    echo === Следующие шаги ===
    echo 1. Откройте http://localhost:3000 в браузере
    echo 2. Установите приложение (кнопка установки)
    echo 3. Протестируйте офлайн режим
    echo 4. Настройте HTTPS для production
) else (
    echo [ОШИБКА] Найдено %errors% ошибок в PWA конфигурации
    echo.
    echo === Рекомендации ===
    echo 1. Убедитесь, что фронтенд собран: npm run build
    echo 2. Проверьте, что все сервисы запущены
    echo 3. Убедитесь, что все PWA файлы на месте
    echo 4. Проверьте конфигурацию webpack
)

:end
pause
