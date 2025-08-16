# sessions/urls.py

from django.urls import path
from .views import SessionCreateView
from .views import MentorAvailabilityView, AvailableSlotsView


urlpatterns = [
    path('create-session/', SessionCreateView.as_view(), name='session-create'),
    path('mentors/<int:mentor_id>/available-slots/', AvailableSlotsView.as_view(), name='available_slots'),
    path('mentor/availability/', MentorAvailabilityView.as_view(), name='mentor-availability'),

]
