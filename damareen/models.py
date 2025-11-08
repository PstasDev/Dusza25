from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Felhasználó profil
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    PERMISSION_PLAYER = 'player'
    PERMISSION_MASTER = 'master'

    PERMISSION_CHOICES = [
        (PERMISSION_PLAYER, 'Játékos'),
        (PERMISSION_MASTER, 'Játékmester'),
    ]

    user_type = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default=PERMISSION_PLAYER)
    
    # Rangsor / Leaderboard mezők
    osszes_gyozelem = models.IntegerField(default=0, verbose_name="Összes győzelem")
    osszes_vereseg = models.IntegerField(default=0, verbose_name="Összes vereség")
    legmagasabb_sorozat = models.IntegerField(default=0, verbose_name="Leghosszabb győzelmi sorozat")
    jelenlegi_sorozat = models.IntegerField(default=0, verbose_name="Jelenlegi győzelmi sorozat")
    osszes_pontszam = models.IntegerField(default=0, verbose_name="Összes pontszám")

    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"
    
    def gyozelem_hozzaad(self):
        """Győzelem hozzáadása és sorozat frissítése"""
        self.osszes_gyozelem += 1
        self.jelenlegi_sorozat += 1
        self.osszes_pontszam += 10
        
        if self.jelenlegi_sorozat > self.legmagasabb_sorozat:
            self.legmagasabb_sorozat = self.jelenlegi_sorozat
        
        self.save()
    
    def vereseg_hozzaad(self):
        """Vereség hozzáadása és sorozat nullázása"""
        self.osszes_vereseg += 1
        self.jelenlegi_sorozat = 0
        self.save()
    
    def get_gyozelem_arany(self):
        """Visszaadja a győzelmi arányt százalékban"""
        osszes_harc = self.osszes_gyozelem + self.osszes_vereseg
        if osszes_harc == 0:
            return 0
        return round((self.osszes_gyozelem / osszes_harc) * 100, 1)


# Achievement modell
class Achievement(models.Model):
    nev = models.CharField(max_length=100, unique=True, verbose_name="Név")
    leiras = models.TextField(verbose_name="Leírás")
    ikon = models.CharField(max_length=10, default='🏆', verbose_name="Ikon (emoji)")
    tipus = models.CharField(max_length=50, verbose_name="Típus")
    cel_ertek = models.IntegerField(verbose_name="Cél érték")
    pontok = models.IntegerField(default=10, verbose_name="Pontok")
    
    class Meta:
        verbose_name = "Achievement"
        verbose_name_plural = "Achievementek"
    
    def __str__(self):
        return f"{self.ikon} {self.nev}"


# Játékos achievementjei
class PlayerAchievement(models.Model):
    jatekos = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievementek')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    megszerzve = models.DateTimeField(auto_now_add=True, verbose_name="Megszerzve")
    jelenlegi_haladás = models.IntegerField(default=0, verbose_name="Jelenlegi haladás")
    
    class Meta:
        verbose_name = "Játékos Achievement"
        verbose_name_plural = "Játékos Achievementek"
        unique_together = [['jatekos', 'achievement']]
    
    def __str__(self):
        return f"{self.jatekos.username} - {self.achievement.nev}"
    
    @property
    def teljesitve(self):
        """Igaz, ha az achievement teljesítve van"""
        return self.jelenlegi_haladás >= self.achievement.cel_ertek
    
    def get_haladás_szazalek(self):
        """Visszaadja a haladást százalékban"""
        if self.achievement.cel_ertek == 0:
            return 100
        return min(100, round((self.jelenlegi_haladás / self.achievement.cel_ertek) * 100, 1))


# Elem típusok konstansai
ELEMENT_FIRE = 'tuz'
ELEMENT_EARTH = 'fold'
ELEMENT_WATER = 'viz'
ELEMENT_AIR = 'levego'

ELEMENT_CHOICES = [
    (ELEMENT_FIRE, 'Tűz'),
    (ELEMENT_EARTH, 'Föld'),
    (ELEMENT_WATER, 'Víz'),
    (ELEMENT_AIR, 'Levegő'),
]


