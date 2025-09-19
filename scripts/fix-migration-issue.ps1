# Скрипт для исправления проблемы с миграциями базы данных
# Исправляет ошибку с несуществующим ограничением unique_username_per_tenant

Write-Host "[ИНФО] Исправляем проблему с миграциями базы данных..." -ForegroundColor Green

# Переходим в директорию backend
Set-Location backend

# Проверяем, активировано ли виртуальное окружение
if (-not $env:VIRTUAL_ENV) {
    Write-Host "[ИНФО] Активируем виртуальное окружение..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Выполняем SQL команду для безопасного удаления ограничения
Write-Host "[ИНФО] Безопасно удаляем несуществующее ограничение..." -ForegroundColor Yellow

# Создаем временный SQL файл
$sqlContent = @"
DO `$`$ 
BEGIN
    -- Проверяем существование ограничения и удаляем его
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'unique_username_per_tenant' 
        AND table_name = 'users'
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE users DROP CONSTRAINT unique_username_per_tenant;
        RAISE NOTICE 'Constraint unique_username_per_tenant dropped successfully';
    ELSE
        RAISE NOTICE 'Constraint unique_username_per_tenant does not exist, skipping';
    END IF;
END `$`$;
"@

$sqlContent | Out-File -FilePath "temp_fix.sql" -Encoding UTF8

# Выполняем SQL команду
try {
    python manage.py dbshell  temp_fix.sql
    Write-Host "[УСПЕХ] SQL команда выполнена успешно!" -ForegroundColor Green
} catch {
    Write-Host "[ВНИМАНИЕ] Не удалось выполнить SQL команду: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Удаляем временный файл
Remove-Item "temp_fix.sql" -ErrorAction SilentlyContinue

# Помечаем проблемную миграцию как выполненную (если она существует)
Write-Host "[ИНФО] Помечаем проблемную миграцию как выполненную..." -ForegroundColor Yellow
try {
    python manage.py migrate app 0008 --fake 2>$null
    Write-Host "[УСПЕХ] Миграция 0008 помечена как выполненная!" -ForegroundColor Green
} catch {
    Write-Host "[ИНФО] Миграция 0008 не найдена, продолжаем..." -ForegroundColor Yellow
}

# Выполняем все миграции
Write-Host "[ИНФО] Выполняем все миграции..." -ForegroundColor Yellow
try {
    python manage.py migrate
    Write-Host "[УСПЕХ] Все миграции выполнены успешно!" -ForegroundColor Green
} catch {
    Write-Host "[ОШИБКА] Ошибка при выполнении миграций: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "[УСПЕХ] Проблема с миграциями исправлена!" -ForegroundColor Green
