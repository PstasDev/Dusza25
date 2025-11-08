"""
WebSocket routing for Damareen app
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/battle/(?P<jatek_id>\d+)/(?P<kazamata_id>\d+)/$', consumers.BattleConsumer.as_asgi()),
]
