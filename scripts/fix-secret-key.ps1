# Скрипт для исправления проблемы с SECRET_KEY (PowerShell версия)
# Использование: .\scripts\fix-secret-key.ps1

param(
    [switch]$Force
)

# Функции для вывода
function Write-Status {
    param([string]$Message)
    Write-Host "[ИНФО] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[УСПЕХ] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[ПРЕДУПРЕЖДЕНИЕ] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ОШИБКА] $Message" -ForegroundColor Red
}

Write-Status "Исправляем проблему с SECRET_KEY..."

# Переходим в корневую директорию проекта
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

# Проверяем, существует ли файл .env
if (-not (Test-Path ".env")) {
    Write-Error "Файл .env не найден!"
    if (Test-Path "env.example") {
        Write-Status "Создаем .env из env.example..."
        Copy-Item "env.example" ".env"
    } else {
        Write-Error "env.example также не найден!"
        exit 1
    }
}

# Генерируем новые секреты
Write-Status "Генерируем новые секреты..."
$SecretKey = -join ((1..50) | ForEach {[char]((65..90) + (97..122) + (48..57) + (33..47) | Get-Random)})
$JwtSecret = -join ((1..50) | ForEach {[char]((65..90) + (97..122) + (48..57) + (33..47) | Get-Random)})

# Читаем содержимое .env файла
$EnvContent = Get-Content ".env"

# Принудительно устанавливаем SECRET_KEY
Write-Status "Устанавливаем SECRET_KEY..."
$EnvContent = $EnvContent | ForEach-Object {
    if ($_ -match "^SECRET_KEY=") {
        "SECRET_KEY=$SecretKey"
    } else {
        $_
    }
}

# Если SECRET_KEY не найден, добавляем его
if (-not ($EnvContent -match "^SECRET_KEY=")) {
    $EnvContent += "SECRET_KEY=$SecretKey"
}

# Принудительно устанавливаем JWT_SECRET_KEY
Write-Status "Устанавливаем JWT_SECRET_KEY..."
$EnvContent = $EnvContent | ForEach-Object {
    if ($_ -match "^JWT_SECRET_KEY=") {
        "JWT_SECRET_KEY=$JwtSecret"
    } else {
        $_
    }
}

# Если JWT_SECRET_KEY не найден, добавляем его
if (-not ($EnvContent -match "^JWT_SECRET_KEY=")) {
    $EnvContent += "JWT_SECRET_KEY=$JwtSecret"
}

# Сохраняем обновленный .env файл
$EnvContent | Set-Content ".env"

# Копируем .env в backend/
Write-Status "Копируем .env в backend/..."
if (Test-Path "backend") {
    Copy-Item ".env" "backend\.env" -Force
    Write-Success ".env скопирован в backend/"
} else {
    Write-Warning "Папка backend/ не найдена"
}

# Проверяем, что SECRET_KEY установлен
$EnvContent = Get-Content ".env"
if ($EnvContent -match "^SECRET_KEY=" -and $EnvContent -notmatch "^SECRET_KEY=$" -and $EnvContent -notmatch "your-secret-key-here") {
    Write-Success "SECRET_KEY успешно установлен"
} else {
    Write-Error "Не удалось установить SECRET_KEY"
    exit 1
}

Write-Success "Проблема с SECRET_KEY исправлена!"
Write-Status "Теперь можно запускать миграции: python manage.py migrate"
