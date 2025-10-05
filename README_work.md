# Hart Citizens - Кадровая служба королевства

Система поиска и учета подданных в различных королевствах, их отбор через вступительные испытания и оповещение о результатах для последующего зачисления в подданные королей.

## Особенности

- **Django 5.0** с кастомной моделью пользователя
- **UUID** в качестве первичных ключей для всех моделей
- **Django REST Framework** с JWT аутентификацией
- **Swagger/OpenAPI** документация
- **Jinja2** шаблонизатор
- **PostgreSQL** база данных
- **Docker** контейнеризация
- **Логирование** действий с экспортом в Excel
- **Django Admin** для управления данными

## Структура проекта

```
hart_citizens/
├── hart_citizens_project/     # Основные настройки Django
├── users/                     # Приложение пользователей
│   ├── models.py             # Кастомная модель User
│   ├── views.py              # Представления для аутентификации
│   ├── forms.py              # Формы регистрации и входа
│   ├── admin.py              # Админка для пользователей
│   └── api/                  # REST API для пользователей
├── kingdom/                   # Приложение королевства
│   ├── models.py             # Модели Kingdom, King, Citizen, Test, etc.
│   ├── views.py              # Представления для королей и подданных
│   ├── forms.py              # Формы для тестирования
│   ├── admin.py              # Админка с импорт/экспорт
│   ├── api/                  # REST API для королевства
│   ├── utils.py              # Утилиты для логирования
│   └── management/           # Команды управления
├── templates/                # Шаблоны Jinja2
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

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройте базу данных PostgreSQL:**
   - Создайте базу данных `hart_citizens`
   - Обновите настройки в `hart_citizens_project/settings.py` при необходимости

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

## Демо-аккаунты

После выполнения команды `init_data` будут созданы следующие аккаунты:

### Короли:
- `king.north@example.com` (пароль: `king123`)
- `king.golden@example.com` (пароль: `king123`)
- `king.forest@example.com` (пароль: `king123`)

### Подданные:
- `citizen1@example.com` (пароль: `citizen123`)
- `citizen2@example.com` (пароль: `citizen123`)
- `citizen3@example.com` (пароль: `citizen123`)
- `citizen4@example.com` (пароль: `citizen123`)
- `citizen5@example.com` (пароль: `citizen123`)

### Администратор:
- `admin@example.com` (пароль: `admin123`)

## API Endpoints

### Аутентификация
- `POST /api/auth/register/` - Регистрация пользователя
- `POST /api/auth/login/` - Вход пользователя
- `POST /api/auth/logout/` - Выход пользователя
- `POST /api/auth/refresh/` - Обновление JWT токена

### Пользователи
- `GET /api/profile/` - Получение профиля
- `PUT /api/profile/update/` - Обновление профиля

### Королевство
- `GET /api/kingdoms/` - Список королевств
- `GET /api/kings/` - Информация о королях
- `GET /api/citizens/` - Список подданных
- `GET /api/tests/` - Тестовые испытания
- `POST /api/test-attempts/start_test/` - Начало тестирования
- `POST /api/test-attempts/{id}/answer_question/` - Ответ на вопрос
- `POST /api/citizens/{id}/enroll/` - Зачисление подданного
- `GET /api/dashboard/` - Данные для панели управления

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

## Логирование

Система ведет подробные логи всех действий:
- Вход/выход пользователей
- Регистрация новых пользователей
- Прохождение тестирования
- Зачисление подданных
- Все API запросы

Логи доступны в админке и могут быть экспортированы в Excel.

## Технические детали

- **База данных:** PostgreSQL с UUID первичными ключами
- **Аутентификация:** JWT токены с Simple JWT
- **Шаблоны:** Jinja2 с Bootstrap 5
- **API:** Django REST Framework с автоматической документацией
- **Логирование:** Встроенное Django логирование + кастомные логи действий
- **Импорт/экспорт:** django-import-export для админки
- **Контейнеризация:** Docker с PostgreSQL и Redis

## Разработка

### Добавление новых функций:
1. Создайте модели в соответствующих приложениях
2. Добавьте представления и формы
3. Создайте шаблоны
4. Добавьте API endpoints
5. Обновите админку
6. Добавьте тесты

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
