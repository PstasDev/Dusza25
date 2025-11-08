from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.db.models import Max

from .models import (
    UserProfile, JatekKornyezet, Jatek, Jatekoskartya,
    Pakli, PakliKartya, Kazamata, Harc, Vilagkartya,
    Vezerkartya, GyujtemenyKartya, KazamataKartya,
    Achievement, PlayerAchievement,
    ELEMENT_FIRE, ELEMENT_EARTH, ELEMENT_WATER, ELEMENT_AIR
)
from .game_logic import harc_vegrehajtasa, jutalom_alkalmazasa, frissit_rangsort
from .forms import KazamataForm, VilagkartyaForm, VezerkartyaForm


def index(request):
    """Főoldal"""
    return render(request, 'damareen/index.html')


def user_login(request):
    """Bejelentkezés"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Üdvözöl a Damareen, {user.username}!')
            return redirect('damareen:index')
        else:
            messages.error(request, 'Hibás felhasználónév vagy jelszó!')
    
    return render(request, 'damareen/login.html')


def user_logout(request):
    """Kijelentkezés"""
    logout(request)
    messages.info(request, 'Sikeresen kijelentkeztél!')
    return redirect('damareen:index')


def user_register(request):
    """Regisztráció"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        user_type = request.POST.get('user_type', UserProfile.PERMISSION_PLAYER)
        
        if password != password2:
            messages.error(request, 'A jelszavak nem egyeznek!')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ez a felhasználónév már foglalt!')
        else:
            user = User.objects.create_user(username=username, password=password)
            UserProfile.objects.create(user=user, user_type=user_type)
            messages.success(request, 'Sikeres regisztráció! Most már bejelentkezhetsz.')
            return redirect('damareen:login')
    
    return render(request, 'damareen/register.html')


@login_required
def master_dashboard(request):
    """Játékmester műszerfal"""
    kornyezetek = JatekKornyezet.objects.filter(keszitette=request.user)
    vilag_kartyak = Vilagkartya.objects.all()
    vezer_kartyak = Vezerkartya.objects.all()
    kazamatak = Kazamata.objects.all()
    
    return render(request, 'damareen/master/dashboard.html', {
        'kornyezetek': kornyezetek,
        'vilag_kartyak': vilag_kartyak,
        'vezer_kartyak': vezer_kartyak,
        'kazamatak': kazamatak,
    })


@login_required
def create_kornyezet(request):
    """Új játékkörnyezet létrehozása"""
    if request.method == 'POST':
        nev = request.POST.get('nev')
        
        # Játékkörnyezet létrehozása
        kornyezet = JatekKornyezet.objects.create(
            nev=nev,
            keszitette=request.user
        )
        
        messages.success(request, f'Játékkörnyezet "{nev}" létrehozva!')
        return redirect('damareen:view_kornyezet', kornyezet_id=kornyezet.id)
    
    vilag_kartyak = Vilagkartya.objects.all()
    return render(request, 'damareen/master/create_kornyezet.html', {
        'vilag_kartyak': vilag_kartyak
    })


@login_required
def view_kornyezet(request, kornyezet_id):
    """Játékkörnyezet megtekintése"""
    kornyezet = get_object_or_404(JatekKornyezet, id=kornyezet_id, keszitette=request.user)
    
    if request.method == 'POST':
        # Kezdő gyűjtemény frissítése
        valasztott_kartyak = request.POST.getlist('kartyak')
        GyujtemenyKartya.objects.filter(kornyezet=kornyezet).delete()
        
        for kartya_id in valasztott_kartyak:
            GyujtemenyKartya.objects.create(
                kornyezet=kornyezet,
                kartya_id=kartya_id
            )
        
        messages.success(request, 'Kezdő gyűjtemény frissítve!')
    
    vilag_kartyak = Vilagkartya.objects.all()
    kezdo_gyujtemeny = kornyezet.kezdo_gyujtemeny.all()
    kazamatak = Kazamata.objects.all()
    
    return render(request, 'damareen/master/view_kornyezet.html', {
        'kornyezet': kornyezet,
        'vilag_kartyak': vilag_kartyak,
        'kezdo_gyujtemeny': kezdo_gyujtemeny,
        'kazamatak': kazamatak
    })


@login_required
def player_dashboard(request):
    """Játékos műszerfal"""
    jatekok = Jatek.objects.filter(jatekos=request.user)
    kornyezetek = JatekKornyezet.objects.all()
    
    return render(request, 'damareen/player/dashboard.html', {
        'jatekok': jatekok,
        'kornyezetek': kornyezetek
    })


