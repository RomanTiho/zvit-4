"""
Скрипт для додавання 7 команд, результатів матчів та турнірної таблиці
до турніру "Літній Кубок 2025" (pk=3).

Запуск: python seed_summer_cup_2025.py
"""

import os
import sys

import django

# --- Налаштування Django ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_project.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from datetime import datetime, timezone

from my_app.models import Match, Standing, Team, Tournament

TOURNAMENT_ID = 3  # "Літній Кубок 2025"

# ─── 1. Отримуємо турнір ───────────────────────────────────────────────────────
tournament = Tournament.objects.get(pk=TOURNAMENT_ID)
print(f"Турнір: {tournament.name}  (статус: {tournament.status})")

# ─── 2. Нові команди (7 штук) ─────────────────────────────────────────────────
new_teams_data = [
    {
        "name": "Динамо",
        "captain": "Шевченко Олексій",
        "email": "dynamo@example.com",
        "phone": "+380671000001",
        "players_count": 11,
        "player_roster": [
            "Шевченко Олексій",
            "Бойко Владислав",
            "Бураков Микола",
            "Луценко Артем",
            "Кадар Тамаш",
            "Сидорчук Сергій",
            "Гармаш Денис",
            "Циганков Віктор",
            "Шапаренко Микола",
            "Вербич Дєян",
            "Супряга Артем",
        ],
    },
    {
        "name": "Шахтар",
        "captain": "Маторан Педро",
        "email": "shakhtar@example.com",
        "phone": "+380671000002",
        "players_count": 11,
        "player_roster": [
            "Трубін Анатолій",
            "Додо Педро",
            "Кривцов Сергій",
            "Маторан Педро",
            "Степаненко Тарас",
            "Майкон Мей",
            "Судаков Георгій",
            "Марлон Сантос",
            "Зубков Олег",
            "Лассіна Траоре",
            "Антоні Жун",
        ],
    },
    {
        "name": "Металіст",
        "captain": "Кравченко Павло",
        "email": "metalist@example.com",
        "phone": "+380671000003",
        "players_count": 11,
        "player_roster": [
            "Кравченко Павло",
            "Іванов Дмитро",
            "Семенюк Роман",
            "Попов Андрій",
            "Онищенко Богдан",
            "Голуб Ігор",
            "Ященко Олег",
            "Харченко Микита",
            "Демченко Сергій",
            "Марченко Юрій",
            "Литвиненко Артем",
        ],
    },
    {
        "name": "Карпати",
        "captain": "Олексієнко Віктор",
        "email": "karpaty@example.com",
        "phone": "+380671000004",
        "players_count": 11,
        "player_roster": [
            "Олексієнко Віктор",
            "Гавриш Роман",
            "Рудик Василь",
            "Козак Олег",
            "Яремчук Роман",
            "Борець Микола",
            "Паращук Андрій",
            "Захарчин Ігор",
            "Білик Петро",
            "Кучер Іван",
            "Лесюк Михайло",
        ],
    },
    {
        "name": "Ворскла",
        "captain": "Безус Роман",
        "email": "vorskla@example.com",
        "phone": "+380671000005",
        "players_count": 11,
        "player_roster": [
            "Безус Роман",
            "Чеберко Євген",
            "Процюк Сергій",
            "Лучкевич Вадим",
            "Мартиненко Денис",
            "Тригуба Максим",
            "Кулач Дмитро",
            "Чорний Олег",
            "Сікан Олексій",
            "Коваль Руслан",
            "Шайтанов Антон",
        ],
    },
    {
        "name": "Олімпік",
        "captain": "Тищенко Артем",
        "email": "olimpik@example.com",
        "phone": "+380671000006",
        "players_count": 11,
        "player_roster": [
            "Тищенко Артем",
            "Бодня Дмитро",
            "Горленко Олег",
            "Закалюжний Серхіо",
            "Гамула Михайло",
            "Кобець Іван",
            "Морозенко Ярослав",
            "Піддубний Сергій",
            "Руснак Григорій",
            "Федченко Микола",
            "Коломієць Андрій",
        ],
    },
    {
        "name": "Чорноморець",
        "captain": "Лещук Владислав",
        "email": "chornomorets@example.com",
        "phone": "+380671000007",
        "players_count": 11,
        "player_roster": [
            "Лещук Владислав",
            "Дудик Руслан",
            "Кадєєв Дмитро",
            "Назаренко Богдан",
            "Перепелиця Андрій",
            "Яковенко Олег",
            "Штурмак Євген",
            "Цибуленко Максим",
            "Куліш Іван",
            "Плюш Сергій",
            "Горбань Артем",
        ],
    },
]

