import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')

django_application = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from messenger.routing import websocket_urlpatterns as messenger_websocket_urlpatterns
from django_app.routing import websocket_urlpatterns as notification_websocket_urlpatterns


application = ProtocolTypeRouter({
    "http": django_application,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            notification_websocket_urlpatterns + messenger_websocket_urlpatterns
        )
    ),
})
