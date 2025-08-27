from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from chat.models import GroupMessage, Group
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = "Seed group with test users and messages for load testing"

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10000, help='Number of fake users')
        parser.add_argument('--messages', type=int, default=10000, help='Number of fake messages')

    def handle(self, *args, **options):
        num_users = options['users']
        num_messages = options['messages']

        group = Group.objects.last()
        if not group:
            self.stdout.write(self.style.ERROR("No Group found, create one first."))
            return

        self.stdout.write(f"Creating {num_users} users if not exist...")

        # Create users
        users = []
        for i in range(num_users):
            username = f"testuser{i}"
            email = f"testuser{i}@example.com"
            if not User.objects.filter(username=username).exists():
                users.append(User(username=username, email=email))
        User.objects.bulk_create(users, ignore_conflicts=True)

        all_users = list(User.objects.filter(username__startswith="testuser")[:num_users])

        self.stdout.write(self.style.SUCCESS(f"Users ready: {len(all_users)}"))

        self.stdout.write(f"Creating {num_messages} messages...")
        now = timezone.now()

        sample_texts = [
            "Hey there!", "Testing load 🚀", "Chat flood message.",
            "Random thought...", "Good morning!", "Good night 🌙",
            "Yesterday’s update", "What’s up?", "Performance test!",
            "Django rocks 💡"
        ]

        messages = []
        for i in range(num_messages):
            sender = random.choice(all_users)
            offset_days = random.randint(0, 30)     # last 30 days
            offset_minutes = random.randint(0, 1440)
            timestamp = now - timedelta(days=offset_days, minutes=offset_minutes)

            messages.append(
                GroupMessage(
                    group=group,
                    sender=sender,
                    message=random.choice(sample_texts),
                    timestamp=timestamp,
                    profile_picture=f"https://i.pravatar.cc/150?img={random.randint(1, 70)}"
                )
            )

            if len(messages) >= 5000:  # bulk insert in batches
                GroupMessage.objects.bulk_create(messages)
                messages = []

        if messages:
            GroupMessage.objects.bulk_create(messages)

        self.stdout.write(
        self.style.SUCCESS(
            f"Inserted {num_messages} messages into group: {group.group_name} (college: {group.college})"
        )
)

