# Руководство по исправлению проблемы с SECRET_KEY

## Проблема
При выполнении миграций Django возникает ошибка:
```
django.core.exceptions.ImproperlyConfigured: Set the SECRET_KEY environment variable
```

## Причина
Файл `.env` содержит плейсхолдеры вместо реальных значений:
- `SECRET_KEY=your-secret-key-here`
- `JWT_SECRET_KEY=your-jwt-secret-key`

## Решение

### Автоматическое исправление (рекомендуется)

1. **В Linux-окружении** выполните:
```bash
cd /home/worker/portal-support-ERP-WorkerNet
bash scripts/fix-secret-key.sh
```

2. **В Windows-окружении** выполните:
```powershell
cd D:\WN\portal-support-ERP-WorkerNet
.\scripts\fix-secret-key.ps1
```

### Ручное исправление

1. **Откройте файл `.env`** в корне проекта

2. **Замените плейсхолдеры** на реальные значения:
```bash
# Генерируем SECRET_KEY
SECRET_KEY=$(openssl rand -base64 32 2>/dev/null || head -c 32 /dev/urandom | base64)

# Генерируем JWT_SECRET_KEY  
JWT_SECRET=$(openssl rand -base64 32 2>/dev/null || head -c 32 /dev/urandom | base64)

# Заменяем в файле .env
sed -i "s|SECRET_KEY=your-secret-key-here|SECRET_KEY=$SECRET_KEY|" .env
sed -i "s|JWT_SECRET_KEY=your-jwt-secret-key|JWT_SECRET_KEY=$JWT_SECRET|" .env
```

3. **Скопируйте файл в backend**:
```bash
cp .env backend/.env
```

### Проверка исправления

После исправления файл `.env` должен содержать:
```
SECRET_KEY=<реальный-сгенерированный-ключ>
JWT_SECRET_KEY=<реальный-сгенерированный-ключ>
```

### Запуск миграций

После исправления можно запустить миграции:
```bash
cd backend
python manage.py migrate
```

## Предотвращение проблемы

Скрипт `universal-install-update.sh` был обновлен для автоматического исправления этой проблемы в будущем. Теперь он:

1. Проверяет наличие плейсхолдеров в файле `.env`
2. Автоматически генерирует новые секреты
3. Заменяет плейсхолдеры на реальные значения
4. Копирует файл `.env` в папку `backend/`

## Дополнительные скрипты

- `scripts/fix-secret-key.sh` - Linux версия скрипта исправления
- `scripts/fix-secret-key.ps1` - Windows версия скрипта исправления

## Примечания

- SECRET_KEY должен быть уникальным для каждого окружения
- Никогда не коммитьте файл `.env` с реальными секретами в Git
- Используйте разные SECRET_KEY для разработки, тестирования и продакшена
