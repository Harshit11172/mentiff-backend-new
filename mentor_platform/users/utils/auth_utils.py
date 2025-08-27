# utils/auth_utils.py
import random
import string
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_unique_username(email):
    base = email.split('@')[0]
    username = base
    suffix = 0
    while User.objects.filter(username=username).exists():
        suffix += 1
        # try base + random 4 chars after few collisions to keep it short
        if suffix < 4:
            username = f"{base}{suffix}"
        else:
            rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            username = f"{base}{rand}"
    return username
