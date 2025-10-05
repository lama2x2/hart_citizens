# Hart Citizens - Кадровая служба королевства

Система поиска и учета подданных в различных королевствах, их отбор через вступительные испытания и оповещение о результатах для последующего зачисления в подданные королей.

## Особенности

- **Django 5.0** с кастомной моделью пользователя (username-based)
- **UUID** в качестве первичных ключей для всех моделей
- **Django REST Framework** с JWT аутентификацией
- **Swagger/OpenAPI** документация
- **Jinja2** шаблонизатор
- **PostgreSQL** база данных
- **Docker** контейнеризация
- **Логирование** действий с экспортом в Excel
- **Django Admin** для управления данными
- **Переменные окружения** через .env файл

## Структура проекта

```
hart_citizens/
├── hart_citizens_project/     # Основные настройки Django
├── users/                     # Приложение пользователей
│   ├── models.py             # Кастомная модель User
│   ├── views.py              # Представления для аутентификации
│   ├── forms.py              # Формы регистрации и входа
│   ├── admin.py              # Админка для пользователей
│   ├── resources.py           # Ресурсы для импорт/экспорт
│   └── api/                  # REST API для пользователей
├── kingdom/                   # Приложение королевства
│   ├── models.py             # Модели Kingdom, King, Citizen, Test, etc.
│   ├── views.py              # Представления для королей и подданных
│   ├── forms.py              # Формы для тестирования
│   ├── admin.py              # Админка с импорт/экспорт
│   ├── resources.py           # Ресурсы для импорт/экспорт
│   ├── api/                  # REST API для королевства
│   ├── utils.py              # Утилиты для логирования
│   └── management/           # Команды управления
├── action_logs/              # Приложение логирования действий
│   ├── models.py             # Модель ActionLog
│   ├── views.py              # Представления для логов
│   ├── admin.py              # Админка для логов
│   ├── resources.py           # Ресурсы для импорт/экспорт
│   ├── utils.py              # Утилиты экспорта в Excel
│   └── api/                  # REST API для логов
├── api/                      # Общие API модули
│   ├── users/                # API пользователей
│   ├── kingdom/              # API королевства
│   └── action_logs/          # API логов
├── templates/                # Шаблоны Django
├── static/                   # Статические файлы
├── logs/                     # Логи приложения
├── requirements.txt          # Зависимости Python
├── docker-compose.yml       # Docker Compose конфигурация
├── Dockerfile               # Docker образ
└── manage.py                # Django управление
```

## Установка и запуск

### Локальная разработка

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd hart_citizens
   ```

2. **Создайте виртуальное окружение:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate     # Windows
   ```

3. **Настройте переменные окружения:**
   ```bash
   cp .env.example .env
   # Отредактируйте .env файл под ваши настройки
   ```

4. **Настройте базу данных PostgreSQL:**
   - Создайте базу данных `hart_citizens`
   - Обновите настройки в `.env` файле при необходимости

5. **Выполните миграции:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Создайте начальные данные:**
   ```bash
   python manage.py init_data
   ```

7. **Создайте суперпользователя:**
   ```bash
   python manage.py createsuperuser
   ```

8. **Запустите сервер разработки:**
   ```bash
   python manage.py runserver
   ```

### Docker

1. **Запустите с Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Выполните миграции:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Создайте начальные данные:**
   ```bash
   docker-compose exec web python manage.py init_data
   ```

## Доступ к приложению

- **Веб-интерфейс:** http://localhost:8000
- **Админка:** http://localhost:8000/admin
- **API документация:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **JWT токены:** http://localhost:8000/api/token/

## Демо-аккаунты

После выполнения команды `init_data` будут созданы следующие аккаунты:

### Короли:
- `king_north` (пароль: `king123`)
- `king_golden` (пароль: `king123`)
- `king_forest` (пароль: `king123`)

### Подданные:
- `citizen_anna` (пароль: `citizen123`)
- `citizen_boris` (пароль: `citizen123`)
- `citizen_victoria` (пароль: `citizen123`)
- `citizen_grigory` (пароль: `citizen123`)
- `citizen_darya` (пароль: `citizen123`)

