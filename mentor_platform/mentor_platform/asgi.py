import os

# Set the DJANGO_SETTINGS_MODULE before any Django imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentor_platform.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns

from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from voice_video.routing import websocket_urlpatterns as voice_video_websocket_urlpatterns

websocket_urlpatterns = chat_websocket_urlpatterns + voice_video_websocket_urlpatterns
print(websocket_urlpatterns)

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
