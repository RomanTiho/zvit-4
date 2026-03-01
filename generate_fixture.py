import json
from datetime import datetime

# Sample data translated from app.js to Django fixture format
tournaments = [
    {
        "model": "my_app.tournament",
        "pk": 1,
        "fields": {
            "name": 'Літній Кубок 2026',
            "start_date": '2026-06-15',
            "end_date": '2026-06-30',
            "format": 'league',
            "max_teams": 8,
            "location": 'Київ, Україна',
            "description": 'Запрошуємо всіх любителів футболу взяти участь у нашому літньому турнірі! Це чудова можливість показати свої навички.',
            "status": 'upcoming'
        }
    },
    {
        "model": "my_app.tournament",
        "pk": 2,
        "fields": {
            "name": 'Весняний Чемпіонат 2026',
            "start_date": '2026-04-10',
            "end_date": '2026-04-25',
            "format": 'knockout',
            "max_teams": 16,
            "location": 'Львів, Україна',
            "description": 'Турнір на вибування для найсильніших команд регіону. Переможець отримає кубок та грошовий приз.',
            "status": 'upcoming'
        }
    },
    {
        "model": "my_app.tournament",
        "pk": 3,
        "fields": {
            "name": 'Літній Кубок 2025',
            "start_date": '2025-06-15',
            "end_date": '2025-06-30',
            "format": 'league',
            "max_teams": 8,
            "location": 'Київ, Україна',
            "description": 'Літній турнір 2025 року пройшов з великим успіхом! Команда Динамо стала переможцем.',
            "status": 'completed'
        }
    }
]

teams = [
    {
        "model": "my_app.team",
        "pk": 1,
        "fields": {
            "tournament": 1,
            "name": 'Блискавка',
            "captain": 'Коваленко Іван',
            "email": 'bliskavka@example.com',
            "phone": '+380501234567',
            "players_count": 11,
            "player_roster": ['Мороз Василь', 'Лисенко Андрій', 'Коваленко Іван', 'Перець Михайло', 'Сидоренко Олег', 'Гриценко Павло', 'Бондаренко Юрій', 'Ткаченко Роман', 'Мельник Сергій', 'Захаренко Денис', 'Поліщук Артем']
        }
    },
    {
        "model": "my_app.team",
        "pk": 2,
        "fields": {
            "tournament": 1,
            "name": 'Сталь',
            "captain": 'Пилипенко Максим',
            "email": 'stal@example.com',
            "phone": '+380501234568',
            "players_count": 11,
            "player_roster": ['Федоренко Богдан', 'Кравченко Дмитро', 'Нечипоренко Ігор', 'Пилипенко Максим']
        }
    },
    {
        "model": "my_app.team",
        "pk": 3,
        "fields": {
            "tournament": 3,
            "name": 'Блискавка',
            "captain": 'Коваленко Іван',
            "email": 'bliskavka@example.com',
            "phone": '+380501234567',
            "players_count": 11,
            "player_roster": ['Мороз Василь', 'Лисенко Андрій', 'Коваленко Іван']
        }
    },
]

standings = [
    {
        "model": "my_app.standing",
        "pk": 1,
        "fields": {
            "tournament": 3,
            "team": 3,
            "played": 5, "won": 4, "drawn": 1, "lost": 0, "goals_for": 12, "goals_against": 3, "points": 13
        }
    }
]

from django.utils.dateparse import parse_datetime

matches = [
    {
        "model": "my_app.match",
        "pk": 1,
        "fields": {
            "tournament": 3,
            "date": "2025-06-15T15:00:00Z",
            "home_team": 'Блискавка',
            "away_team": 'Сталь',
            "home_score": 2,
            "away_score": 1,
            "status": 'completed'
        }
    },
    {
        "model": "my_app.match",
        "pk": 2,
        "fields": {
            "tournament": 3,
            "date": "2025-06-16T15:00:00Z",
            "home_team": 'Метеор',
            "away_team": 'Колос',
            "home_score": 1,
            "away_score": 0,
            "status": 'completed'
        }
    }
]

with open(r'd:\zvit4\diplom\my_app\fixtures\initial_data.json', 'w', encoding='utf-8') as f:
    json.dump(tournaments + teams + standings + matches, f, ensure_ascii=False, indent=2)

print("Fixture generated.")
