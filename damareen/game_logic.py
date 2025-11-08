"""
Damareen játék logika
"""
from django.contrib.auth.models import User
from .models import (
    ELEMENT_FIRE, ELEMENT_EARTH, ELEMENT_WATER, ELEMENT_AIR,
    Harc, Utközet, Jatekoskartya, PakliKartya, 
    Achievement, PlayerAchievement, UserProfile
)


def elem_legyozi(elem1, elem2):
    """
    Meghatározza, hogy elem1 legyőzi-e elem2-t.
    Tűz > Föld > Víz > Levegő > Tűz
    """
    gyozelmek = {
        ELEMENT_FIRE: ELEMENT_EARTH,      # Tűz > Föld
        ELEMENT_EARTH: ELEMENT_WATER,     # Föld > Víz
        ELEMENT_WATER: ELEMENT_AIR,       # Víz > Levegő
        ELEMENT_AIR: ELEMENT_FIRE,        # Levegő > Tűz
    }
    
    return gyozelmek.get(elem1) == elem2


def utközet_ertekeles(jatekos_sebzes, jatekos_eletero, jatekos_tipus,
                       kazamata_sebzes, kazamata_eletero, kazamata_tipus):
    """
    Kiértékel egy ütközetet és visszaadja, hogy a játékos nyert-e, és miért.
    
    Visszatérés: (jatekos_nyert: bool, ok: str)
    """
    
    # 1. szabály: Sebzés vs életerő
    jatekos_sebez = jatekos_sebzes > kazamata_eletero
    kazamata_sebez = kazamata_sebzes > jatekos_eletero
    
    if jatekos_sebez and not kazamata_sebez:
        return True, f"Játékos sebzése ({jatekos_sebzes}) > Kazamata életereje ({kazamata_eletero})"
    
    if kazamata_sebez and not jatekos_sebez:
        return False, f"Kazamata sebzése ({kazamata_sebzes}) > Játékos életereje ({jatekos_eletero})"
    
    # 2. szabály: Típus alapján
    if elem_legyozi(jatekos_tipus, kazamata_tipus):
        jatekos_tipus_nev = dict([(ELEMENT_FIRE, 'Tűz'), (ELEMENT_EARTH, 'Föld'), 
                                   (ELEMENT_WATER, 'Víz'), (ELEMENT_AIR, 'Levegő')]).get(jatekos_tipus, jatekos_tipus)
        kazamata_tipus_nev = dict([(ELEMENT_FIRE, 'Tűz'), (ELEMENT_EARTH, 'Föld'), 
                                    (ELEMENT_WATER, 'Víz'), (ELEMENT_AIR, 'Levegő')]).get(kazamata_tipus, kazamata_tipus)
        return True, f"Típus előny: {jatekos_tipus_nev} > {kazamata_tipus_nev}"
    
    if elem_legyozi(kazamata_tipus, jatekos_tipus):
        jatekos_tipus_nev = dict([(ELEMENT_FIRE, 'Tűz'), (ELEMENT_EARTH, 'Föld'), 
                                   (ELEMENT_WATER, 'Víz'), (ELEMENT_AIR, 'Levegő')]).get(jatekos_tipus, jatekos_tipus)
        kazamata_tipus_nev = dict([(ELEMENT_FIRE, 'Tűz'), (ELEMENT_EARTH, 'Föld'), 
                                    (ELEMENT_WATER, 'Víz'), (ELEMENT_AIR, 'Levegő')]).get(kazamata_tipus, kazamata_tipus)
        return False, f"Típus előny: {kazamata_tipus_nev} > {jatekos_tipus_nev}"
    
    # 3. szabály: Ha nincs egyértelmű győztes, a kazamata nyer
    return False, "Döntetlen esetén a kazamata nyer"


