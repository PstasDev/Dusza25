"""
Management command to initialize default achievements
"""
from django.core.management.base import BaseCommand
from damareen.game_logic import inicializal_achievementeket


class Command(BaseCommand):
    help = 'Inicializálja az alapértelmezett achievementeket'

    def handle(self, *args, **options):
        self.stdout.write('Achievementek inicializálása...')
        
        inicializal_achievementeket()
        
        self.stdout.write(self.style.SUCCESS('✅ Achievementek sikeresen inicializálva!'))
        self.stdout.write('')
        self.stdout.write('Elérhető achievementek:')
        self.stdout.write('  🎯 Első győzelem (10 pont)')
        self.stdout.write('  ⚔️ Veterán - 10 győzelem (50 pont)')
        self.stdout.write('  👑 Bajnok - 50 győzelem (200 pont)')
        self.stdout.write('  🏆 Legenda - 100 győzelem (500 pont)')
        self.stdout.write('  🔥 Lendületben - 3 sorozat (25 pont)')
        self.stdout.write('  💪 Legyőzhetetlen - 5 sorozat (75 pont)')
        self.stdout.write('  ⚡ Halhatatlan - 10 sorozat (250 pont)')
        self.stdout.write('  💔 Kitartó - 10 vereség (20 pont)')