# Sima világkártya
class Vilagkartya(models.Model):
    nev = models.CharField(max_length=16, unique=True, verbose_name="Név")
    sebzes = models.IntegerField(
        validators=[MinValueValidator(2), MaxValueValidator(100)],
        verbose_name="Sebzés"
    )
    eletero = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="Életerő"
    )
    tipus = models.CharField(max_length=10, choices=ELEMENT_CHOICES, verbose_name="Típus")
    
    class Meta:
        verbose_name = "Világkártya"
        verbose_name_plural = "Világkártyák"
    
    def __str__(self):
        return f"{self.nev} (S:{self.sebzes}, É:{self.eletero}, {self.get_tipus_display()})"


# Vezérkártya - származtatott a sima kártyából
class Vezerkartya(models.Model):
    DUPLICATION_DAMAGE = 'sebzes'
    DUPLICATION_HP = 'eletero'
    
    DUPLICATION_CHOICES = [
        (DUPLICATION_DAMAGE, 'Sebzés duplázás'),
        (DUPLICATION_HP, 'Életerő duplázás'),
    ]
    
    nev = models.CharField(max_length=16, unique=True, verbose_name="Név")
    eredeti_kartya = models.ForeignKey(Vilagkartya, on_delete=models.CASCADE, verbose_name="Eredeti kártya")
    duplazas_tipusa = models.CharField(max_length=10, choices=DUPLICATION_CHOICES, verbose_name="Duplázás típusa")
    
    class Meta:
        verbose_name = "Vezérkártya"
        verbose_name_plural = "Vezérkártyák"
    
    def __str__(self):
        return f"{self.nev} (Vezér - {self.eredeti_kartya.nev})"
    
    @property
    def sebzes(self):
        if self.duplazas_tipusa == self.DUPLICATION_DAMAGE:
            return self.eredeti_kartya.sebzes * 2
        return self.eredeti_kartya.sebzes
    
    @property
    def eletero(self):
        if self.duplazas_tipusa == self.DUPLICATION_HP:
            return self.eredeti_kartya.eletero * 2
        return self.eredeti_kartya.eletero
    
    @property
    def tipus(self):
        return self.eredeti_kartya.tipus
    
    def get_tipus_display(self):
        return self.eredeti_kartya.get_tipus_display()


# Kazamata
class Kazamata(models.Model):
    TIPUS_EGYSZERU = 'egyszeru'
    TIPUS_KIS = 'kis'
    TIPUS_NAGY = 'nagy'
    
    TIPUS_CHOICES = [
        (TIPUS_EGYSZERU, 'Egyszerű találkozás'),
        (TIPUS_KIS, 'Kis kazamata'),
        (TIPUS_NAGY, 'Nagy kazamata'),
    ]
    
    nev = models.CharField(max_length=100, unique=True, verbose_name="Név")
    tipus = models.CharField(max_length=10, choices=TIPUS_CHOICES, verbose_name="Típus")
    
    class Meta:
        verbose_name = "Kazamata"
        verbose_name_plural = "Kazamaták"
    
    def __str__(self):
        return f"{self.nev} ({self.get_tipus_display()})"
    
    def get_kartyak_szama(self):
        """Visszaadja, hogy hány kártyát tartalmaz a kazamata"""
        if self.tipus == self.TIPUS_EGYSZERU:
            return 1
        elif self.tipus == self.TIPUS_KIS:
            return 4  # 3 sima + 1 vezér
        elif self.tipus == self.TIPUS_NAGY:
            return 6  # 5 sima + 1 vezér
        return 0
    
    def get_nyeremeny_leiras(self):
        """Visszaadja a kazamata legyőzésének jutalmát"""
        if self.tipus == self.TIPUS_EGYSZERU:
            return "+1 sebzés"
        elif self.tipus == self.TIPUS_KIS:
            return "+2 életerő"
        elif self.tipus == self.TIPUS_NAGY:
            return "+3 sebzés"
        return ""