def harc_vegrehajtasa(harc):
    """
    Végrehajtja a harcot és elmenti az eredményeket.
    
    Visszatérés: (jatekos_gyozott: bool, utközetek: list)
    """
    pakli = harc.jatek.pakli
    kazamata = harc.kazamata
    
    # Pakli kártyák lekérése
    pakli_kartyak = list(pakli.kartyak.all().order_by('sorrend'))
    kazamata_kartyak = list(kazamata.kartyak.all().order_by('sorrend'))
    
    if len(pakli_kartyak) != len(kazamata_kartyak):
        raise ValueError("A pakli és a kazamata kártyáinak száma nem egyezik!")
    
    utközetek = []
    jatekos_gyozelmek = 0
    
    # Végigmegyünk az ütközeteken
    for i, (pakli_kartya, kazamata_kartya) in enumerate(zip(pakli_kartyak, kazamata_kartyak)):
        jatekos_k = pakli_kartya.kartya
        
        # Játékos kártya adatai
        j_sebzes = jatekos_k.aktualis_sebzes
        j_eletero = jatekos_k.aktualis_eletero
        j_tipus = jatekos_k.tipus
        
        # Kazamata kártya adatai
        k_sebzes = kazamata_kartya.get_sebzes()
        k_eletero = kazamata_kartya.get_eletero()
        k_tipus = kazamata_kartya.get_tipus()
        
        # Ütközet kiértékelése
        jatekos_nyert, ok = utközet_ertekeles(
            j_sebzes, j_eletero, j_tipus,
            k_sebzes, k_eletero, k_tipus
        )
        
        if jatekos_nyert:
            jatekos_gyozelmek += 1
        
        # Ütközet mentése
        utközet = Utközet.objects.create(
            harc=harc,
            sorrend=i + 1,
            jatekos_kartya=jatekos_k,
            jatekos_sebzes=j_sebzes,
            jatekos_eletero=j_eletero,
            jatekos_tipus=j_tipus,
            kazamata_kartya_ref=kazamata_kartya,
            kazamata_sebzes=k_sebzes,
            kazamata_eletero=k_eletero,
            kazamata_tipus=k_tipus,
            jatekos_nyert=jatekos_nyert,
            gyoztes_ok=ok
        )
        utközetek.append(utközet)
    
    # Harc eredményének meghatározása
    # A játékos akkor nyer, ha legalább annyi kártyája nyert, mint amennyi a kazamatának
    szukseges_gyozelmek = (len(kazamata_kartyak) + 1) // 2  # Kerekítés felfelé
    jatekos_gyozott = jatekos_gyozelmek >= szukseges_gyozelmek
    
    # Harc befejezése
    harc.befejezve = True
    harc.jatekos_gyozott = jatekos_gyozott
    harc.save()
    
    return jatekos_gyozott, utközetek


def jutalom_alkalmazasa(jatek, kazamata, valasztott_kartya_id):
    """
    Alkalmazza a kazamata legyőzésének jutalmát a kiválasztott kártyára.
    
    Args:
        jatek: Jatek objektum
        kazamata: Kazamata objektum
        valasztott_kartya_id: A fejlesztendő Jatekoskartya id-ja
    """
    from .models import Kazamata
    
    try:
        kartya = Jatekoskartya.objects.get(id=valasztott_kartya_id, jatek=jatek)
    except Jatekoskartya.DoesNotExist:
        raise ValueError("A kiválasztott kártya nem található a gyűjteményben!")
    
    # Jutalom alkalmazása típus szerint
    if kazamata.tipus == Kazamata.TIPUS_EGYSZERU:
        # +1 sebzés
        kartya.aktualis_sebzes += 1
        kartya.save()
        return f"{kartya.eredeti_kartya.nev} +1 sebzést kapott!"
    
    elif kazamata.tipus == Kazamata.TIPUS_KIS:
        # +2 életerő
        kartya.aktualis_eletero += 2
        kartya.save()
        return f"{kartya.eredeti_kartya.nev} +2 életerőt kapott!"
    
    elif kazamata.tipus == Kazamata.TIPUS_NAGY:
        # +3 sebzés
        kartya.aktualis_sebzes += 3
        kartya.save()
        return f"{kartya.eredeti_kartya.nev} +3 sebzést kapott!"
    
    return "Ismeretlen jutalom típus!"


