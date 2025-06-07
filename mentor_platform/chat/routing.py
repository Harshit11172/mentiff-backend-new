# chat/routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('api_backend/ws/chat/group/<str:group_name>/', consumers.GroupChatConsumer.as_asgi()),
    path('api_backend/ws/chat/private/<str:user_id>/', consumers.PrivateChatConsumer.as_asgi()),
]
