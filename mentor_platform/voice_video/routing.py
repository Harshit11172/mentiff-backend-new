from django.urls import re_path
from . import consumers
from django.urls import path

websocket_urlpatterns = [
    # re_path(r'ws/call/(?P<call_id>\w+)/$', consumers.CallConsumer.as_asgi()),
    path('ws/call/<str:call_id>/', consumers.CallConsumer.as_asgi()),
]
