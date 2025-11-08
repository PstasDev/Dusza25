"""
Damareen játék logika
"""
from .models import (
    ELEMENT_FIRE, ELEMENT_EARTH, ELEMENT_WATER, ELEMENT_AIR,
    Harc, Utközet, Jatekoskartya, PakliKartya
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
