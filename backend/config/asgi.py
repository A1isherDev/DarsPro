"""DarsPro — ASGI entry point.

HTTP so'rovlari Django'ga, WebSocket so'rovlari Channels routing'ga yo'naltiriladi.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Django app'ni WebSocket import'laridan oldin ishga tushiramiz
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402

from consumers.middleware import JWTAuthMiddleware  # noqa: E402
from consumers.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
