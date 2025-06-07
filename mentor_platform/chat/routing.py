# chat/routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/group/<str:group_name>/', consumers.GroupChatConsumer.as_asgi()),
    path('ws/chat/private/<str:user_id>/', consumers.PrivateChatConsumer.as_asgi()),
]
