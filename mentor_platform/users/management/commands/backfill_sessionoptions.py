from django.core.management.base import BaseCommand
from users.models import Mentor, SessionOption

class Command(BaseCommand):
    help = "Backfill default SessionOptions (200 INR/15 mins, 300 INR/30 mins) for all existing mentors."

    def handle(self, *args, **kwargs):
        defaults = [
            {"duration_minutes": 15, "fee": 200, "currency": "INR"},
            {"duration_minutes": 30, "fee": 300, "currency": "INR"},
        ]

        created_count = 0
        for mentor in Mentor.objects.all():
            for option in defaults:
                obj, created = SessionOption.objects.get_or_create(
                    mentor=mentor,
                    duration_minutes=option["duration_minutes"],
                    defaults={"fee": option["fee"], "currency": option["currency"]},
                )
                if created:
                    created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ Backfill complete. Created {created_count} new SessionOptions.")
        )