# Видаляємо старі команди (крім Блискавки, pk=3) якщо вже є зайві від попередніх запусків
print("\nПеревірка існуючих команд у турнірі...")
existing_teams = list(Team.objects.filter(tournament=tournament))
print(f"  Знайдено {len(existing_teams)} команд(и):")
for t in existing_teams:
    print(f"    - {t.name} (pk={t.pk})")

# Видаляємо команди, додані попередніми запусками скрипта (не Блискавка)
extra = Team.objects.filter(tournament=tournament).exclude(pk=3)
deleted_count = extra.count()
if deleted_count:
    extra.delete()
    print(f"  Видалено {deleted_count} зайвих команд (від попередніх запусків).")

# Додаємо 7 нових команд
print("\nДодавання нових команд...")
created_teams = []
for data in new_teams_data:
    team = Team.objects.create(tournament=tournament, **data)
    created_teams.append(team)
    print(f"  + {team.name}")

# Всі 8 команд
all_teams = list(Team.objects.filter(tournament=tournament).order_by("pk"))
print(f"\nУсього команд у турнірі: {len(all_teams)}")
for t in all_teams:
    print(f"  {t.pk}: {t.name}")

# ─── 3. Генерація матчів (round-robin: кожна з кожною) ────────────────────────
print("\nВидалення старих матчів турніру...")
old_matches = Match.objects.filter(tournament=tournament)
print(f"  Видалено {old_matches.count()} матч(ів).")
old_matches.delete()

# Результати матчів — задаємо реалістичні значення
# Структура: (home_name, away_name, home_score, away_score)
# Дати: з 15 по 30 червня 2025, по 1–3 матчі на день

match_results = [
    # Тур 1 — 15 червня
    ("Блискавка", "Динамо", 1, 3),
    ("Шахтар", "Металіст", 2, 0),
    ("Карпати", "Ворскла", 1, 1),
    ("Олімпік", "Чорноморець", 0, 2),
    # Тур 2 — 17 червня
    ("Динамо", "Шахтар", 1, 2),
    ("Металіст", "Карпати", 3, 1),
    ("Ворскла", "Олімпік", 2, 0),
    ("Чорноморець", "Блискавка", 1, 1),
    # Тур 3 — 19 червня
    ("Блискавка", "Металіст", 2, 2),
    ("Динамо", "Карпати", 4, 0),
    ("Шахтар", "Ворскла", 3, 1),
    ("Чорноморець", "Олімпік", 1, 0),
    # Тур 4 — 21 червня
    ("Карпати", "Блискавка", 0, 2),
    ("Металіст", "Динамо", 1, 1),
    ("Ворскла", "Чорноморець", 2, 3),
    ("Олімпік", "Шахтар", 0, 1),
    # Тур 5 — 23 червня
    ("Блискавка", "Ворскла", 3, 0),
    ("Динамо", "Чорноморець", 2, 1),
    ("Шахтар", "Карпати", 2, 0),
    ("Металіст", "Олімпік", 1, 1),
    # Тур 6 — 25 червня
    ("Чорноморець", "Шахтар", 0, 3),
    ("Олімпік", "Блискавка", 1, 2),
    ("Карпати", "Динамо", 0, 2),
    ("Ворскла", "Металіст", 1, 2),
    # Тур 7 — 27 червня
    ("Блискавка", "Шахтар", 1, 1),
    ("Динамо", "Ворскла", 3, 0),
    ("Металіст", "Чорноморець", 2, 0),
    ("Карпати", "Олімпік", 1, 0),
]