@login_required
@transaction.atomic
def start_game(request, kornyezet_id):
    """Új játék indítása"""
    kornyezet = get_object_or_404(JatekKornyezet, id=kornyezet_id)
    
    # Ellenőrizzük, hogy van-e már játék ezzel a környezettel
    jatek, created = Jatek.objects.get_or_create(
        jatekos=request.user,
        kornyezet=kornyezet
    )
    
    if created:
        # Kezdő gyűjtemény másolása
        for gyujtemeny_kartya in kornyezet.kezdo_gyujtemeny.all():
            Jatekoskartya.objects.create(
                jatek=jatek,
                eredeti_kartya=gyujtemeny_kartya.kartya,
                aktualis_sebzes=gyujtemeny_kartya.kartya.sebzes,
                aktualis_eletero=gyujtemeny_kartya.kartya.eletero
            )
        messages.success(request, f'Új játék indítva: {kornyezet.nev}')
    else:
        messages.info(request, 'Folytatod a megkezdett játékot.')
    
    return redirect('damareen:game_view', jatek_id=jatek.id)


@login_required
def game_view(request, jatek_id):
    """Játék nézet"""
    jatek = get_object_or_404(Jatek, id=jatek_id, jatekos=request.user)
    gyujtemeny = jatek.gyujtemeny.all()
    pakli = None
    
    try:
        pakli = jatek.pakli
    except Pakli.DoesNotExist:
        pass
    
    kazamatak = Kazamata.objects.all()
    utolso_harcok = jatek.harcok.filter(befejezve=True).order_by('-inditas')[:5]
    
    return render(request, 'damareen/player/game_view.html', {
        'jatek': jatek,
        'gyujtemeny': gyujtemeny,
        'pakli': pakli,
        'kazamatak': kazamatak,
        'utolso_harcok': utolso_harcok
    })


@login_required
@transaction.atomic
def pakli_osszeallit(request, jatek_id):
    """Pakli összeállítása"""
    jatek = get_object_or_404(Jatek, id=jatek_id, jatekos=request.user)
    
    if request.method == 'POST':
        valasztott_kartyak = request.POST.getlist('kartyak')
        
        if not valasztott_kartyak:
            messages.error(request, 'Válassz ki legalább egy kártyát!')
            return redirect('damareen:pakli_osszeallit', jatek_id=jatek_id)
        
        # Régi pakli törlése
        try:
            jatek.pakli.delete()
        except Pakli.DoesNotExist:
            pass
        
        # Új pakli létrehozása
        pakli = Pakli.objects.create(jatek=jatek)
        
        for i, kartya_id in enumerate(valasztott_kartyak):
            PakliKartya.objects.create(
                pakli=pakli,
                kartya_id=kartya_id,
                sorrend=i + 1
            )
        
        messages.success(request, f'Pakli összeállítva {len(valasztott_kartyak)} kártyával!')
        return redirect('damareen:game_view', jatek_id=jatek_id)
    
    gyujtemeny = jatek.gyujtemeny.all()
    return render(request, 'damareen/player/pakli_osszeallit.html', {
        'jatek': jatek,
        'gyujtemeny': gyujtemeny
    })


@login_required
@transaction.atomic
def harc_indit(request, jatek_id, kazamata_id):
    """Harc indítása - új: WebSocket alapú real-time battle"""
    jatek = get_object_or_404(Jatek, id=jatek_id, jatekos=request.user)
    kazamata = get_object_or_404(Kazamata, id=kazamata_id)
    
    # Ellenőrizzük, hogy van-e pakli
    try:
        pakli = jatek.pakli
    except Pakli.DoesNotExist:
        messages.error(request, '❌ Először állíts össze egy paklit!')
        return redirect('damareen:game_view', jatek_id=jatek_id)
    
    # Ellenőrizzük a kártyák számát
    pakli_meret = pakli.get_kartyak_szama()
    kazamata_meret = kazamata.get_kartyak_szama()
    
    if pakli_meret != kazamata_meret:
        messages.error(request, 
            f'❌ A paklidban {pakli_meret} kártya van, de a kazamatához {kazamata_meret} kell!')
        return redirect('damareen:game_view', jatek_id=jatek_id)
    
    # Redirect to WebSocket battle arena
    return redirect('damareen:battle_arena', jatek_id=jatek_id, kazamata_id=kazamata_id)


@login_required
def battle_arena(request, jatek_id, kazamata_id):
    """Real-time battle arena with WebSocket"""
    jatek = get_object_or_404(Jatek, id=jatek_id, jatekos=request.user)
    kazamata = get_object_or_404(Kazamata, id=kazamata_id)
    
    return render(request, 'damareen/player/battle_arena.html', {
        'jatek': jatek,
        'kazamata': kazamata
    })