def ellenorzi_es_ad_achievementet(user, tipus, ertek=1):
    """
    Ellenőrzi és frissíti a játékos achievementjeit.
    
    Args:
        user: User objektum
        tipus: Achievement típusa
        ertek: Növekmény érték (alapértelmezetten 1)
    """
    try:
        # Lekérjük az összes ilyen típusú achievementet
        achievementek = Achievement.objects.filter(tipus=tipus)
        
        for achievement in achievementek:
            # Lekérjük vagy létrehozzuk a játékos achievementjét
            player_ach, created = PlayerAchievement.objects.get_or_create(
                jatekos=user,
                achievement=achievement,
                defaults={'jelenlegi_haladás': 0}
            )
            
            # Ha már teljesítve, nem módosítjuk
            if player_ach.teljesitve:
                continue
            
            # Frissítjük a haladást
            player_ach.jelenlegi_haladás += ertek
            
            # Ha most teljesült, pontokat adunk
            if player_ach.teljesitve:
                try:
                    profile = user.userprofile
                    profile.osszes_pontszam += achievement.pontok
                    profile.save()
                except UserProfile.DoesNotExist:
                    pass
            
            player_ach.save()
            
    except Exception as e:
        # Hibák esetén csendesen továbblépünk
        pass


def frissit_rangsort(user, gyozott):
    """
    Frissíti a játékos rangsor statisztikáit.
    
    Args:
        user: User objektum
        gyozott: Boolean - igaz, ha a játékos nyert
    """
    try:
        profile = user.userprofile
        
        if gyozott:
            profile.gyozelem_hozzaad()
            # Achievementek ellenőrzése
            ellenorzi_es_ad_achievementet(user, 'gyozelem', 1)
            ellenorzi_es_ad_achievementet(user, 'sorozat_gyozelem', 1)
            
            # Sorozat achievementek
            if profile.jelenlegi_sorozat >= 3:
                ellenorzi_es_ad_achievementet(user, '3_sorozat', 0)
            if profile.jelenlegi_sorozat >= 5:
                ellenorzi_es_ad_achievementet(user, '5_sorozat', 0)
            if profile.jelenlegi_sorozat >= 10:
                ellenorzi_es_ad_achievementet(user, '10_sorozat', 0)
        else:
            profile.vereseg_hozzaad()
            ellenorzi_es_ad_achievementet(user, 'vereseg', 1)
            
    except UserProfile.DoesNotExist:
        # Ha nincs profil, létrehozzuk
        UserProfile.objects.create(user=user)


def inicializal_achievementeket():
    """
    Létrehozza az alapértelmezett achievementeket, ha még nem léteznek.
    """
    alapertelmezett_achievementek = [
        # Győzelmek
        {
            'nev': 'Első győzelem',
            'leiras': 'Nyerd meg az első csatádat!',
            'ikon': '🎯',
            'tipus': 'gyozelem',
            'cel_ertek': 1,
            'pontok': 10
        },
        {
            'nev': 'Veterán',
            'leiras': 'Nyerj meg 10 csatát!',
            'ikon': '⚔️',
            'tipus': 'gyozelem',
            'cel_ertek': 10,
            'pontok': 50
        },
        {
            'nev': 'Bajnok',
            'leiras': 'Nyerj meg 50 csatát!',
            'ikon': '👑',
            'tipus': 'gyozelem',
            'cel_ertek': 50,
            'pontok': 200
        },
        {
            'nev': 'Legenda',
            'leiras': 'Nyerj meg 100 csatát!',
            'ikon': '🏆',
            'tipus': 'gyozelem',
            'cel_ertek': 100,
            'pontok': 500
        },
        # Sorozatok
        {
            'nev': 'Lendületben',
            'leiras': 'Nyerj meg 3 csatát egymás után!',
            'ikon': '🔥',
            'tipus': '3_sorozat',
            'cel_ertek': 1,
            'pontok': 25
        },
        {
            'nev': 'Legyőzhetetlen',
            'leiras': 'Nyerj meg 5 csatát egymás után!',
            'ikon': '💪',
            'tipus': '5_sorozat',
            'cel_ertek': 1,
            'pontok': 75
        },
        {
            'nev': 'Halhatatlan',
            'leiras': 'Nyerj meg 10 csatát egymás után!',
            'ikon': '⚡',
            'tipus': '10_sorozat',
            'cel_ertek': 1,
            'pontok': 250
        },
        # Kitartás
        {
            'nev': 'Kitartó',
            'leiras': 'Veszíts el 10 csatát (nem add fel!)',
            'ikon': '💔',
            'tipus': 'vereseg',
            'cel_ertek': 10,
            'pontok': 20
        },
    ]
    
    for ach_data in alapertelmezett_achievementek:
        Achievement.objects.get_or_create(
            nev=ach_data['nev'],
            defaults=ach_data
        )