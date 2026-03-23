import os
import random

import django

# --- Налаштування Django ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_project.settings")
django.setup()

from django.contrib.auth.models import User

from my_app.models import Player, PlayerStats, Team

print("Видалення поточних гравців-ботів (крім адміністраторів і тренерів)...")
# Знайти всіх користувачів, у яких є профіль Player
users_with_players = User.objects.filter(player__isnull=False)
deleted_count = 0
for u in users_with_players:
    # Якщо користувач не адмін і не тренер
    if not u.is_superuser and not u.groups.filter(name="Coach").exists():
        u.delete()  # Це автоматично видалить Player, PlayerStats і UserProfile
        deleted_count += 1
print(f"Видалено {deleted_count} гравців.")

print("Отримання команд з турнірів...")
teams = Team.objects.exclude(tournament=None).exclude(player_roster=None)
print(f"Знайдено {teams.count()} команд.")

positions = ["GK", "DEF", "DEF", "DEF", "DEF", "MID", "MID", "MID", "MID", "FWD", "FWD"]

created_count = 0
for team in teams:
    if not team.player_roster:
        continue

    print(f"Обробка команди: {team.name}")

    # Змішаємо позиції для гравців команди
    team_positions = positions.copy()
    random.shuffle(team_positions)

    for i, name in enumerate(team.player_roster):
        # name "Шевченко Олексій" -> first_name, last_name
        parts = name.split()
        last_name = parts[0] if len(parts) > 0 else "Гравець"
        first_name = parts[1] if len(parts) > 1 else ""
        username_base = f"player_{team.id}_{i}_{random.randint(100,999)}"

        user = User.objects.create_user(
            username=username_base,
            first_name=first_name,
            last_name=last_name,
            password="qwe123Player!",
        )

        position = team_positions[i % len(team_positions)]
        player = Player.objects.create(
            user=user, position=position, jersey_number=random.randint(1, 99)
        )
        created_count += 1

        # Створюємо фейкову статистику для гравця
        num_matches = random.randint(3, 7)
        for m in range(num_matches):
            PlayerStats.objects.create(
                player=player,
                match_id=random.randint(1000, 9999),
                goals=random.randint(0, 2) if position == "FWD" else 0,
                assists=random.randint(0, 1),
                minutes_played=random.randint(45, 90),
                shots=random.randint(0, 5) if position in ["FWD", "MID"] else 0,
                shots_on_target=(
                    random.randint(0, 3) if position in ["FWD", "MID"] else 0
                ),
                tackles=random.randint(1, 6) if position in ["DEF", "MID"] else 0,
                interceptions=random.randint(1, 5) if position in ["DEF", "MID"] else 0,
                saves=random.randint(2, 7) if position == "GK" else 0,
            )

print(f"\nГенерація рейтингу завершена! Створено {created_count} нових гравців.")
