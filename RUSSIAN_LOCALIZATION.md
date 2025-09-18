# 🇷🇺 Русификация WorkerNet Portal

## Обзор

WorkerNet Portal полностью поддерживает русский язык на всех уровнях: от интерфейса до документации и комментариев в коде.

## 📁 Структура локализации

```
backend/
├── locale/
│   ├── ru/
│   │   └── LC_MESSAGES/
│   │       ├── django.po      # Исходные переводы
│   │       └── django.mo      # Скомпилированные переводы
│   └── en/
│       └── LC_MESSAGES/
│           ├── django.po      # Английские переводы
│           └── django.mo      # Скомпилированные переводы
```

## 🔧 Настройка локализации

### 1. Настройки Django

В файле `backend/config/settings.py` настроена поддержка русского языка:

```python
# Internationalization
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Поддерживаемые языки
LANGUAGES = [
    ('ru', 'Русский'),
    ('en', 'English'),
]

# Пути к файлам локализации
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
```

### 2. Модели данных

Все модели используют систему локализации Django:

```python
from django.utils.translation import gettext_lazy as _

class Ticket(models.Model):
    PRIORITY_CHOICES = [
        ('low', _('Низкий')),
        ('medium', _('Средний')),
        ('high', _('Высокий')),
        ('urgent', _('Срочный')),
        ('critical', _('Критический')),
    ]
    
    STATUS_CHOICES = [
        ('open', _('Открыт')),
        ('in_progress', _('В работе')),
        ('pending', _('Ожидание')),
        ('resolved', _('Решён')),
        ('closed', _('Закрыт')),
        ('cancelled', _('Отменён')),
    ]
```

## 🚀 Компиляция переводов

### Linux/macOS

```bash
# Сделать скрипт исполняемым
chmod +x scripts/compile-translations.sh

# Запустить компиляцию
./scripts/compile-translations.sh
```

### Windows

```cmd
# Запустить bat файл
scripts\compile-translations.bat
```

### Ручная компиляция

```bash
# Активировать виртуальное окружение
source backend/venv/bin/activate  # Linux/macOS
# или
backend\venv\Scripts\activate.bat  # Windows

# Установить переменные окружения
export DJANGO_SETTINGS_MODULE=backend.config.settings

# Скомпилировать переводы
python backend/manage.py compilemessages -l ru
python backend/manage.py compilemessages -l en
```

## 📝 Добавление новых переводов

### 1. В коде Python

```python
from django.utils.translation import gettext_lazy as _

# Для моделей
class MyModel(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Название"))
    description = models.TextField(verbose_name=_("Описание"))

# Для форм
class MyForm(forms.Form):
    title = forms.CharField(label=_("Заголовок"))
    content = forms.CharField(label=_("Содержимое"))

# Для представлений
def my_view(request):
    message = _("Сообщение успешно отправлено")
    return JsonResponse({'message': message})
```

### 2. В шаблонах

```html
{% load i18n %}

<h1>{% trans "Добро пожаловать" %}</h1>
<p>{% trans "Выберите действие" %}</p>

<!-- С переменными -->
<p>{% blocktrans with name=user.name %}Привет, {{ name }}!{% endblocktrans %}</p>
```

### 3. Обновление переводов

```bash
# Извлечь новые строки для перевода
python backend/manage.py makemessages -l ru
python backend/manage.py makemessages -l en

# Отредактировать файлы .po
# backend/locale/ru/LC_MESSAGES/django.po
# backend/locale/en/LC_MESSAGES/django.po

# Скомпилировать переводы
python backend/manage.py compilemessages -l ru
python backend/manage.py compilemessages -l en
```

## 🌐 Frontend локализация

### 1. React компоненты

```typescript
// Создать файл переводов
// frontend/src/locales/ru.json
{
  "common": {
    "save": "Сохранить",
    "cancel": "Отмена",
    "delete": "Удалить",
    "edit": "Редактировать"
  },
  "tickets": {
    "title": "Тикеты",
    "create": "Создать тикет",
    "status": "Статус",
    "priority": "Приоритет"
  }
}

// Использование в компонентах
import { useTranslation } from 'react-i18next';

function TicketList() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('tickets.title')}</h1>
      <button>{t('tickets.create')}</button>
    </div>
  );
}
```

### 2. Настройка i18next

```typescript
// frontend/src/i18n.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import ru from './locales/ru.json';
import en from './locales/en.json';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      ru: { translation: ru },
      en: { translation: en }
    },
    lng: 'ru', // язык по умолчанию
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
```

## 📚 Документация

### 1. README файлы

Все основные README файлы переведены на русский язык:

- `README.md` - Основное техническое задание
- `START_HERE.md` - Быстрый старт
- `README_FULL.md` - Полная документация
- `DEVELOPMENT.md` - Инструкции для разработчиков
- `DEPLOYMENT.md` - Развертывание в продакшене

### 2. Комментарии в коде

Все Python файлы содержат русские комментарии и docstring'и:

```python
"""
Модели тикетов для системы службы поддержки.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

class Ticket(models.Model):
    """Модель тикета службы поддержки."""
    
    # Базовая информация
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    description = models.TextField(verbose_name=_("Описание"))
```

### 3. Скрипты установки

Скрипты установки содержат подробные русские комментарии:

```bash
#!/bin/bash

# Скрипт установки WorkerNet Portal для Ubuntu 24.04 LTS
# Скрипт устанавливает все зависимости и подготавливает WorkerNet Portal

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Без цвета

# Функции для вывода
print_status() {
    echo -e "${BLUE}[ИНФО]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[УСПЕХ]${NC} $1"
}
```

## 🔍 Проверка локализации

### 1. Проверка Django переводов

```bash
# Проверить статус переводов
python backend/manage.py showmigrations

# Проверить загруженные переводы
python backend/manage.py shell
>>> from django.utils.translation import gettext as _
>>> print(_('Низкий'))
```

### 2. Проверка Frontend переводов

```typescript
// В браузере
console.log(i18n.t('common.save')); // "Сохранить"
console.log(i18n.t('tickets.title')); // "Тикеты"
```

## 🛠️ Устранение проблем

### 1. Переводы не отображаются

```bash
# Проверить компиляцию
ls -la backend/locale/ru/LC_MESSAGES/django.mo

# Перекомпилировать
python backend/manage.py compilemessages -l ru
```

### 2. Неправильная кодировка

Убедитесь, что файлы .po сохранены в UTF-8:

```bash
# Проверить кодировку
file backend/locale/ru/LC_MESSAGES/django.po

# Конвертировать в UTF-8
iconv -f windows-1251 -t utf-8 django.po > django_utf8.po
```

### 3. Отсутствующие переводы

```bash
# Найти непереведенные строки
grep -n 'msgstr ""' backend/locale/ru/LC_MESSAGES/django.po

# Обновить переводы
python backend/manage.py makemessages -l ru
```

## 📋 Чек-лист русификации

- [x] Настройки Django для русского языка
- [x] Файлы переводов (.po и .mo)
- [x] Русские комментарии в коде
- [x] Русская документация
- [x] Русские скрипты установки
- [x] Скрипты компиляции переводов
- [x] Проверка кодировки UTF-8
- [x] Тестирование переводов

## 🎯 Заключение

WorkerNet Portal полностью русифицирован и готов к использованию на русском языке. Все компоненты системы поддерживают локализацию, а документация и код содержат подробные русские комментарии для удобства разработки и поддержки.
