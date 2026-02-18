"""
Management command для оновлення рейтингів всіх гравців
"""
from django.core.management.base import BaseCommand
from my_app.models import Player


class Command(BaseCommand):
    help = 'Оновити рейтинги всіх гравців на основі їх статистики'

    def handle(self, *args, **options):
        players = Player.objects.all()
        updated_count = 0
        
        self.stdout.write('Оновлення рейтингів гравців...')
        
        for player in players:
            old_rating = player.overall_rating
            new_rating = player.update_rating()
            
            if old_rating != new_rating:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ {player.user.username}: {old_rating} → {new_rating}'
                    )
                )
                updated_count += 1
            else:
                self.stdout.write(
                    f'  {player.user.username}: {old_rating} (без змін)'
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nГотово! Оновлено рейтинги {updated_count} гравців з {players.count()}'
            )
        )