@login_required
def harc_eredmeny(request, jatek_id, harc_id):
    """Harc eredményének megtekintése"""
    jatek = get_object_or_404(Jatek, id=jatek_id, jatekos=request.user)
    harc = get_object_or_404(Harc, id=harc_id, jatek=jatek)
    
    # Rangsor frissítése (csak egyszer)
    if harc.befejezve and not harc.rangsor_frissitve:
        frissit_rangsort(request.user, harc.jatekos_gyozott)
        harc.rangsor_frissitve = True
        harc.save(update_fields=['rangsor_frissitve'])
    
    utközetek = harc.utközetek.all()
    
    return render(request, 'damareen/player/harc_eredmeny.html', {
        'jatek': jatek,
        'harc': harc,
        'utközetek': utközetek
    })


@login_required
@transaction.atomic
def jutalom_valaszt(request, jatek_id, harc_id):
    """Jutalom kártya választása"""
    jatek = get_object_or_404(Jatek, id=jatek_id, jatekos=request.user)
    harc = get_object_or_404(Harc, id=harc_id, jatek=jatek)
    
    if not harc.jatekos_gyozott:
        messages.error(request, 'Csak győzelem esetén kaphatsz jutalmat!')
        return redirect('damareen:game_view', jatek_id=jatek_id)
    
    if request.method == 'POST':
        kartya_id = request.POST.get('kartya_id')
        
        try:
            uzenet = jutalom_alkalmazasa(jatek, harc.kazamata, kartya_id)
            messages.success(request, uzenet)
            return redirect('damareen:game_view', jatek_id=jatek_id)
        except Exception as e:
            messages.error(request, f'Hiba: {str(e)}')
    
    gyujtemeny = jatek.gyujtemeny.all()
    
    return render(request, 'damareen/player/jutalom_valaszt.html', {
        'jatek': jatek,
        'harc': harc,
        'gyujtemeny': gyujtemeny
    })


# ============= JÁTÉKMESTER FUNKCIÓK (Admin nélkül) =============

@login_required
def manage_vilagkartyak(request):
    """Világkártyák kezelése"""
    kartyak = Vilagkartya.objects.all().order_by('nev')
    
    return render(request, 'damareen/master/manage_vilagkartyak.html', {
        'kartyak': kartyak
    })


@login_required
@transaction.atomic
def create_vilagkartya(request):
    """Új világkártya létrehozása"""
    if request.method == 'POST':
        form = VilagkartyaForm(request.POST)
        if form.is_valid():
            kartya = form.save()
            messages.success(request, f'Világkártya "{kartya.nev}" létrehozva!')
            return redirect('damareen:manage_vilagkartyak')
    else:
        form = VilagkartyaForm()
    
    return render(request, 'damareen/master/create_vilagkartya.html', {
        'form': form
    })


@login_required
@transaction.atomic
def edit_vilagkartya(request, kartya_id):
    """Világkártya szerkesztése"""
    kartya = get_object_or_404(Vilagkartya, id=kartya_id)
    
    if request.method == 'POST':
        form = VilagkartyaForm(request.POST, instance=kartya)
        if form.is_valid():
            form.save()
            messages.success(request, f'Világkártya "{kartya.nev}" frissítve!')
            return redirect('damareen:manage_vilagkartyak')
    else:
        form = VilagkartyaForm(instance=kartya)
    
    return render(request, 'damareen/master/edit_vilagkartya.html', {
        'kartya': kartya,
        'form': form
    })


@login_required
@transaction.atomic
def delete_vilagkartya(request, kartya_id):
    """Világkártya törlése"""
    kartya = get_object_or_404(Vilagkartya, id=kartya_id)
    
    if request.method == 'POST':
        nev = kartya.nev
        kartya.delete()
        messages.success(request, f'Világkártya "{nev}" törölve!')
        return redirect('damareen:manage_vilagkartyak')
    
    return render(request, 'damareen/master/delete_vilagkartya.html', {
        'kartya': kartya
    })


@login_required
def manage_vezerkartyak(request):
    """Vezérkártyák kezelése"""
    kartyak = Vezerkartya.objects.all().order_by('nev')
    
    return render(request, 'damareen/master/manage_vezerkartyak.html', {
        'kartyak': kartyak
    })


