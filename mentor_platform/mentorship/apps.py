from django.apps import AppConfig


class MentorshipConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mentorship'


# sessions/apps.py

def ready(self):
    import mentorship.signals
