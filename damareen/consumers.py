"""
WebSocket consumers for real-time battle functionality
"""
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

from .models import (
    Jatek, Harc, Utközet, Kazamata, Pakli, PakliKartya, Jatekoskartya,
    ELEMENT_FIRE, ELEMENT_EARTH, ELEMENT_WATER, ELEMENT_AIR
)
from .game_logic import utközet_ertekeles


class BattleConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time battle animations and interactions
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.jatek_id = self.scope['url_route']['kwargs']['jatek_id']
        self.kazamata_id = self.scope['url_route']['kwargs']['kazamata_id']
        
        # Create a unique room name for this battle
        self.room_name = f'battle_{self.jatek_id}_{self.kazamata_id}'
        self.room_group_name = f'battle_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial connection message
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': '✅ Kapcsolat létrejött! Kattints a HARC INDÍTÁSA gombra!'
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'start_battle':
            await self.start_battle()
        elif action == 'auto_save':
            await self.auto_save_game()
    
    async def start_battle(self):
        """Start the battle and execute it step by step with animations"""
        try:
            # Verify game and kazamata
            battle_data = await self.verify_and_create_battle()
            
            if 'error' in battle_data:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': battle_data['error']
                }))
                return
            
            harc = battle_data['harc']
            pakli_kartyak = battle_data['pakli_kartyak']
            kazamata_kartyak = battle_data['kazamata_kartyak']
            
            # Send battle start message
            await self.send(text_data=json.dumps({
                'type': 'battle_start',
                'message': f'🏰 Harc kezdődik: {battle_data["kazamata_nev"]}!',
                'total_rounds': len(pakli_kartyak)
            }))
            
            await asyncio.sleep(1.5)
            
            # Execute each round
            utközetek = []
            jatekos_gyozelmek = 0
            
            for i, (pakli_kartya, kazamata_kartya) in enumerate(zip(pakli_kartyak, kazamata_kartyak)):
                round_num = i + 1
                
                # Send round start
                await self.send(text_data=json.dumps({
                    'type': 'round_start',
                    'round': round_num,
                    'message': f'⚔️ {round_num}. ütközet kezdődik...'
                }))
                
                await asyncio.sleep(1)
                
                # Send player card reveal
                await self.send(text_data=json.dumps({
                    'type': 'card_reveal',
                    'side': 'player',
                    'round': round_num,
                    'card': {
                        'name': pakli_kartya['name'],
                        'damage': pakli_kartya['damage'],
                        'hp': pakli_kartya['hp'],
                        'element': pakli_kartya['element'],
                        'element_display': pakli_kartya['element_display']
                    }
                }))
                
                await asyncio.sleep(1.2)
                
                # Send enemy card reveal
                await self.send(text_data=json.dumps({
                    'type': 'card_reveal',
                    'side': 'enemy',
                    'round': round_num,
                    'card': {
                        'name': kazamata_kartya['name'],
                        'damage': kazamata_kartya['damage'],
                        'hp': kazamata_kartya['hp'],
                        'element': kazamata_kartya['element'],
                        'element_display': kazamata_kartya['element_display'],
                        'is_leader': kazamata_kartya['is_leader']
                    }
                }))
                
                await asyncio.sleep(1.2)
                
                # Calculate battle result
                jatekos_nyert, ok = utközet_ertekeles(
                    pakli_kartya['damage'], pakli_kartya['hp'], pakli_kartya['element'],
                    kazamata_kartya['damage'], kazamata_kartya['hp'], kazamata_kartya['element']
                )
                
                if jatekos_nyert:
                    jatekos_gyozelmek += 1
                
                # Save battle round to database
                utközet_data = await self.save_utközet(
                    harc['id'], round_num, pakli_kartya, kazamata_kartya,
                    jatekos_nyert, ok
                )
                utközetek.append(utközet_data)
                
                # Send battle animation
                await self.send(text_data=json.dumps({
                    'type': 'battle_animation',
                    'round': round_num,
                    'winner': 'player' if jatekos_nyert else 'enemy',
                    'player_element': pakli_kartya['element'],
                    'enemy_element': kazamata_kartya['element']
                }))
                
                await asyncio.sleep(1.5)
                
                # Send round result
                await self.send(text_data=json.dumps({
                    'type': 'round_result',
                    'round': round_num,
                    'winner': 'player' if jatekos_nyert else 'enemy',
                    'reason': ok,
                    'player_wins': jatekos_gyozelmek
                }))
                
                await asyncio.sleep(1.8)
            
            # Determine overall winner
            szukseges_gyozelmek = (len(kazamata_kartyak) + 1) // 2
            jatekos_gyozott = jatekos_gyozelmek >= szukseges_gyozelmek
            
            # Update battle in database
            await self.complete_battle(harc['id'], jatekos_gyozott)
            
            # Auto-save after battle
            await self.auto_save_game()
            
            # Send final result
            await self.send(text_data=json.dumps({
                'type': 'battle_end',
                'winner': 'player' if jatekos_gyozott else 'enemy',
                'player_wins': jatekos_gyozelmek,
                'total_rounds': len(pakli_kartyak),
                'message': '🎉 GYŐZELEM! 🎉' if jatekos_gyozott else '😞 VERESÉG 😞',
                'harc_id': harc['id'],
                'reward': battle_data['reward'] if jatekos_gyozott else None
            }))
            
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'❌ Hiba történt: {str(e)}'
            }))
    
    @database_sync_to_async
    def verify_and_create_battle(self):
        """Verify game state and create battle record"""
        try:
            jatek = Jatek.objects.get(id=self.jatek_id, jatekos=self.user)
            kazamata = Kazamata.objects.get(id=self.kazamata_id)
            
            # Check if pakli exists
            try:
                pakli = jatek.pakli
            except Pakli.DoesNotExist:
                return {'error': '❌ Először állíts össze egy paklit!'}
            
            # Check card count match
            pakli_meret = pakli.get_kartyak_szama()
            kazamata_meret = kazamata.get_kartyak_szama()
            
            if pakli_meret != kazamata_meret:
                return {'error': f'❌ A pakli ({pakli_meret}) és kazamata ({kazamata_meret}) kártyáinak száma nem egyezik!'}
            
            # Create battle
            harc = Harc.objects.create(
                jatek=jatek,
                kazamata=kazamata
            )
            
            # Get cards
            pakli_kartyak = []
            for pk in pakli.kartyak.all().order_by('sorrend'):
                pakli_kartyak.append({
                    'id': pk.kartya.id,
                    'name': pk.kartya.eredeti_kartya.nev,
                    'damage': pk.kartya.aktualis_sebzes,
                    'hp': pk.kartya.aktualis_eletero,
                    'element': pk.kartya.tipus,
                    'element_display': pk.kartya.get_tipus_display()
                })
            
            kazamata_kartyak = []
            for kk in kazamata.kartyak.all().order_by('sorrend'):
                kazamata_kartyak.append({
                    'id': kk.id,
                    'name': kk.kartya.nev,
                    'damage': kk.get_sebzes(),
                    'hp': kk.get_eletero(),
                    'element': kk.get_tipus(),
                    'element_display': dict([(ELEMENT_FIRE, 'Tűz'), (ELEMENT_EARTH, 'Föld'), 
                                           (ELEMENT_WATER, 'Víz'), (ELEMENT_AIR, 'Levegő')]).get(kk.get_tipus(), ''),
                    'is_leader': kk.is_vezer
                })
            
            return {
                'harc': {'id': harc.id},
                'pakli_kartyak': pakli_kartyak,
                'kazamata_kartyak': kazamata_kartyak,
                'kazamata_nev': kazamata.nev,
                'reward': kazamata.get_nyeremeny_leiras()
            }
            
        except Jatek.DoesNotExist:
            return {'error': '❌ Játék nem található!'}
        except Kazamata.DoesNotExist:
            return {'error': '❌ Kazamata nem található!'}
    
    @database_sync_to_async
    def save_utközet(self, harc_id, sorrend, pakli_kartya, kazamata_kartya, jatekos_nyert, ok):
        """Save battle round to database"""
        harc = Harc.objects.get(id=harc_id)
        jatekos_k = Jatekoskartya.objects.get(id=pakli_kartya['id'])
        
        # Get kazamata kartya reference
        from .models import KazamataKartya
        kazamata_kartya_ref = KazamataKartya.objects.get(id=kazamata_kartya['id'])
        
        utközet = Utközet.objects.create(
            harc=harc,
            sorrend=sorrend,
            jatekos_kartya=jatekos_k,
            jatekos_sebzes=pakli_kartya['damage'],
            jatekos_eletero=pakli_kartya['hp'],
            jatekos_tipus=pakli_kartya['element'],
            kazamata_kartya_ref=kazamata_kartya_ref,
            kazamata_sebzes=kazamata_kartya['damage'],
            kazamata_eletero=kazamata_kartya['hp'],
            kazamata_tipus=kazamata_kartya['element'],
            jatekos_nyert=jatekos_nyert,
            gyoztes_ok=ok
        )
        
        return {'id': utközet.id}
    
    @database_sync_to_async
    def complete_battle(self, harc_id, jatekos_gyozott):
        """Mark battle as complete and update leaderboard"""
        from .game_logic import frissit_rangsort
        
        harc = Harc.objects.get(id=harc_id)
        harc.befejezve = True
        harc.jatekos_gyozott = jatekos_gyozott
        harc.save()
        
        # Rangsor és achievementek frissítése
        if not harc.rangsor_frissitve:
            frissit_rangsort(self.user, jatekos_gyozott)
            harc.rangsor_frissitve = True
            harc.save(update_fields=['rangsor_frissitve'])
    
    @database_sync_to_async
    def auto_save_game(self):
        """Auto-save game state"""
        try:
            jatek = Jatek.objects.get(id=self.jatek_id, jatekos=self.user)
            # Save method automatically updates utolso_aktivitas
            jatek.save()
            return True
        except:
            return False