@login_required
@transaction.atomic
def create_vezerkartya(request):
    """Új vezérkártya létrehozása"""
    if request.method == 'POST':
        form = VezerkartyaForm(request.POST)
        if form.is_valid():
            kartya = form.save()
            messages.success(request, f'Vezérkártya "{kartya.nev}" létrehozva!')
            return redirect('damareen:manage_vezerkartyak')
    else:
        form = VezerkartyaForm()
    
    vilag_kartyak = Vilagkartya.objects.all().order_by('nev')
    
    return render(request, 'damareen/master/create_vezerkartya.html', {
        'form': form,
        'vilag_kartyak': vilag_kartyak
    })


@login_required
@transaction.atomic
def delete_vezerkartya(request, kartya_id):
    """Vezérkártya törlése"""
    kartya = get_object_or_404(Vezerkartya, id=kartya_id)
    
    if request.method == 'POST':
        nev = kartya.nev
        kartya.delete()
        messages.success(request, f'Vezérkártya "{nev}" törölve!')
        return redirect('damareen:manage_vezerkartyak')
    
    return render(request, 'damareen/master/delete_vezerkartya.html', {
        'kartya': kartya
    })


@login_required
def manage_kazamatak(request):
    """Kazamaták kezelése"""
    kazamatak = Kazamata.objects.all().order_by('nev')
    
    return render(request, 'damareen/master/manage_kazamatak.html', {
        'kazamatak': kazamatak
    })


@login_required
@transaction.atomic
def create_kazamata(request):
    """Új kazamata létrehozása"""
    if request.method == 'POST':
        form = KazamataForm(request.POST)
        if form.is_valid():
            kazamata = form.save()
            messages.success(request, f'Kazamata "{kazamata.nev}" létrehozva! Most add hozzá a kártyákat.')
            return redirect('damareen:edit_kazamata', kazamata_id=kazamata.id)
    else:
        form = KazamataForm()
    
    return render(request, 'damareen/master/create_kazamata.html', {
        'form': form
    })


@login_required
@transaction.atomic
def edit_kazamata(request, kazamata_id):
    """Kazamata szerkesztése (kártyák hozzáadása/törlése)"""
    kazamata = get_object_or_404(Kazamata, id=kazamata_id)
    
    if request.method == 'POST':
        # Kártya eltávolítása
        if 'remove_card' in request.POST:
            kazamata_kartya_id = request.POST.get('remove_card')
            try:
                KazamataKartya.objects.get(id=kazamata_kartya_id).delete()
                messages.success(request, 'Kártya eltávolítva!')
            except Exception as e:
                messages.error(request, f'Hiba: {str(e)}')
            return redirect('damareen:edit_kazamata', kazamata_id=kazamata_id)
        
        # Normál kártya hozzáadása
        if 'add_normal_card' in request.POST:
            vilag_kartya_id = request.POST.get('add_normal_card')
            try:
                vilag_kartya = Vilagkartya.objects.get(id=vilag_kartya_id)
                # Következő sorrend meghatározása
                max_sorrend = kazamata.kartyak.aggregate(Max('sorrend'))['sorrend__max'] or 0
                KazamataKartya.objects.create(
                    kazamata=kazamata,
                    sorrend=max_sorrend + 1,
                    vilag_kartya=vilag_kartya
                )
                messages.success(request, f'"{vilag_kartya.nev}" hozzáadva!')
            except Exception as e:
                messages.error(request, f'Hiba: {str(e)}')
            return redirect('damareen:edit_kazamata', kazamata_id=kazamata_id)
        
        # Vezérkártya hozzáadása
        if 'add_leader_card' in request.POST:
            vezer_kartya_id = request.POST.get('add_leader_card')
            try:
                vezer_kartya = Vezerkartya.objects.get(id=vezer_kartya_id)
                # Következő sorrend meghatározása
                max_sorrend = kazamata.kartyak.aggregate(Max('sorrend'))['sorrend__max'] or 0
                KazamataKartya.objects.create(
                    kazamata=kazamata,
                    sorrend=max_sorrend + 1,
                    vezer_kartya=vezer_kartya
                )
                messages.success(request, f'Vezér "{vezer_kartya.nev}" hozzáadva!')
            except Exception as e:
                messages.error(request, f'Hiba: {str(e)}')
            return redirect('damareen:edit_kazamata', kazamata_id=kazamata_id)
        
        # Alapadatok módosítása
        form = KazamataForm(request.POST, instance=kazamata)
        if form.is_valid():
            # Ha típus változott, töröljük a kártyákat
            if form.cleaned_data['tipus'] != kazamata.tipus:
                kazamata.kartyak.all().delete()
                messages.warning(request, 'A típus megváltozott, az összes kártya törölve!')
            form.save()
            messages.success(request, 'Kazamata módosítva!')
            return redirect('damareen:edit_kazamata', kazamata_id=kazamata_id)
    else:
        form = KazamataForm(instance=kazamata)
    
    # Kártyák lekérdezése
    vilag_kartyak = Vilagkartya.objects.all().order_by('nev')
    vezer_kartyak = Vezerkartya.objects.all().order_by('nev')
    
    # Kapacitás számítás
    if kazamata.tipus == Kazamata.TIPUS_EGYSZERU:
        max_normalis = 1
        max_vezer = 0
        max_kartyak = 1
    elif kazamata.tipus == Kazamata.TIPUS_KIS:
        max_normalis = 3
        max_vezer = 1
        max_kartyak = 4
    else:  # NAGY
        max_normalis = 5
        max_vezer = 1
        max_kartyak = 6
    
    # Jelenlegi kártyák száma
    current_normal = kazamata.kartyak.filter(vilag_kartya__isnull=False).count()
    current_leader = kazamata.kartyak.filter(vezer_kartya__isnull=False).count()
    
    can_add_normal = current_normal < max_normalis
    can_add_leader = (max_vezer > 0) and (current_leader < max_vezer)
    
    return render(request, 'damareen/master/edit_kazamata.html', {
        'kazamata': kazamata,
        'form': form,
        'vilag_kartyak': vilag_kartyak,
        'vezer_kartyak': vezer_kartyak,
        'max_kartyak': max_kartyak,
        'can_add_normal': can_add_normal,
        'can_add_leader': can_add_leader,
    })


