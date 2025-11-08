from django.contrib import admin
from .models import (
    UserProfile, Vilagkartya, Vezerkartya, Kazamata, KazamataKartya,
    JatekKornyezet, GyujtemenyKartya, Jatek, Jatekoskartya,
    Pakli, PakliKartya, Harc, Utközet, Achievement, PlayerAchievement
)


class KazamataKartyaInline(admin.TabularInline):
    model = KazamataKartya
    extra = 1
    fields = ['sorrend', 'vilag_kartya', 'vezer_kartya']


class GyujtemenyKartyaInline(admin.TabularInline):
    model = GyujtemenyKartya
    extra = 1


class PakliKartyaInline(admin.TabularInline):
    model = PakliKartya
    extra = 1


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'osszes_pontszam', 'osszes_gyozelem', 'osszes_vereseg', 'legmagasabb_sorozat']
    list_filter = ['user_type']
    search_fields = ['user__username']
    readonly_fields = ['osszes_pontszam', 'osszes_gyozelem', 'osszes_vereseg', 'legmagasabb_sorozat', 'jelenlegi_sorozat']


@admin.register(Vilagkartya)
class VilagkartyaAdmin(admin.ModelAdmin):
    list_display = ['nev', 'sebzes', 'eletero', 'tipus']
    list_filter = ['tipus']
    search_fields = ['nev']


@admin.register(Vezerkartya)
class VezerkartyaAdmin(admin.ModelAdmin):
    list_display = ['nev', 'eredeti_kartya', 'duplazas_tipusa', 'sebzes', 'eletero']
    list_filter = ['duplazas_tipusa']
    search_fields = ['nev', 'eredeti_kartya__nev']


@admin.register(Kazamata)
class KazamataAdmin(admin.ModelAdmin):
    list_display = ['nev', 'tipus', 'get_kartyak_szama', 'get_nyeremeny_leiras']
    list_filter = ['tipus']
    search_fields = ['nev']
    inlines = [KazamataKartyaInline]


@admin.register(JatekKornyezet)
class JatekKornyezetAdmin(admin.ModelAdmin):
    list_display = ['nev', 'keszitette', 'letrehozva']
    list_filter = ['keszitette', 'letrehozva']
    search_fields = ['nev']
    inlines = [GyujtemenyKartyaInline]


@admin.register(Jatek)
class JatekAdmin(admin.ModelAdmin):
    list_display = ['jatekos', 'kornyezet', 'inditas', 'utolso_aktivitas']
    list_filter = ['jatekos', 'kornyezet', 'inditas']
    search_fields = ['jatekos__username', 'kornyezet__nev']


@admin.register(Jatekoskartya)
class JatekoskartyaAdmin(admin.ModelAdmin):
    list_display = ['jatek', 'eredeti_kartya', 'aktualis_sebzes', 'aktualis_eletero', 'tipus']
    list_filter = ['jatek', 'eredeti_kartya__tipus']
    search_fields = ['eredeti_kartya__nev', 'jatek__jatekos__username']


@admin.register(Pakli)
class PakliAdmin(admin.ModelAdmin):
    list_display = ['jatek', 'get_kartyak_szama', 'letrehozva']
    inlines = [PakliKartyaInline]


@admin.register(Harc)
class HarcAdmin(admin.ModelAdmin):
    list_display = ['jatek', 'kazamata', 'inditas', 'befejezve', 'jatekos_gyozott']
    list_filter = ['befejezve', 'jatekos_gyozott', 'inditas']
    search_fields = ['jatek__jatekos__username', 'kazamata__nev']


@admin.register(Utközet)
class UtközetAdmin(admin.ModelAdmin):
    list_display = ['harc', 'sorrend', 'jatekos_kartya', 'jatekos_nyert']
    list_filter = ['jatekos_nyert']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['nev', 'ikon', 'tipus', 'cel_ertek', 'pontok']
    list_filter = ['tipus']
    search_fields = ['nev', 'leiras']


@admin.register(PlayerAchievement)
class PlayerAchievementAdmin(admin.ModelAdmin):
    list_display = ['jatekos', 'achievement', 'jelenlegi_haladás', 'teljesitve', 'megszerzve']
    list_filter = ['achievement', 'megszerzve']
    search_fields = ['jatekos__username', 'achievement__nev']
    readonly_fields = ['megszerzve']
    
    def teljesitve(self, obj):
        return obj.teljesitve
    teljesitve.boolean = True
    teljesitve.short_description = 'Teljesítve'
