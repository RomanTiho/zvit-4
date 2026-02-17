# Швидкий Старт Backend

## Що вже створено:

1. ✅ `requirements.txt` - залежності Python
2. ✅ `players_models.py` - моделі для системи рейтингу
3. ✅ `players_serializers.py` - serializers для API
4. ✅ `api-client.js` - клієнт для frontend

## Наступні кроки:

### 1. Встановити залежності

```bash
# Активувати віртуальне середовище (якщо ще не активоване)
venv\Scripts\activate

# Встановити пакети
pip install -r requirements.txt
```

### 2. Інтегрувати моделі в Django

Скопіювати код з `players_models.py` в `my_app/models.py` або створити новий app:

```bash
python manage.py startapp players
```

Потім додати в `my_project/settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'corsheaders',
    'players',
]
```

### 3. Налаштувати CORS

В `my_project/settings.py`:
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ... інші middleware
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
]
```

### 4. Створити міграції

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Запустити сервер

```bash
python manage.py runserver 8001
```

### 6. Підключити API клієнт на frontend

Додати в HTML:
```html
<script src="api-client.js"></script>
```

Використовувати:
```javascript
// Отримати гравців
const players = await PlayersAPI.getPlayers();

// Таблиця лідерів
const leaderboard = await PlayersAPI.getLeaderboard();
```

## Структура файлів

```
d:\diplom\
├── requirements.txt          # Залежності
├── players_models.py         # Моделі гравців
├── players_serializers.py    # Serializers
├── api-client.js            # API клієнт для frontend
├── my_project/              # Django проект
│   └── settings.py
└── my_app/                  # Django app
    └── models.py
```

## Тестування API

Після запуску сервера:
- API: http://localhost:8001/api/
- Admin: http://localhost:8001/admin/

## Проблеми?

Якщо щось не працює:
1. Перевірте чи активоване venv
2. Перевірте чи встановлені всі пакети
3. Перевірте чи запущений сервер на порту 8001
4. Перевірте CORS налаштування