### Администратор:
- `admin` (пароль: `admin123`)

## API Endpoints

API полностью функционален и доступен через Swagger UI.

### Аутентификация
- `POST /api/token/` - Получение JWT токена (username + password)
- `POST /api/token/refresh/` - Обновление JWT токена
- `POST /api/users/auth/register/` - Регистрация пользователя
- `POST /api/users/auth/login/` - Вход пользователя
- `POST /api/users/auth/logout/` - Выход пользователя

### Пользователи
- `GET /api/users/profile/` - Получение профиля
- `PUT /api/users/profile/update/` - Обновление профиля

### Королевство
- `GET /api/kingdom/kingdoms/` - Список королевств
- `GET /api/kingdom/kings/` - Информация о королях
- `GET /api/kingdom/citizens/` - Список подданных
- `GET /api/kingdom/tests/` - Тестовые испытания
- `POST /api/kingdom/test-attempts/` - Начало тестирования
- `POST /api/kingdom/citizens/{id}/enroll/` - Зачисление подданного
- `GET /api/kingdom/dashboard/` - Данные для панели управления

### Логи действий
- `GET /api/action-logs/logs/` - Список логов действий
- `GET /api/action-logs/logs/export/` - Экспорт логов в Excel

## Функциональность

### Для подданных:
- Регистрация с выбором королевства
- Прохождение тестового испытания
- Просмотр статуса зачисления
- Просмотр результатов тестирования

### Для королей:
- Просмотр кандидатов на зачисление
- Просмотр ответов подданных на тесты
- Зачисление подданных (с ограничением по количеству)
- Управление лимитом подданных

### Для администраторов:
- Управление королевствами через админку
- Создание и редактирование тестовых испытаний
- Просмотр логов действий
- Экспорт логов в Excel
- Управление пользователями
- **Импорт/экспорт данных** через отдельные файлы resources.py

## Структура импорт/экспорт

Проект использует django-import-export с отдельными файлами resources.py для каждого приложения:

- **`action_logs/resources.py`** - ресурсы для экспорта логов действий
- **`kingdom/resources.py`** - ресурсы для всех моделей королевства (Kingdom, King, Citizen, Test, Question, TestAttempt, Answer)
- **`users/resources.py`** - ресурсы для экспорта пользователей

Все админ-классы наследуются от `ImportExportModelAdmin` и связаны с соответствующими ресурсами.

## Логирование

Система ведет подробные логи всех действий через отдельное приложение `action_logs`:
- Вход/выход пользователей
- Регистрация новых пользователей
- Прохождение тестирования
- Зачисление подданных
- Все API запросы

Логи доступны в админке и могут быть экспортированы в Excel через `ActionLogResource`.

## Технические детали

- **База данных:** PostgreSQL с UUID первичными ключами
- **Аутентификация:** JWT токены с Simple JWT (username-based)
- **Шаблоны:** Django Templates с Bootstrap 5
- **API:** Django REST Framework с автоматической документацией (Swagger/OpenAPI)
- **Логирование:** Встроенное Django логирование + кастомные логи действий
- **Импорт/экспорт:** django-import-export для админки с отдельными файлами resources.py
- **Контейнеризация:** Docker с PostgreSQL и Redis
- **Приложения:** users, kingdom, action_logs (отдельное приложение для логов)

## Переменные окружения

Проект использует `.env` файл для конфигурации. Создайте `.env` файл на основе `.env.example`:

```env
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Settings (для Docker)
DB_NAME=hart_citizens
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Redis Settings
REDIS_URL=redis://redis:6379/0

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## Разработка

### Добавление новых функций:
1. Создайте модели в соответствующих приложениях
2. Добавьте представления и формы
3. Создайте шаблоны
4. Добавьте API endpoints
5. Обновите админку
6. Добавьте ресурсы для импорт/экспорт в resources.py
7. Добавьте тесты

### Тестирование:
```bash
python manage.py test
```

### Сбор статических файлов:
```bash
python manage.py collectstatic
```

## Лицензия

MIT License
