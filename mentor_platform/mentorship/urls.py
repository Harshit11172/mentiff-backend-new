# sessions/urls.py

from django.urls import path
from .views import SessionCreateView

urlpatterns = [
    path('create-session/', SessionCreateView.as_view(), name='session-create'),
]
