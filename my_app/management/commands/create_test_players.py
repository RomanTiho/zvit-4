from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from my_app.models import Player, PlayerStats
from my_app.services import PlayerRatingService
import random


class Command(BaseCommand):
    help = 'Створює тестових гравців з випадковою статистикою'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Кількість гравців для створення'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Імена для генерації
        first_names = [
            'Андрій', 'Богдан', 'Віктор', 'Григорій', 'Дмитро',
            'Євген', 'Іван', 'Максим', 'Олександр', 'Петро',
            'Роман', 'Сергій', 'Тарас', 'Юрій', 'Ярослав'
        ]
        
        last_names = [
            'Шевченко', 'Коваленко', 'Бондаренко', 'Мельник', 'Ткаченко',
            'Кравченко', 'Морозов', 'Петренко', 'Іваненко', 'Савченко',
            'Павленко', 'Марченко', 'Литвиненко', 'Гончаренко', 'Сидоренко'
        ]
        
        positions = ['GK', 'DEF', 'MID', 'FWD']
        
        self.stdout.write(self.style.SUCCESS(f'Створення {count} тестових гравців...'))
        
        created_count = 0
        
        for i in range(count):
            # Генерація імені
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}_{last_name.lower()}_{i+1}"
            
            # Перевірка чи користувач вже існує
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'Користувач {username} вже існує, пропускаємо'))
                continue
            
            # Створення користувача
            user = User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password='password123',
                first_name=first_name,
                last_name=last_name
            )
            
            # Створення гравця
            position = random.choice(positions)
            player = Player.objects.create(
                user=user,
                position=position
            )
            
            # Генерація випадкової статистики (3-10 матчів)
            num_matches = random.randint(3, 10)
            
            for match_num in range(1, num_matches + 1):
                # Статистика залежить від позиції
                if position == 'GK':
                    goals = 0
                    assists = 0
                elif position == 'DEF':
                    goals = random.randint(0, 1)
                    assists = random.randint(0, 2)
                elif position == 'MID':
                    goals = random.randint(0, 2)
                    assists = random.randint(0, 3)
                else:  # FWD
                    goals = random.randint(0, 3)
                    assists = random.randint(0, 2)
                
                PlayerStats.objects.create(
                    player=player,
                    match_id=random.randint(1, 100),
                    goals=goals,
                    assists=assists,
                    yellow_cards=random.randint(0, 1),
                    red_cards=0 if random.random() > 0.1 else 1,
                    minutes_played=random.choice([90, 80, 70, 60])
                )
            
            # Розрахунок рейтингу
            rating = PlayerRatingService.calculate_rating(player)
            
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Створено гравця: {first_name} {last_name} ({position}) - Рейтинг: {rating}'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Успішно створено {created_count} гравців!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Перевірте: http://localhost:8001/api/players/')
        )