# Дати матчів
match_dates = [
    "2025-06-15",
    "2025-06-15",
    "2025-06-15",
    "2025-06-15",  # тур 1
    "2025-06-17",
    "2025-06-17",
    "2025-06-17",
    "2025-06-17",  # тур 2
    "2025-06-19",
    "2025-06-19",
    "2025-06-19",
    "2025-06-19",  # тур 3
    "2025-06-21",
    "2025-06-21",
    "2025-06-21",
    "2025-06-21",  # тур 4
    "2025-06-23",
    "2025-06-23",
    "2025-06-23",
    "2025-06-23",  # тур 5
    "2025-06-25",
    "2025-06-25",
    "2025-06-25",
    "2025-06-25",  # тур 6
    "2025-06-27",
    "2025-06-27",
    "2025-06-27",
    "2025-06-27",  # тур 7
]

print("\nСтворення матчів...")
times = ["12:00:00", "14:00:00", "16:00:00", "18:00:00"]
for i, (home, away, hs, as_) in enumerate(match_results):
    dt_str = f"{match_dates[i]}T{times[i % 4]}+00:00"
    dt = datetime.fromisoformat(dt_str)
    Match.objects.create(
        tournament=tournament,
        date=dt,
        home_team=home,
        away_team=away,
        home_score=hs,
        away_score=as_,
        status="completed",
    )
print(f"  Створено {len(match_results)} матч(ів).")

# ─── 4. Розрахунок турнірної таблиці ─────────────────────────────────────────
print("\nОновлення турнірної таблиці...")

# Видаляємо старі рядки таблиці
Standing.objects.filter(tournament=tournament).delete()

# Ініціалізуємо статистику для кожної команди
stats = {
    t.name: {
        "team_obj": t,
        "played": 0,
        "won": 0,
        "drawn": 0,
        "lost": 0,
        "gf": 0,
        "ga": 0,
        "pts": 0,
    }
    for t in all_teams
}

for home, away, hs, as_ in match_results:
    if home not in stats or away not in stats:
        print(f"  УВАГА: команда '{home}' або '{away}' не знайдена у словнику!")
        continue

    # home
    stats[home]["played"] += 1
    stats[home]["gf"] += hs
    stats[home]["ga"] += as_
    # away
    stats[away]["played"] += 1
    stats[away]["gf"] += as_
    stats[away]["ga"] += hs

    if hs > as_:
        stats[home]["won"] += 1
        stats[home]["pts"] += 3
        stats[away]["lost"] += 1
    elif hs < as_:
        stats[away]["won"] += 1
        stats[away]["pts"] += 3
        stats[home]["lost"] += 1
    else:
        stats[home]["drawn"] += 1
        stats[home]["pts"] += 1
        stats[away]["drawn"] += 1
        stats[away]["pts"] += 1

for name, s in stats.items():
    Standing.objects.create(
        tournament=tournament,
        team=s["team_obj"],
        played=s["played"],
        won=s["won"],
        drawn=s["drawn"],
        lost=s["lost"],
        goals_for=s["gf"],
        goals_against=s["ga"],
        points=s["pts"],
    )

print("\n  Турнірна таблиця:")
print(
    f"  {'#':<3} {'Команда':<14} {'М':<4} {'В':<4} {'Н':<4} {'П':<4} {'ГЗ':<4} {'ГП':<4} {'РГ':<5} {'О'}"
)
sorted_standings = sorted(
    stats.values(), key=lambda x: (-x["pts"], -(x["gf"] - x["ga"]), -x["gf"])
)
for pos, s in enumerate(sorted_standings, 1):
    gd = s["gf"] - s["ga"]
    print(
        f"  {pos:<3} {s['team_obj'].name:<14} {s['played']:<4} {s['won']:<4} {s['drawn']:<4} {s['lost']:<4} {s['gf']:<4} {s['ga']:<4} {gd:+d}    {s['pts']}"
    )

print("\nГотово! База даних оновлена.")
