# 🔧 Руководство по исправлению проблем с миграциями Django

## 🚨 Проблема

Ошибка: `NodeNotFoundError: Migration app.0008_agentrating_incident_incidentattachment_and_more dependencies reference nonexistent parent node ('app', '0007_add_user_reset_tokens')`

## 🔍 Причина

Django пытается найти миграцию `0007_add_user_reset_tokens`, которая должна быть родительской для миграции `0008_agentrating_incident_incidentattachment_and_more`, но эта миграция **отсутствует** в файловой системе.

## ✅ Решение

### Вариант 1: Быстрое исправление (Рекомендуется)

**Для Ubuntu:**
```bash
./scripts/quick-migration-fix.sh
```

### Вариант 2: Полное исправление

**Для Ubuntu:**
```bash
./scripts/fix-migration-dependencies.sh
```

### Вариант 3: Ubuntu-специфичное исправление

**Для Ubuntu:**
```bash
./scripts/ubuntu-migration-fix.sh
```

### Вариант 4: Ручное исправление

1. **Очистите проблемные записи миграций:**
```bash
cd backend
python manage.py dbshell -c "DELETE FROM django_migrations WHERE app = 'app' AND name != '0001_initial';"
```

2. **Сбросьте состояние миграций:**
```bash
python manage.py migrate app 0001 --fake
```

3. **Создайте новые миграции:**
```bash
python manage.py makemigrations app
```

4. **Примените миграции:**
```bash
python manage.py migrate
```

5. **Проверьте состояние:**
```bash
python manage.py showmigrations app
```

## 🔄 Что происходит при исправлении

1. **Очистка базы данных:** Удаляются все записи о миграциях приложения `app`, кроме базовой `0001_initial`
2. **Сброс состояния:** Django помечает базовую миграцию как выполненную
3. **Создание новых миграций:** Django анализирует текущие модели и создает новые миграции
4. **Применение миграций:** Новые миграции применяются к базе данных

## ⚠️ Важные замечания

- **Резервное копирование:** Перед исправлением сделайте резервную копию базы данных
- **Тестирование:** После исправления протестируйте работу приложения
- **Мониторинг:** Следите за логами на предмет ошибок

## 🚀 После исправления

1. Проверьте, что все миграции применены:
```bash
python manage.py showmigrations app
```

2. Убедитесь, что приложение запускается:
```bash
python manage.py runserver
```

3. Проверьте API endpoints:
```bash
python manage.py check
```

## 📞 Поддержка

Если проблемы продолжаются, проверьте:
- Версию Django
- Состояние базы данных
- Логи приложения
- Конфигурацию базы данных в `settings.py`
