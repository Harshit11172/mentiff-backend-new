from django.db import models
from users.models import Mentor, Mentee 
import uuid
from django.utils import timezone
# from agora import RtmTokenBuilder, RtcTokenBuilder 
from datetime import datetime, time, timedelta
from django.conf import settings
from django.urls import reverse
import time
import hmac
import hashlib
import base64
import uuid
from django.db import models
from django.core.mail import send_mail
# from .utils.google_calendar import authenticate_google_calendar
from googleapiclient.discovery import build
from twilio.rest import Client 



# NOT NEEDED NOW AS CREATED MODEL UNDER MENTORSHIP APP

# NOT NEEDED NOW AS CREATED MODEL UNDER MENTORSHIP APP

# NOT NEEDED NOW AS CREATED MODEL UNDER MENTORSHIP APP

# NOT NEEDED NOW AS CREATED MODEL UNDER MENTORSHIP APP

# NOT NEEDED NOW AS CREATED MODEL UNDER MENTORSHIP APP

# NOT NEEDED NOW AS CREATED MODEL UNDER MENTORSHIP APP

# NOT NEEDED NOW AS CREATED MODEL UNDER MENTORSHIP APP


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
        ('issue raised', 'Issue Raised'),
        ('issue resolved', 'Issue Resolved'), 
    ]
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    mentee = models.ForeignKey(Mentee, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    channel_name = models.CharField(max_length=255, blank=True)  # Will store generated channel name
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the field to now when the object is created
    booking_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Booking amount in currency")  # New field for booking amount
    call_link = models.URLField(max_length=200, blank=True, null=True, help_text="Link for the call")

    def __str__(self):
        return f"Booking with {self.mentor} and {self.mentee} at {self.scheduled_time}"
    

