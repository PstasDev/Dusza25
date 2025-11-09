# 🃏 Damareen - Fantasy Kártyajáték

**DUSZA ÁRPÁD ORSZÁGOS PROGRAMOZÓI EMLÉKVERSENY 2025/2026**  
I. forduló (Web verseny) - 2025. november 7-9., déltől-délig

## 📝 Projekt leírása

A Damareen egy gyűjtögetős fantasy kártyajáték, ahol stratégia, szerencse és képzelet találkozik. 
A játékosok saját kártyagyűjteményüket fejlesztik kazamaták ellen vívott harcok során.

## 🚀 Telepítés és indítás

### 1. Előfeltételek
- Python 3.8 vagy újabb
- pip (Python package manager)
- Libraryk telepítése, preferáltan virtualenv-ben. Minden megtalálható a requirements.txt fájlban.

### 2. Projekt előkészítése

```cmd
cd .\Dusza25
```

### 3. Django migrációk futtatása, ha a libraryk már telepítve vannak

```cmd
python manage.py migrate
```

### 4. Superuser létrehozása (admin felülethez)

```cmd
python manage.py createsuperuser
```

Követve a megjelenő utasításokat adj meg felhasználónevet és jelszót.

### 5. Minta játékkörnyezet létrehozása

```cmd
python manage.py create_sample_world
```

Ez létrehoz egy teljes játékvilágot:
- 20 világkártyát (LOTR és Star Wars karakterek)
- 5 vezérkártyát
- 4 kazamatát (Egyszerű, 2 Kis, 1 Nagy)
- Egy "Középfölde kalandjai" nevű játékkörnyezetet kezdő gyűjteménnyel

### 6. Achievementek inicializálása

```cmd
python manage.py init_achievements
```

Ez létrehozza az alapértelmezett achievementeket:
- 4 győzelmi achievement
- 3 sorozat achievement
- 1 kitartás achievement

### 7. Szerver indítása

```cmd
python manage.py runserver
```

Az alkalmazás elérhető lesz: **http://127.0.0.1:8000/**

## 🎮 Használati útmutató

### Szerepkörök

#### 🎲 Játékmester
- **Feladat:** Játékvilágok és környezetek létrehozása
- **Admin felület:** http://127.0.0.1:8000/admin/
  - Világkártyák létrehozása (név, sebzés, életerő, típus)
  - Vezérkártyák származtatása (sebzés vagy életerő duplázás)
  - Kazamaták összeállítása (kártyák sorrendje)
- **Játékmester felület:** Kezdő gyűjtemény beállítása
- **Mindent lehet a felhasználói felületen is kezelni, nem kell a Django Admint használni.**

#### 🎮 Játékos
1. **Játék indítása:** Válassz egy játékkörnyezetet
2. **Pakli összeállítása:** Válaszd ki kártyáidat a gyűjteményből
3. **Harc:** Válassz kazamatát (pakli méret = kazamata méret)
4. **Győzelem esetén:** Választhatsz egy kártyát fejlesztésre

### Harc szabályok

#### Ütközet kiértékelése (kártya vs kártya):
1. **Sebzés vs Életerő:** Ha az egyik kártya sebzése nagyobb, mint a másik életereje → nyer
2. **Típus előny:** 
   - 🔥 Tűz > 🌍 Föld
   - 🌍 Föld > 💧 Víz  
   - 💧 Víz > 💨 Levegő
   - 💨 Levegő > 🔥 Tűz
3. **Döntetlen:** Kazamata nyer

#### Harc eredménye:
A játékos akkor nyer, ha legalább annyi kártyája győzött, mint amennyi kártya van a kazamatában.

### Kazamata típusok és jutalmak:

| Típus | Kártyák | Jutalom |
|-------|---------|---------|
| **Egyszerű találkozás** | 1 sima | +1 sebzés |
| **Kis kazamata** | 3 sima + 1 vezér | +2 életerő |
| **Nagy kazamata** | 5 sima + 1 vezér | +3 sebzés |

## 📂 Projekt struktúra

```
Dusza25/
├── damareen/               # Fő alkalmazás
│   ├── models.py          # Adatmodellek
│   ├── views.py           # Nézetek
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin konfiguráció
│   ├── game_logic.py      # Játéklogika
│   ├── templates/         # HTML sablonok
│   └── management/        # Management commandok
│       └── commands/
│           └── create_sample_world.py
├── dusza25/               # Django projekt beállítások
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3            # Adatbázis
└── manage.py             # Django management script
```