@login_required
@transaction.atomic
def delete_kazamata(request, kazamata_id):
    """Kazamata törlése"""
    kazamata = get_object_or_404(Kazamata, id=kazamata_id)
    
    if request.method == 'POST':
        nev = kazamata.nev
        kazamata.delete()
        messages.success(request, f'Kazamata "{nev}" törölve!')
        return redirect('damareen:manage_kazamatak')
    
    return render(request, 'damareen/master/delete_kazamata.html', {
        'kazamata': kazamata
    })


# ============= RANGSOR ÉS ACHIEVEMENTEK =============

def leaderboard(request):
    """Rangsor - legjobb játékosok listája"""
    # Top 50 játékos pontszám szerint
    top_players = UserProfile.objects.filter(
        user_type=UserProfile.PERMISSION_PLAYER
    ).select_related('user').order_by('-osszes_pontszam', '-osszes_gyozelem')[:50]
    
    # Aktuális felhasználó rangja
    current_user_rank = None
    current_user_profile = None
    
    if request.user.is_authenticated:
        try:
            current_user_profile = request.user.userprofile
            # Megkeressük a rangját
            all_profiles = UserProfile.objects.filter(
                user_type=UserProfile.PERMISSION_PLAYER
            ).order_by('-osszes_pontszam', '-osszes_gyozelem')
            
            for idx, profile in enumerate(all_profiles, 1):
                if profile.user == request.user:
                    current_user_rank = idx
                    break
        except UserProfile.DoesNotExist:
            pass
    
    return render(request, 'damareen/leaderboard.html', {
        'top_players': top_players,
        'current_user_rank': current_user_rank,
        'current_user_profile': current_user_profile
    })


@login_required
def my_achievements(request):
    """Saját achievementek megtekintése"""
    # Összes achievement
    all_achievements = Achievement.objects.all().order_by('cel_ertek', 'nev')
    
    # Játékos achievementjei
    player_achievements = PlayerAchievement.objects.filter(
        jatekos=request.user
    ).select_related('achievement')
    
    #Dict létrehozása gyors kereséshez
    player_ach_dict = {pa.achievement.id: pa for pa in player_achievements}
    
    # Achievement lista előkészítése haladással
    achievements_with_progress = []
    for achievement in all_achievements:
        player_ach = player_ach_dict.get(achievement.id)
        
        if player_ach:
            achievements_with_progress.append({
                'achievement': achievement,
                'haladás': player_ach.jelenlegi_haladás,
                'teljesitve': player_ach.teljesitve,
                'szazalek': player_ach.get_haladás_szazalek(),
                'megszerzve': player_ach.megszerzve if player_ach.teljesitve else None
            })
        else:
            achievements_with_progress.append({
                'achievement': achievement,
                'haladás': 0,
                'teljesitve': False,
                'szazalek': 0,
                'megszerzve': None
            })
    
    # Statisztikák
    teljesitett_szam = sum(1 for a in achievements_with_progress if a['teljesitve'])
    osszes_szam = len(achievements_with_progress)
    
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = None
    
    return render(request, 'damareen/achievements.html', {
        'achievements': achievements_with_progress,
        'teljesitett_szam': teljesitett_szam,
        'osszes_szam': osszes_szam,
        'profile': profile
    })
