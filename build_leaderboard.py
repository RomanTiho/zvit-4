"""
Скрипт:
1. Доповнює всі команди до 11 гравців (якщо менше)
2. Видаляє старих ботів з бази
3. Створює User + Player для кожного гравця зі списків команд
4. Генерує статистику → рейтинг автоматично рахується моделлю
"""
import os, sys, django, random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from my_app.models import Player, PlayerStats, Team

# ─── Укр. імена для доповнення ────────────────────────────────────────────────
EXTRA_NAMES = [
    "Ковальчук Андрій", "Захаренко Юрій", "Панченко Віктор", "Мельник Роман",
    "Ткаченко Ігор",    "Гончаренко Олег","Бондаренко Сергій","Назаренко Дмитро",
    "Savchenko Ivan",   "Sydorenko Vasyl", "Lysenko Pavel",   "Moroz Anton",
    "Petrenko Denys",   "Koval Oleksiy",  "Zinchenko Artem", "Yaremchuk Mykola",
    "Тимченко Артем",   "Рибаченко Сашко","Шульга Максим",   "Олійник Борис",
]

# ─── 1. Доповнити команди до 11 гравців ───────────────────────────────────────
print("=== Доповнення команд до 11 гравців ===")
extra_idx = 0
for team in Team.objects.all():
    roster = list(team.player_roster or [])
    while len(roster) < 11:
        roster.append(EXTRA_NAMES[extra_idx % len(EXTRA_NAMES)])
        extra_idx += 1
    if len(team.player_roster or []) != len(roster):
        team.player_roster = roster
        team.players_count = 11
        team.save()
        print(f"  {team.name}: доповнено до 11")
    else:
        print(f"  {team.name}: вже {len(roster)} гравців — ОК")

# ─── 2. Видалити старих ботів ─────────────────────────────────────────────────
print("\n=== Видалення старих Player-ботів ===")
bots = User.objects.filter(player__isnull=False).exclude(is_superuser=True)
# Не чіпаємо тренерів (Coach group)
bots = bots.exclude(groups__name='Coach')
count = bots.count()
bots.delete()
print(f"  Видалено {count} користувачів-ботів.")

# ─── 3. Позиції команди (11 чоловік, класична розстановка 4-4-2) ──────────────
TEAM_POSITIONS = ['GK','DEF','DEF','DEF','DEF','MID','MID','MID','MID','FWD','FWD']

# ─── 4. Створити Player для кожного гравця з ростеру ──────────────────────────
print("\n=== Генерація гравців ===")
seen_names = {}     # name -> player (щоб не дублювати)
created = 0

for team in Team.objects.all():
    roster = team.player_roster or []
    pos_list = TEAM_POSITIONS.copy()
    random.shuffle(pos_list)

    for i, full_name in enumerate(roster[:11]):
        if full_name in seen_names:
            continue            # гравець вже є (між командами дублюватись не будуть)

        parts = full_name.split()
        last  = parts[0] if parts else "Гравець"
        first = parts[1] if len(parts) > 1 else ""

        username = f"p_{team.id}_{i}_{random.randint(1000,9999)}"
        user = User.objects.create_user(
            username=username,
            first_name=first,
            last_name=last,
            password="Footb@llHub2025!"
        )

        position = pos_list[i % len(pos_list)]
        player = Player.objects.create(
            user=user,
            position=position,
            jersey_number=i + 1
        )
        seen_names[full_name] = player
        created += 1

        # Статистика: 4–8 матчів, залежно від позиції
        num_matches = random.randint(4, 8)
        for _ in range(num_matches):
            is_fwd = position == 'FWD'
            is_mid = position == 'MID'
            is_def = position in ('DEF', 'MID')
            is_gk  = position == 'GK'
            PlayerStats.objects.create(
                player=player,
                match_id=random.randint(1000, 9999),
                goals           = random.randint(0, 2) if is_fwd else (random.randint(0,1) if is_mid else 0),
                assists         = random.randint(0, 2) if (is_fwd or is_mid) else random.randint(0,1),
                minutes_played  = random.randint(60, 90),
                shots           = random.randint(1, 6) if is_fwd else (random.randint(0,2) if is_mid else 0),
                shots_on_target = random.randint(0, 3) if is_fwd else (random.randint(0,1) if is_mid else 0),
                key_passes      = random.randint(0, 3) if (is_fwd or is_mid) else random.randint(0,1),
                tackles         = random.randint(2, 7) if is_def else 0,
                interceptions   = random.randint(1, 5) if is_def else 0,
                saves           = random.randint(2, 8) if is_gk else 0,
                yellow_cards    = 1 if random.random() < 0.1 else 0,
                red_cards       = 0,
            )

print(f"  Створено {created} нових гравців.")

# ─── 5. Оновити загальний рейтинг ────────────────────────────────────────────
print("\n=== Перерахунок рейтингу ===")
for player in Player.objects.all():
    player.update_rating()
print("  Готово!")

# ─── Підсумок ─────────────────────────────────────────────────────────────────
total = Player.objects.count()
print(f"\n✅ Усього гравців у базі: {total}")
top5 = Player.objects.order_by('-overall_rating')[:5]
print("Топ-5:")
for p in top5:
    print(f"  {p.user.get_full_name() or p.user.username}  — {p.overall_rating}  ({p.get_position_display()})")