## 🎯 Implementált funkciók

### ✅ Teljes mértékben elkészült

1. **Adatmodellek:**
   - ✅ Vilagkartya (név, sebzés, életerő, típus)
   - ✅ Vezerkartya (származtatás sebzés/életerő duplázással)
   - ✅ Kazamata (3 típus, kártyák sorrendje)
   - ✅ JatekKornyezet (világ + gyűjtemény)
   - ✅ Jatek (játékos játéka)
   - ✅ Jatekoskartya (fejlődő gyűjtemény)
   - ✅ Pakli (kártyák sorrendje)
   - ✅ Harc és Utközet (részletes nyilvántartás)

2. **Játéklogika:**
   - ✅ Elem előny számítás (Tűz>Föld>Víz>Levegő>Tűz)
   - ✅ Ütközet kiértékelés (sebzés vs életerő, típus, döntetlen)
   - ✅ Harc végrehajtása
   - ✅ Jutalmak alkalmazása

3. **Felhasználói felület:**
   - ✅ Regisztráció és bejelentkezés
   - ✅ Játékmester műszerfal
   - ✅ Játékkörnyezet létrehozása/szerkesztése
   - ✅ Játékos műszerfal
   - ✅ Játék indítása
   - ✅ Pakli összeállítása (vizuális kártyák)
   - ✅ Harc indítása
   - ✅ Harc eredmény megjelenítése (részletes ütközetek)
   - ✅ Jutalom választása
   - ✅ Reszponzív, esztétikus dizájn

4. **Admin funkciók:**
   - ✅ Teljes CRUD műveletek minden modellre
   - ✅ Inline szerkesztés (kazamata kártyák, gyűjtemény)
   - ✅ Keresés és szűrés

5. **Egyéb:**
   - ✅ Minta adatok generálása (create_sample_world)
   - ✅ Hibakezelés
   - ✅ User-friendly üzenetek
   - ✅ Folyamatban lévő játékok mentése

## 🎨 Plusz szolgáltatások

1. **Vizuális elemek:**
   - 🎨 Kártyák színes megjelenítése típus szerint
   - 🎨 Gradient háttér
   - 🎨 Animációk (hover effektek)
   - 🎨 Emoji ikonok

2. **Felhasználói élmény:**
   - ✨ Részletes harc kiértékelés (minden ütközet látható)
   - ✨ Jutalom előnézet (fejlesztés után várható érték)
   - ✨ Pakli vizuális összeállítás sorrend jelöléssel
   - ✨ Utolsó harcok története
   - ✨ Kazamata szűrés pakli méret alapján

3. **Technikai:**
   - 🔧 Django admin testreszabás
   - 🔧 Management command minta adatokhoz
   - 🔧 Tranzakció-biztos műveletek
   - 🔧 Optimalizált adatbázis lekérdezések

4. **Rangsor és Achievementek:** 🆕
   - 🏆 **Rangsor rendszer:** Legjobb 50 játékos listája pontszám alapján
   - 📊 **Statisztikák:** Győzelmek, vereségek, győzelmi arány, sorozatok
   - ⭐ **Achievement rendszer:** 8 különböző achievement kategória
   - 🎯 **Haladás követés:** Részletes progress bar minden achievementnél
   - 🥇 **Érmek és rangok:** Első 3 helyezett különleges kiemelése
   - 💎 **Pontrendszer:** Achievementek és győzelmek pontokat adnak

## 🏆 Rangsor és Achievementek

### Rangsor Funkciók
- **Top 50 játékos** megjelenítése pontszám szerint rangsorolva
- **Saját rang** kijelzése és kiemelése a listában
- **Részletes statisztikák:**
  - Összes pontszám (achievementek + győzelmek)
  - Győzelmek és vereségek száma
  - Győzelmi arány (%)
  - Leghosszabb győzelmi sorozat
- **Vizuális kiemelés:** Arany/ezüst/bronz érmek az első 3 helyen
- **Színkódolt eredmények:** Win rate alapján zöld/sárga/piros jelzés

### Achievement Rendszer

#### Elérhető Achievementek:

**Győzelem Achievementek:**
- 🎯 **Első győzelem** - Nyerd meg az első csatádat! (10 pont)
- ⚔️ **Veterán** - Nyerj meg 10 csatát! (50 pont)
- 👑 **Bajnok** - Nyerj meg 50 csatát! (200 pont)
- 🏆 **Legenda** - Nyerj meg 100 csatát! (500 pont)

**Győzelmi Sorozat Achievementek:**
- 🔥 **Lendületben** - Nyerj meg 3 csatát egymás után! (25 pont)
- 💪 **Legyőzhetetlen** - Nyerj meg 5 csatát egymás után! (75 pont)
- ⚡ **Halhatatlan** - Nyerj meg 10 csatát egymás után! (250 pont)

**Kitartás Achievement:**
- 💔 **Kitartó** - Veszíts el 10 csatát, de ne add fel! (20 pont)

#### Achievement Jellemzők:
- **Automatikus követés:** A játék automatikusan frissíti a haladást
- **Progress bar:** Vizuális visszajelzés az előrehaladásról
- **Dátum jelzés:** Minden teljesített achievementnél megjelenik a megszerzés időpontja
- **Pontjutalom:** Teljesítéskor automatikus pontszám növelés
- **Szűrt nézet:** Teljesített/nem teljesített achievementek elkülönítése

### Hogyan Működik?

1. **Harc után automatikus frissítés:**
   - Győzelem esetén: +10 pont, győzelmi sorozat növelése
   - Vereség esetén: sorozat nullázása
   - Achievement haladás frissítése

2. **Rangsor számítás:**
   - Pontszám = (Győzelmek × 10) + Achievement pontok
   - Rangsorolás: Pontszám > Győzelmek száma

3. **Achievement teljesítés:**
   - Automatikus felismerés célérték elérésekor
   - Egyszeri pontjutalom
   - Permanens megjelenítés teljesítettként

### Elérés:
- **Rangsor:** Navigációs menü → 🏆 Rangsor
- **Achievementek:** Navigációs menü → ⭐ Achievementek
- Vagy a játékos műszerfalról az újábból

## ❌ Nem implementált funkciók

Nincs, minden feladat követelmény teljesült!

**Plusz implementált funkciók:**
- ✅ Rangsor rendszer (legjobb 50 játékos)
- ✅ Achievement rendszer (8 achievement kategória)
- ✅ Automatikus statisztika követés
- ✅ Pontrendszer és jutalmak

## 🐛 Hibakezelés

- Pakli és kazamata méret ellenőrzése
- Felhasználói jogosultságok ellenőrzése
- Hibás input kezelése
- Nem létező objektumok kezelése (404)
- Tranzakciók használata konzisztencia biztosítására

## 😱 Fejlesztési folyamat során felmerülő problémák 

- Szándékosan olyan technológiákat használtunk, melyeket már jól ismerünk típushibáit már korábbi projektekben kiaknáztuk.
    - Ezen okból lehet különös, hogy static fájlokat **nem** kezelünk, hanem bele vannak templatelve a html fájlokba, így sokkal gyorsabb deployolni stabilan, nem kell a static kezelést külön beállítani.
- Az animációk elkészítése, különösen a BattleArenába nehézkes volt, de igyekeztünk látványosat alkotni.
- Nem futottunk egyéb problémákba.

## 🔮 Továbbfejlesztési lehetőségek

1. **Multiplayer mód:** Játékosok egymás ellen
2. ~~**Rangsor:** Legjobb játékosok listája~~ ✅ **IMPLEMENTÁLVA**
3. ~~**Achievementek:** Teljesítmények gyűjtése~~ ✅ **IMPLEMENTÁLVA**
4. **Kártya animációk:** Harc során animált ütközetek
5. **Export/Import:** Játékkörnyezetek megosztása
6. **Statisztikák:** Játékos teljesítmény grafikonok
7. **Storyline:** Küldetés rendszer
8. **Deck builder AI:** Automatikus pakli javaslat
9. **Real-time battles:** WebSocket használatával
10. **Kártya trading:** Játékosok közötti csere

## 👥 Készítette

Ílllyj - 2025
(mi sem tudjuk leírni a csapatnevünket, mert elfelejtettük)

Kőbányai Szent László Gimnázium, 10. F (23F), 2025. 11. 07-09.

- Balla Botond
- Balla Letícia (igen ikrek vagyunk)
- Szabó Réka Hanna

---

**Jó játékot! 🎮**
