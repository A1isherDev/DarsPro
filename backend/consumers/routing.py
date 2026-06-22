"""DarsPro — WebSocket marshrutlari."""
from django.urls import re_path

from .session_consumer import SessionConsumer

websocket_urlpatterns = [
    re_path(
        r"^ws/session/(?P<join_code>DRS-[A-Z0-9]{4})/$",
        SessionConsumer.as_asgi(),
    ),
]
