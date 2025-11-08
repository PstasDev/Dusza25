"""
Management command minta játékkörnyezet létrehozásához
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from damareen.models import (
    Vilagkartya, Vezerkartya, Kazamata, KazamataKartya,
    JatekKornyezet, GyujtemenyKartya,
    ELEMENT_FIRE, ELEMENT_EARTH, ELEMENT_WATER, ELEMENT_AIR
)


class Command(BaseCommand):
    help = 'Létrehoz egy minta játékkörnyezetet a Damareen játékhoz'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Minta játékkörnyezet létrehozása...'))
        
        # Superuser ellenőrzése
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('Nincs superuser! Először hozz létre egyet: python manage.py createsuperuser'))
            return
        
        # Töröljük az előző adatokat (csak fejlesztési célokra!)
        Vilagkartya.objects.all().delete()
        Vezerkartya.objects.all().delete()
        Kazamata.objects.all().delete()
        JatekKornyezet.objects.all().delete()
        
        # Világkártyák létrehozása
        self.stdout.write('Világkártyák létrehozása...')
        
        kartyak = [
            ('Aragorn', 2, 5, ELEMENT_FIRE),
            ('Legolas', 4, 3, ELEMENT_AIR),
            ('Gimli', 3, 6, ELEMENT_EARTH),
            ('Gandalf', 5, 4, ELEMENT_FIRE),
            ('Frodo', 2, 2, ELEMENT_WATER),
            ('Sam', 3, 4, ELEMENT_EARTH),
            ('Merry', 2, 3, ELEMENT_AIR),
            ('Pippin', 2, 3, ELEMENT_WATER),
            ('Boromir', 4, 5, ELEMENT_FIRE),
            ('Faramir', 3, 4, ELEMENT_EARTH),
            ('Éowyn', 4, 4, ELEMENT_AIR),
            ('Théoden', 3, 5, ELEMENT_EARTH),
            ('Galadriel', 5, 3, ELEMENT_WATER),
            ('Elrond', 4, 4, ELEMENT_WATER),
            ('Arwen', 3, 3, ELEMENT_AIR),
            ('Saruman', 6, 5, ELEMENT_FIRE),
            ('ObiWan', 2, 2, ELEMENT_WATER),
            ('Luke', 3, 3, ELEMENT_AIR),
            ('Yoda', 5, 2, ELEMENT_EARTH),
            ('Vader', 6, 6, ELEMENT_FIRE),
        ]
        
        vilag_kartyak = {}
        for nev, sebzes, eletero, tipus in kartyak:
            kartya = Vilagkartya.objects.create(
                nev=nev,
                sebzes=sebzes,
                eletero=eletero,
                tipus=tipus
            )
            vilag_kartyak[nev] = kartya
            self.stdout.write(f'  ✓ {kartya}')
        
        # Vezérkártyák létrehozása
        self.stdout.write('\nVezérkártyák létrehozása...')
        
        vezerek = [
            ('Darth ObiWan', 'ObiWan', 'sebzes'),
            ('Master Luke', 'Luke', 'eletero'),
            ('Dark Gandalf', 'Gandalf', 'sebzes'),
            ('King Aragorn', 'Aragorn', 'eletero'),
            ('Elder Yoda', 'Yoda', 'sebzes'),
        ]
        
        vezer_kartyak = {}
        for nev, eredeti, duplazas in vezerek:
            vezer = Vezerkartya.objects.create(
                nev=nev,
                eredeti_kartya=vilag_kartyak[eredeti],
                duplazas_tipusa=duplazas
            )
            vezer_kartyak[nev] = vezer
            self.stdout.write(f'  ✓ {vezer} (S:{vezer.sebzes}, É:{vezer.eletero})')
        
        # Kazamaták létrehozása
        self.stdout.write('\nKazamaták létrehozása...')
        
        # 1. Egyszerű találkozás
        kaz1 = Kazamata.objects.create(
            nev='Első próba',
            tipus=Kazamata.TIPUS_EGYSZERU
        )
        KazamataKartya.objects.create(
            kazamata=kaz1,
            sorrend=1,
            vilag_kartya=vilag_kartyak['Merry']
        )
        self.stdout.write(f'  ✓ {kaz1}')
        
        # 2. Kis kazamata
        kaz2 = Kazamata.objects.create(
            nev='Az erdő mélyén',
            tipus=Kazamata.TIPUS_KIS
        )
        KazamataKartya.objects.create(kazamata=kaz2, sorrend=1, vilag_kartya=vilag_kartyak['Pippin'])
        KazamataKartya.objects.create(kazamata=kaz2, sorrend=2, vilag_kartya=vilag_kartyak['Sam'])
        KazamataKartya.objects.create(kazamata=kaz2, sorrend=3, vilag_kartya=vilag_kartyak['Gimli'])
        KazamataKartya.objects.create(kazamata=kaz2, sorrend=4, vezer_kartya=vezer_kartyak['Master Luke'])
        self.stdout.write(f'  ✓ {kaz2}')
        
        # 3. Nagy kazamata
        kaz3 = Kazamata.objects.create(
            nev='A mélység királynője',
            tipus=Kazamata.TIPUS_NAGY
        )
        KazamataKartya.objects.create(kazamata=kaz3, sorrend=1, vilag_kartya=vilag_kartyak['Boromir'])
        KazamataKartya.objects.create(kazamata=kaz3, sorrend=2, vilag_kartya=vilag_kartyak['Faramir'])
        KazamataKartya.objects.create(kazamata=kaz3, sorrend=3, vilag_kartya=vilag_kartyak['Éowyn'])
        KazamataKartya.objects.create(kazamata=kaz3, sorrend=4, vilag_kartya=vilag_kartyak['Théoden'])
        KazamataKartya.objects.create(kazamata=kaz3, sorrend=5, vilag_kartya=vilag_kartyak['Galadriel'])
        KazamataKartya.objects.create(kazamata=kaz3, sorrend=6, vezer_kartya=vezer_kartyak['Dark Gandalf'])
        self.stdout.write(f'  ✓ {kaz3}')
        
        # 4. Még egy kis kazamata
        kaz4 = Kazamata.objects.create(
            nev='Sötét lovagok',
            tipus=Kazamata.TIPUS_KIS
        )
        KazamataKartya.objects.create(kazamata=kaz4, sorrend=1, vilag_kartya=vilag_kartyak['Arwen'])
        KazamataKartya.objects.create(kazamata=kaz4, sorrend=2, vilag_kartya=vilag_kartyak['Elrond'])
        KazamataKartya.objects.create(kazamata=kaz4, sorrend=3, vilag_kartya=vilag_kartyak['Legolas'])
        KazamataKartya.objects.create(kazamata=kaz4, sorrend=4, vezer_kartya=vezer_kartyak['King Aragorn'])
        self.stdout.write(f'  ✓ {kaz4}')
        
        # Játékkörnyezet létrehozása
        self.stdout.write('\nJátékkörnyezet létrehozása...')
        
        kornyezet = JatekKornyezet.objects.create(
            nev='Középfölde kalandjai',
            keszitette=admin_user
        )
        
        # Kezdő gyűjtemény (egyszerűbb kártyák)
        kezdo_kartyak = ['Frodo', 'Aragorn', 'Legolas', 'Gimli', 'Merry', 'Pippin', 'Sam']
        for kartya_nev in kezdo_kartyak:
            GyujtemenyKartya.objects.create(
                kornyezet=kornyezet,
                kartya=vilag_kartyak[kartya_nev]
            )
        
        self.stdout.write(f'  ✓ {kornyezet}')
        self.stdout.write(f'  ✓ Kezdő gyűjtemény: {len(kezdo_kartyak)} kártya')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Minta játékkörnyezet sikeresen létrehozva!'))
        self.stdout.write(self.style.SUCCESS(f'   Játékkörnyezet neve: "{kornyezet.nev}"'))
        self.stdout.write(self.style.SUCCESS(f'   Világkártyák: {len(vilag_kartyak)} db'))
        self.stdout.write(self.style.SUCCESS(f'   Vezérkártyák: {len(vezer_kartyak)} db'))
        self.stdout.write(self.style.SUCCESS(f'   Kazamaták: 4 db'))
        self.stdout.write(self.style.SUCCESS(f'\n   Most futtasd: python manage.py runserver'))
