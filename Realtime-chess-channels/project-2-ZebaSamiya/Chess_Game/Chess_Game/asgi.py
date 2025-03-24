import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Chess_Game.settings")
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import Chess_App.routing
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            Chess_App.routing.websocket_urlpatterns
        )
    ),
})



