from django.db import models
from django.contrib.auth.models import User


class Player(models.Model):
    """Модель гравця з рейтингом"""
    POSITION_CHOICES = [
        ('GK', 'Воротар'),
        ('DEF', 'Захисник'),
        ('MID', 'Півзахисник'),
        ('FWD', 'Нападник')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player')
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    jersey_number = models.IntegerField(null=True, blank=True, help_text='Ігровий номер (1-99)')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    overall_rating = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    matches_played = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-overall_rating']
        verbose_name = 'Гравець'
        verbose_name_plural = 'Гравці'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_position_display()}"
    
    def calculate_rating(self):
        """
        Загальний рейтинг гравця = середнє рейтингів матчів (шкала 1.0–10.0).
        Рейтинг кожного матчу вже розраховується в PlayerStats._calculate_match_rating().
        """
        from django.db.models import Avg
        from decimal import Decimal

        recent_stats = self.stats.filter(rating__isnull=False)[:10]
        if not recent_stats.exists():
            return Decimal('0.00')

        avg = recent_stats.aggregate(Avg('rating'))['rating__avg'] or Decimal('0')
        return round(Decimal(str(avg)), 2)

    def update_rating(self):
        """Оновити загальний рейтинг гравця і записати в історію."""
        new_rating = self.calculate_rating()
        if self.overall_rating != new_rating:
            PlayerRatingHistory.objects.create(player=self, rating=new_rating)
            self.overall_rating = new_rating
            self.save(update_fields=['overall_rating'])
        return new_rating


class PlayerStats(models.Model):
    """Статистика гравця за матч"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='stats')
    match_id = models.IntegerField()

    # Базова статистика
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)
    minutes_played = models.IntegerField(default=90)

    # xG-натхненна статистика (якість гри)
    shots = models.IntegerField(default=0, help_text='Усього ударів по воротах')
    shots_on_target = models.IntegerField(default=0, help_text='Удари у ціль (xG proxy)')
    key_passes = models.IntegerField(default=0, help_text='Ключові передачі (передача під удар)')
    saves = models.IntegerField(default=0, help_text='Сейви (тільки для воротаря)')
    tackles = models.IntegerField(default=0, help_text='Відбори мяча')
    interceptions = models.IntegerField(default=0, help_text='Перехоплення')

    # Рейтинг матчу (0–10), розраховується автоматично
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Статистика гравця'
        verbose_name_plural = 'Статистика гравців'

    def __str__(self):
        return f"{self.player.user.username} - Матч {self.match_id}"

    def save(self, *args, **kwargs):
        """При збереженні статистики автоматично рахуємо рейтинг матчу і оновлюємо гравця"""
        # Розраховуємо рейтинг матчу перед збереженням
        self.rating = self._calculate_match_rating()
        super().save(*args, **kwargs)
        # Оновлюємо загальний рейтинг гравця
        self.player.matches_played = self.player.stats.count()
        self.player.save(update_fields=['matches_played'])
        self.player.update_rating()

    def _calculate_match_rating(self):
        """
        xG-натхнена формула рейтингу матчу (1.0 – 10.0).

        Базовий бал: 5.0 (повна гра 90 хв).
        Бонуси/штрафи залежать від позиції та статистики.
        """
        from decimal import Decimal
        position = self.player.position
        score = Decimal('5.0')

        # --- Бонус за хвилини на полі ---
        if self.minutes_played < 20:
            score -= Decimal('1.5')
        elif self.minutes_played < 45:
            score -= Decimal('0.75')
        elif self.minutes_played < 60:
            score -= Decimal('0.25')

        # --- Голи (позиційно зважені) ---
        goal_weights = {'GK': Decimal('0.5'), 'DEF': Decimal('1.5'),
                        'MID': Decimal('1.5'), 'FWD': Decimal('1.0')}
        score += Decimal(str(self.goals)) * goal_weights.get(position, Decimal('1.0'))

        # --- Асисти ---
        score += Decimal(str(self.assists)) * Decimal('1.0')

        # --- xG proxy: удари у ціль ---
        # Кожен удар у ціль = +0.2, максимум +1.5
        sot_bonus = min(Decimal(str(self.shots_on_target)) * Decimal('0.2'), Decimal('1.5'))
        score += sot_bonus

        # --- Ключові передачі ---
        kp_bonus = min(Decimal(str(self.key_passes)) * Decimal('0.15'), Decimal('0.9'))
        score += kp_bonus

        # --- Сейви (тільки GK) ---
        if position == 'GK':
            save_bonus = min(Decimal(str(self.saves)) * Decimal('0.3'), Decimal('2.0'))
            score += save_bonus

        # --- Оборонні дії (DEF/MID/GK) ---
        if position in ('GK', 'DEF', 'MID'):
            def_bonus = min(
                (Decimal(str(self.tackles)) + Decimal(str(self.interceptions))) * Decimal('0.1'),
                Decimal('1.0')
            )
            score += def_bonus

        # --- Штрафи за картки ---
        score -= Decimal(str(self.yellow_cards)) * Decimal('1.0')
        score -= Decimal(str(self.red_cards)) * Decimal('3.0')

        # Обмежуємо до [1.0, 10.0]
        score = max(Decimal('1.0'), min(Decimal('10.0'), score))
        return round(score, 1)



class PlayerRatingHistory(models.Model):
    """Історія зміни рейтингу"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='rating_history')
    rating = models.DecimalField(max_digits=4, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
        verbose_name = 'Історія рейтингу'
        verbose_name_plural = 'Історія рейтингів'
    
    def __str__(self):
        return f"{self.player.user.username} - {self.rating}"


class UPLSquadCache(models.Model):
    """Кеш складів команд УПЛ з API-Football (оновлюється раз на добу)"""
    team_name   = models.CharField(max_length=100, unique=True, verbose_name='Назва команди')
    api_team_id = models.IntegerField(verbose_name='ID команди в API')
    squad_json  = models.JSONField(default=list, verbose_name='Склад (JSON)')
    fetched_at  = models.DateTimeField(verbose_name='Час оновлення')

    class Meta:
        verbose_name        = 'Кеш складу УПЛ'
        verbose_name_plural = 'Кеш складів УПЛ'

    def __str__(self):
        return f"{self.team_name} (оновлено: {self.fetched_at:%d.%m.%Y %H:%M})"


class Tournament(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    format = models.CharField(max_length=50)
    max_teams = models.IntegerField()
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, default="upcoming")

    class Meta:
        verbose_name = 'Турнір'
        verbose_name_plural = 'Турніри'

    def __str__(self):
        return self.name

class Team(models.Model):
    tournament = models.ForeignKey(Tournament, related_name="teams", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    captain = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    players_count = models.IntegerField(default=11)
    player_roster = models.JSONField(default=list)

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команди'

    def __str__(self):
        return f"{self.name} ({self.tournament.name})"

class Standing(models.Model):
    tournament = models.ForeignKey(Tournament, related_name="standings", on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    played = models.IntegerField(default=0)
    won = models.IntegerField(default=0)
    drawn = models.IntegerField(default=0)
    lost = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Рядок турнірної таблиці'
        verbose_name_plural = 'Рядки турнірної таблиці'

class Match(models.Model):
    tournament = models.ForeignKey(Tournament, related_name="matches", on_delete=models.CASCADE)
    date = models.DateTimeField()
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default="completed")

    class Meta:
        verbose_name = 'Матч'
        verbose_name_plural = 'Матчі'

