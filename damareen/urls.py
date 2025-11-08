"""
Damareen URL Configuration
"""
from django.urls import path
from . import views

app_name = 'damareen'

urlpatterns = [
    # Főoldal
    path('', views.index, name='index'),
    
    # Játékmester nézetek
    path('master/', views.master_dashboard, name='master_dashboard'),
    path('master/kornyezet/create/', views.create_kornyezet, name='create_kornyezet'),
    path('master/kornyezet/<int:kornyezet_id>/', views.view_kornyezet, name='view_kornyezet'),
    
    # Világkártyák kezelése
    path('master/vilagkartyak/', views.manage_vilagkartyak, name='manage_vilagkartyak'),
    path('master/vilagkartyak/create/', views.create_vilagkartya, name='create_vilagkartya'),
    path('master/vilagkartyak/<int:kartya_id>/edit/', views.edit_vilagkartya, name='edit_vilagkartya'),
    path('master/vilagkartyak/<int:kartya_id>/delete/', views.delete_vilagkartya, name='delete_vilagkartya'),
    
    # Vezérkártyák kezelése
    path('master/vezerkartyak/', views.manage_vezerkartyak, name='manage_vezerkartyak'),
    path('master/vezerkartyak/create/', views.create_vezerkartya, name='create_vezerkartya'),
    path('master/vezerkartyak/<int:kartya_id>/delete/', views.delete_vezerkartya, name='delete_vezerkartya'),
    
    # Kazamaták kezelése
    path('master/kazamatak/', views.manage_kazamatak, name='manage_kazamatak'),
    path('master/kazamatak/create/', views.create_kazamata, name='create_kazamata'),
    path('master/kazamatak/<int:kazamata_id>/edit/', views.edit_kazamata, name='edit_kazamata'),
    path('master/kazamatak/<int:kazamata_id>/delete/', views.delete_kazamata, name='delete_kazamata'),
    
    # Játékos nézetek
    path('player/', views.player_dashboard, name='player_dashboard'),
    path('player/jatek/start/<int:kornyezet_id>/', views.start_game, name='start_game'),
    path('player/jatek/<int:jatek_id>/', views.game_view, name='game_view'),
    path('player/jatek/<int:jatek_id>/pakli/', views.pakli_osszeallit, name='pakli_osszeallit'),
    path('player/jatek/<int:jatek_id>/harc/<int:kazamata_id>/', views.harc_indit, name='harc_indit'),
    path('player/game/<int:jatek_id>/battle/<int:kazamata_id>/', views.battle_arena, name='battle_arena'),
    path('player/jatek/<int:jatek_id>/harc/<int:harc_id>/eredmeny/', views.harc_eredmeny, name='harc_eredmeny'),
    path('player/game/<int:jatek_id>/harc/<int:harc_id>/jutalom/', views.jutalom_valaszt, name='jutalom_valaszt'),
    
    # Autentikáció
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    
    # Rangsor és achievementek
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('achievements/', views.my_achievements, name='achievements'),
]