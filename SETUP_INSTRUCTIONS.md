# 🚀 Запуск Backend - Інструкції

## ✅ Що вже зроблено:

1. ✅ Оновлено `my_project/settings.py` - додано REST Framework та CORS
2. ✅ Створено моделі в `my_app/models.py` - Player, PlayerStats, PlayerRatingHistory
3. ✅ Створено serializers в `my_app/serializers.py`
4. ✅ Створено views в `my_app/views.py`
5. ✅ Створено URLs в `my_app/urls.py`
6. ✅ Створено admin в `my_app/admin.py`
7. ✅ Оновлено `my_project/urls.py` - підключено API

## 📋 Наступні кроки:

### 1. Встановити залежності (якщо ще не встановлені)

```bash
pip install -r requirements.txt
```

### 2. Створити міграції

```bash
python manage.py makemigrations
```

Очікуваний вивід:
```
Migrations for 'my_app':
  my_app\migrations\0001_initial.py
    - Create model Player
    - Create model PlayerStats
    - Create model PlayerRatingHistory
```

### 3. Застосувати міграції

```bash
python manage.py migrate
```

### 4. Створити суперкористувача (для доступу в admin)

```bash
python manage.py createsuperuser
```

Введіть:
- Username: admin
- Email: admin@example.com
- Password: (ваш пароль)

### 5. Запустити Django сервер

```bash
python manage.py runserver 8001
```

Сервер запуститься на http://localhost:8001

### 6. Перевірити API

Відкрийте в браузері:
- **API Root**: http://localhost:8001/api/
- **Players**: http://localhost:8001/api/players/
- **Leaderboard**: http://localhost:8001/api/players/leaderboard/
- **Admin Panel**: http://localhost:8001/admin/

### 7. Запустити Frontend

В іншому терміналі:

```bash
python serve.py
```

Frontend запуститься на http://localhost:8000

### 8. Тестування

1. Відкрийте http://localhost:8000/players.html
2. Сторінка спробує завантажити гравців з API
3. Якщо гравців немає - створіть їх через admin panel

## 🎯 Створення тестових даних

### Через Admin Panel

1. Перейдіть на http://localhost:8001/admin/
2. Увійдіть як суперкористувач
3. Створіть кількох користувачів (Users)
4. Створіть гравців (Players) для цих користувачів
5. Додайте статистику (Player Stats)

### Через Django Shell

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from my_app.models import Player, PlayerStats
from my_app.services import PlayerRatingService

# Створити користувача
user = User.objects.create_user('player1', 'player1@example.com', 'password')

# Створити гравця
player = Player.objects.create(user=user, position='FWD')

# Додати статистику
stats = PlayerStats.objects.create(
    player=player,
    match_id=1,
    goals=2,
    assists=1,
    yellow_cards=0,
    red_cards=0
)

# Розрахувати рейтинг
PlayerRatingService.calculate_rating(player)

# Перевірити
print(f"Rating: {player.overall_rating}")
```

## 🔧 Troubleshooting

### Помилка: "No module named 'rest_framework'"

```bash
pip install djangorestframework
```

### Помилка: "No module named 'corsheaders'"

```bash
pip install django-cors-headers
```

### API не відповідає

1. Перевірте чи запущений Django сервер на порту 8001
2. Перевірте CORS налаштування в settings.py
3. Перевірте консоль браузера на помилки

### Frontend не може з'єднатися з API

1. Перевірте `api-client.js` - `API_BASE_URL` має бути `http://localhost:8001/api`
2. Перевірте чи обидва сервери запущені
3. Перевірте CORS налаштування

## 📊 API Endpoints

### Players

- `GET /api/players/` - Список всіх гравців
- `GET /api/players/{id}/` - Деталі гравця
- `POST /api/players/` - Створити гравця
- `PUT /api/players/{id}/` - Оновити гравця
- `DELETE /api/players/{id}/` - Видалити гравця

### Custom Actions

- `GET /api/players/leaderboard/` - Таблиця лідерів
  - Query params: `?position=FWD&limit=20`
- `GET /api/players/search/` - Пошук гравців
  - Query params: `?q=Іван&position=MID&min_rating=7.5`
- `GET /api/players/{id}/rating_history/` - Історія рейтингу
- `POST /api/players/{id}/update_stats/` - Оновити статистику

### Player Stats

- `GET /api/player-stats/` - Вся статистика
  - Query params: `?player_id=1&match_id=5`
- `POST /api/player-stats/` - Додати статистику

## ✅ Готово!

Тепер у вас працює:
- ✅ Django Backend з REST API
- ✅ Frontend з інтеграцією API
- ✅ Система рейтингу гравців
- ✅ Admin панель для управління

Наступний крок: додати інші функції (Analytics, Achievements, Notifications, Player Finder)
