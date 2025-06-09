
# chat/management/commands/import_groups.py

import json
from django.core.management.base import BaseCommand
from chat.models import Group, Membership
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Import groups from a JSON file'

    def handle(self, *args, **kwargs):
        with open('static_files/university.json', 'r') as file:
            data = json.load(file)

        for group_data in data:
            # Create admin users
            admin_usernames = group_data['admin']
            admin_users = User.objects.filter(username__in=admin_usernames)

            if admin_users.count() == 0:
                self.stdout.write(self.style.WARNING(f"Admin users not found: {admin_usernames}"))
                continue

            # Create the group
            group = Group.objects.create(
                group_name=group_data['group_name'],
                college=group_data['college'],
                country=group_data['country'],
                url=group_data['url'],
                logo=group_data.get('logo')
            )

            # Add admins to the group
            group.admins.set(admin_users)  # Set multiple admins

            # Create memberships
            for member in group_data['members']:
                user = User.objects.filter(username=member['username']).first()
                if user:
                    Membership.objects.create(
                        user=user,
                        group=group,
                        user_type=member['user_type']
                    )
                else:
                    self.stdout.write(self.style.WARNING(f"Member user not found: {member['username']}"))

        self.stdout.write(self.style.SUCCESS('Groups imported successfully!'))
