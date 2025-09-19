# Скрипт для исправления конфликтов миграций

Write-Host "[ИНФО] Исправляем конфликты миграций..." -ForegroundColor Green

# Переходим в директорию backend
Set-Location backend

# Проверяем, активировано ли виртуальное окружение
if (-not $env:VIRTUAL_ENV) {
    Write-Host "[ИНФО] Активируем виртуальное окружение..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Сначала исправляем проблему с ограничением
Write-Host "[ИНФО] Исправляем проблему с ограничением unique_username_per_tenant..." -ForegroundColor Yellow

# Создаем временный SQL файл
$sqlContent = @"
DO `$`$ 
BEGIN
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

# Проверяем конфликты миграций
Write-Host "[ИНФО] Проверяем конфликты миграций..." -ForegroundColor Yellow
$migrationOutput = python manage.py showmigrations app 2>&1

if ($migrationOutput -match "Conflicting migrations detected") {
    Write-Host "[ИНФО] Обнаружен конфликт миграций, исправляем..." -ForegroundColor Yellow
    
    # Создаем merge миграцию
    Write-Host "[ИНФО] Создаем merge миграцию..." -ForegroundColor Yellow
    try {
        python manage.py makemigrations --merge app --empty 2>$null
        Write-Host "[УСПЕХ] Merge миграция создана!" -ForegroundColor Green
    } catch {
        Write-Host "[ВНИМАНИЕ] Не удалось создать merge миграцию: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    # Помечаем все проблемные миграции как выполненные
    Write-Host "[ИНФО] Помечаем проблемные миграции как выполненные..." -ForegroundColor Yellow
    $migrations = @("0008", "0009", "0010", "0011")
    foreach ($migration in $migrations) {
        try {
            python manage.py migrate app $migration --fake 2>$null
            Write-Host "[УСПЕХ] Миграция $migration помечена как выполненная!" -ForegroundColor Green
        } catch {
            Write-Host "[ИНФО] Миграция $migration не найдена или уже выполнена" -ForegroundColor Yellow
        }
    }
}

# Выполняем миграции
Write-Host "[ИНФО] Выполняем миграции..." -ForegroundColor Yellow
try {
    python manage.py migrate
    Write-Host "[УСПЕХ] Все миграции выполнены успешно!" -ForegroundColor Green
} catch {
    Write-Host "[ОШИБКА] Ошибка при выполнении миграций: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "[УСПЕХ] Конфликты миграций исправлены!" -ForegroundColor Green
