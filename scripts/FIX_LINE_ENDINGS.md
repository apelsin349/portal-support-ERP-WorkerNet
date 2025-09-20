# Исправление окончаний строк в скриптах

## Проблема

При создании скриптов в Windows среда может добавлять символы возврата каретки (`\r`) в окончания строк, что приводит к ошибкам при выполнении в Linux:

```
$'\r': command not found
syntax error near unexpected token `$'{\r''`
```

## Решение

### 1. Автоматическое исправление

```bash
# Удалить все символы \r из файла
tr -d '\r' < universal-install-update.sh > universal-install-update-fixed.sh
mv universal-install-update-fixed.sh universal-install-update.sh

# Или с помощью sed
sed -i 's/\r$//' universal-install-update.sh

# Если установлен dos2unix
dos2unix universal-install-update.sh
```

### 2. Проверка синтаксиса

```bash
# Проверить синтаксис без выполнения
bash -n universal-install-update.sh

# Если ошибок нет - скрипт готов к выполнению
```

### 3. Установка прав доступа

```bash
# Сделать скрипт исполняемым
chmod +x universal-install-update.sh
```

## Профилактика

### В Windows (VS Code)
1. Откройте файл
2. В правом нижнем углу нажмите на "CRLF"
3. Выберите "LF"
4. Сохраните файл

### В Git
```bash
# Настроить Git для автоматического преобразования
git config --global core.autocrlf input

# Для конкретного репозитория
git config core.autocrlf input
```

### В .gitattributes
```
*.sh text eol=lf
*.py text eol=lf
*.md text eol=lf
```

## Проверка окончаний строк

```bash
# Показать окончания строк
cat -A filename.sh

# Проверить тип файла
file filename.sh
```

## Примеры ошибок

### ❌ Неправильно (CRLF)
```
#!/bin/bash\r
set -e\r
```

### ✅ Правильно (LF)
```
#!/bin/bash
set -e
```

---

**Примечание**: Эта проблема часто возникает при работе с файлами, созданными в Windows, на Linux серверах.
