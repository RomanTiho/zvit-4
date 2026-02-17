# Django Backend для FootballHub

## Встановлення

1. Створити віртуальне середовище:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Встановити залежності:
```bash
pip install -r requirements.txt
```

3. Застосувати міграції:
```bash
cd backend
python manage.py migrate
```

4. Створити суперкористувача:
```bash
python manage.py createsuperuser
```

5. Запустити сервер:
```bash
python manage.py runserver 8001
```

## Структура Проекту

```
backend/
├── config/           # Налаштування проекту
├── players/          # Рейтинг гравців
├── analytics/        # Аналітика команд
├── achievements/     # Система досягнень
├── notifications/    # Повідомлення
└── player_finder/    # Пошук гравців
```

## API Endpoints

### Players
- `GET /api/players/` - Список гравців
- `GET /api/players/{id}/` - Деталі гравця
- `GET /api/players/{id}/rating_history/` - Історія рейтингу
- `POST /api/players/{id}/update_stats/` - Оновити статистику
- `GET /api/players/leaderboard/` - Таблиця лідерів

### Analytics
- `GET /api/analytics/teams/` - Аналітика команд
- `GET /api/analytics/teams/{id}/performance_trend/` - Тренд продуктивності
- `GET /api/analytics/teams/{id}/strengths_weaknesses/` - Сильні/слабкі сторони

### Achievements
- `GET /api/achievements/` - Список досягнень
- `GET /api/user-achievements/` - Досягнення користувача
- `GET /api/user-achievements/check_progress/` - Перевірити прогрес

### Notifications
- `GET /api/notifications/` - Всі повідомлення
- `GET /api/notifications/unread/` - Непрочитані
- `POST /api/notifications/{id}/mark_read/` - Позначити як прочитане

### Player Finder
- `GET /api/player-finder/` - Доступні гравці
- `GET /api/player-finder/search/` - Пошук гравців

## Запуск Development

Terminal 1 (Frontend):
```bash
python serve.py
```

Terminal 2 (Backend):
```bash
cd backend
python manage.py runserver 8001
```

Frontend: http://localhost:8000
Backend: http://localhost:8001
Admin: http://localhost:8001/admin
