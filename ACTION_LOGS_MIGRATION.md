# Инструкции по миграции ActionLog в отдельное приложение

## Что было сделано:

### 1. Создано новое приложение `action_logs`
- ✅ Создана структура приложения
- ✅ Перенесена модель `ActionLog` из `kingdom.models`
- ✅ Перенесены утилиты логирования из `kingdom.utils`
- ✅ Перенесены views логирования из `kingdom.logs_views`
- ✅ Перенесена админка для логов из `kingdom.admin`
- ✅ Создан API для логов

### 2. Обновлены импорты
- ✅ Обновлены импорты в `kingdom/utils.py`
- ✅ Обновлены импорты в `kingdom/views.py`
- ✅ Обновлены импорты в `kingdom/api/__init__.py`
- ✅ Обновлены импорты в `kingdom/admin.py`
- ✅ Обновлены импорты в `kingdom/context_processors.py`

### 3. Обновлены настройки
- ✅ Добавлено `action_logs` в `INSTALLED_APPS`
- ✅ Обновлены настройки Jazzmin
- ✅ Добавлены URL-ы для нового приложения

### 4. Удалены старые файлы
- ✅ Удален `kingdom/logs_views.py`
- ✅ Удалена модель `ActionLog` из `kingdom/models.py`
- ✅ Удалены `ActionLogResource` и `ActionLogAdmin` из `kingdom/admin.py`
- ✅ Удалены URL-ы логов из `kingdom/urls.py`

## Необходимые действия для завершения миграции:

### 1. Создать миграцию для удаления ActionLog из kingdom
```bash
python manage.py makemigrations kingdom --empty --name remove_actionlog
```

### 2. Отредактировать созданную миграцию
Добавить операцию удаления таблицы action_logs из kingdom:
```python
operations = [
    migrations.RunSQL(
        "DROP TABLE IF EXISTS kingdom_actionlog;",
        reverse_sql="-- Нельзя отменить удаление таблицы"
    ),
]
```

### 3. Применить миграции
```bash
python manage.py migrate action_logs
python manage.py migrate kingdom
```

### 4. Проверить функциональность
- Проверить работу логирования
- Проверить админку
- Проверить API
- Проверить экспорт логов

## Структура нового приложения action_logs:

```
action_logs/
├── __init__.py
├── apps.py
├── models.py          # Модель ActionLog
├── admin.py           # Админка для логов
├── views.py           # Views для логов
├── urls.py            # URL-ы для логов
├── utils.py           # Утилиты логирования
├── tests.py           # Тесты
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py
└── api/
    ├── __init__.py
    ├── views.py       # API ViewSet
    ├── serializers.py # API сериализаторы
    └── urls.py        # API URL-ы
```

## API Endpoints:

- `GET /api/logs/` - Список логов (с фильтрацией)
- `GET /api/logs/{id}/` - Детали лога
- `GET /api/logs/user_logs/` - Логи текущего пользователя
- `GET /api/logs/kingdom_logs/` - Логи королевства
- `GET /api/logs/export/` - Экспорт логов в Excel
- `GET /api/logs/statistics/` - Статистика логов

## URL-ы для шаблонов:

- `/action-logs/dashboard/` - Панель управления логами
- `/action-logs/user/` - Логи пользователя
- `/action-logs/kingdom/` - Логи королевства
- `/action-logs/export/` - Экспорт логов
- `/action-logs/statistics/` - Статистика логов

## Преимущества разделения:

1. **Модульность**: Логирование выделено в отдельное приложение
2. **Переиспользование**: Можно использовать в других проектах
3. **Масштабируемость**: Легче добавлять новые функции логирования
4. **Чистота кода**: Kingdom приложение стало более сфокусированным
5. **Тестирование**: Легче тестировать логирование отдельно

## Проверка работоспособности:

1. Запустить сервер: `python manage.py runserver`
2. Проверить админку: `http://localhost:8000/admin/`
3. Проверить API: `http://localhost:8000/api/docs/`
4. Проверить логирование в действии (вход/выход/регистрация)
5. Проверить экспорт логов

Все функции логирования должны работать как раньше, но теперь они организованы в отдельном приложении!