# Kazamata kártyák sorrendje
class KazamataKartya(models.Model):
    kazamata = models.ForeignKey(Kazamata, on_delete=models.CASCADE, related_name='kartyak')
    sorrend = models.IntegerField(verbose_name="Sorrend")
    
    # Lehet sima kártya vagy vezérkártya
    vilag_kartya = models.ForeignKey(Vilagkartya, on_delete=models.CASCADE, null=True, blank=True)
    vezer_kartya = models.ForeignKey(Vezerkartya, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name = "Kazamata kártya"
        verbose_name_plural = "Kazamata kártyák"
        ordering = ['sorrend']
        unique_together = [['kazamata', 'sorrend']]
    
    def __str__(self):
        kartya_nev = self.vilag_kartya.nev if self.vilag_kartya else self.vezer_kartya.nev
        return f"{self.kazamata.nev} - {self.sorrend}. {kartya_nev}"
    
    @property
    def kartya(self):
        """Visszaadja a kártyát (sima vagy vezér)"""
        return self.vilag_kartya if self.vilag_kartya else self.vezer_kartya
    
    @property
    def is_vezer(self):
        """Igaz, ha vezérkártya"""
        return self.vezer_kartya is not None
    
    def get_sebzes(self):
        if self.vilag_kartya:
            return self.vilag_kartya.sebzes
        return self.vezer_kartya.sebzes
    
    def get_eletero(self):
        if self.vilag_kartya:
            return self.vilag_kartya.eletero
        return self.vezer_kartya.eletero
    
    def get_tipus(self):
        if self.vilag_kartya:
            return self.vilag_kartya.tipus
        return self.vezer_kartya.tipus


# Játékkörnyezet
class JatekKornyezet(models.Model):
    nev = models.CharField(max_length=100, unique=True, verbose_name="Név")
    keszitette = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Készítette")
    letrehozva = models.DateTimeField(auto_now_add=True, verbose_name="Létrehozva")
    
    class Meta:
        verbose_name = "Játékkörnyezet"
        verbose_name_plural = "Játékkörnyezetek"
    
    def __str__(self):
        return self.nev


# Játékkörnyezet kezdő gyűjteménye
class GyujtemenyKartya(models.Model):
    kornyezet = models.ForeignKey(JatekKornyezet, on_delete=models.CASCADE, related_name='kezdo_gyujtemeny')
    kartya = models.ForeignKey(Vilagkartya, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Gyűjtemény kártya"
        verbose_name_plural = "Gyűjtemény kártyák"
        unique_together = [['kornyezet', 'kartya']]
    
    def __str__(self):
        return f"{self.kornyezet.nev} - {self.kartya.nev}"


# Játék (egy játékos egy játékkörnyezetben)
class Jatek(models.Model):
    jatekos = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Játékos")
    kornyezet = models.ForeignKey(JatekKornyezet, on_delete=models.CASCADE, verbose_name="Játékkörnyezet")
    inditas = models.DateTimeField(auto_now_add=True, verbose_name="Indítás időpontja")
    utolso_aktivitas = models.DateTimeField(auto_now=True, verbose_name="Utolsó aktivitás")
    
    class Meta:
        verbose_name = "Játék"
        verbose_name_plural = "Játékok"
        unique_together = [['jatekos', 'kornyezet']]
    
    def __str__(self):
        return f"{self.jatekos.username} - {self.kornyezet.nev}"


# Játékos kártyagyűjteménye (fejlődő kártyák)
class Jatekoskartya(models.Model):
    jatek = models.ForeignKey(Jatek, on_delete=models.CASCADE, related_name='gyujtemeny')
    eredeti_kartya = models.ForeignKey(Vilagkartya, on_delete=models.CASCADE)
    
    # Aktuális értékek (fejlődhetnek)
    aktualis_sebzes = models.IntegerField(verbose_name="Aktuális sebzés")
    aktualis_eletero = models.IntegerField(verbose_name="Aktuális életerő")
    
    class Meta:
        verbose_name = "Játékos kártya"
        verbose_name_plural = "Játékos kártyák"
        unique_together = [['jatek', 'eredeti_kartya']]
    
    def __str__(self):
        return f"{self.eredeti_kartya.nev} (S:{self.aktualis_sebzes}, É:{self.aktualis_eletero})"
    
    @property
    def tipus(self):
        return self.eredeti_kartya.tipus
    
    def get_tipus_display(self):
        return self.eredeti_kartya.get_tipus_display()


# Pakli
class Pakli(models.Model):
    jatek = models.OneToOneField(Jatek, on_delete=models.CASCADE, related_name='pakli')
    letrehozva = models.DateTimeField(auto_now=True, verbose_name="Létrehozva")
    
    class Meta:
        verbose_name = "Pakli"
        verbose_name_plural = "Paklik"
    
    def __str__(self):
        return f"{self.jatek.jatekos.username} paklija"
    
    def get_kartyak_szama(self):
        return self.kartyak.count()


# Pakli kártyái
class PakliKartya(models.Model):
    pakli = models.ForeignKey(Pakli, on_delete=models.CASCADE, related_name='kartyak')
    kartya = models.ForeignKey(Jatekoskartya, on_delete=models.CASCADE)
    sorrend = models.IntegerField(verbose_name="Sorrend")
    
    class Meta:
        verbose_name = "Pakli kártya"
        verbose_name_plural = "Pakli kártyák"
        ordering = ['sorrend']
        unique_together = [['pakli', 'sorrend'], ['pakli', 'kartya']]
    
    def __str__(self):
        return f"{self.pakli.jatek.jatekos.username} - {self.sorrend}. {self.kartya.eredeti_kartya.nev}"


# Harc
class Harc(models.Model):
    jatek = models.ForeignKey(Jatek, on_delete=models.CASCADE, related_name='harcok')
    kazamata = models.ForeignKey(Kazamata, on_delete=models.CASCADE)
    inditas = models.DateTimeField(auto_now_add=True, verbose_name="Indítás")
    befejezve = models.BooleanField(default=False, verbose_name="Befejezve")
    jatekos_gyozott = models.BooleanField(null=True, blank=True, verbose_name="Játékos győzött")
    rangsor_frissitve = models.BooleanField(default=False, verbose_name="Rangsor frissítve")
    
    class Meta:
        verbose_name = "Harc"
        verbose_name_plural = "Harcok"
        ordering = ['-inditas']
    
    def __str__(self):
        status = "Folyamatban" if not self.befejezve else ("Győzelem" if self.jatekos_gyozott else "Vereség")
        return f"{self.jatek.jatekos.username} vs {self.kazamata.nev} - {status}"


# Ütközet (egy kártya vs egy kártya a harc során)
class Utközet(models.Model):
    harc = models.ForeignKey(Harc, on_delete=models.CASCADE, related_name='utközetek')
    sorrend = models.IntegerField(verbose_name="Sorrend")
    
    # Játékos kártyája
    jatekos_kartya = models.ForeignKey(Jatekoskartya, on_delete=models.CASCADE)
    jatekos_sebzes = models.IntegerField()
    jatekos_eletero = models.IntegerField()
    jatekos_tipus = models.CharField(max_length=10, choices=ELEMENT_CHOICES)
    
    # Kazamata kártyája
    kazamata_kartya_ref = models.ForeignKey(KazamataKartya, on_delete=models.CASCADE)
    kazamata_sebzes = models.IntegerField()
    kazamata_eletero = models.IntegerField()
    kazamata_tipus = models.CharField(max_length=10, choices=ELEMENT_CHOICES)
    
    # Eredmény
    jatekos_nyert = models.BooleanField(verbose_name="Játékos nyert")
    gyoztes_ok = models.TextField(verbose_name="Győztes oka")
    
    class Meta:
        verbose_name = "Ütközet"
        verbose_name_plural = "Ütközetek"
        ordering = ['sorrend']
    
    def __str__(self):
        eredmeny = "Játékos nyert" if self.jatekos_nyert else "Kazamata nyert"
        return f"Ütközet {self.sorrend}: {eredmeny}"