from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import JSONField  # If using PostgreSQL
from django.core.exceptions import ValidationError
import re
from datetime import time


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('mentor', 'Mentor'),
        ('mentee', 'Mentee'),
        ('admin', 'Admin'),
    )
    VERIFICATION_STATUS_CHOICES = (
        ('notInitiated', 'NotInitiated'),
        ('pending', 'Pending'),        # Verification is pending
        ('verified', 'Verified'),      # Email has been verified
        ('rejected', 'Rejected'),      # Verification failed or rejected
    )
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default_dp.jpg', null=True, blank=True)
    email = models.EmailField(unique=True)  # Ensure email is unique
    user_type = models.CharField(max_length=6, choices=USER_TYPE_CHOICES)
    # , default='mentee'
    verification_token = models.CharField(max_length=32, null=True, blank=True)  # Token for verification
    is_verified = models.BooleanField(default=False)  # Status to track email verification

        # New verification status field
    verification_status = models.CharField(
        max_length=15,
        choices=VERIFICATION_STATUS_CHOICES,
        default='notInitiated',  # Default to 'pending' until verification is done
    )

    # Set custom related names to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='users_user_set',  # Change this to avoid conflicts
        blank=True,
    )   
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='users_user_permissions',  # Change this to avoid conflicts
        blank=True,
    )

    def __str__(self):
        return self.username


class Mentor(models.Model):
    
    
    def default_availability():
        return {
      "Monday": ["8:00 PM - 8:20 PM", "8:20 PM - 8:40 PM", "8:40 PM - 9:00 PM", "9:00 PM - 9:20 PM", "9:20 PM - 9:40 PM", "9:40 PM - 10:00 PM"],
      "Tuesday": ["8:00 PM - 8:20 PM", "8:20 PM - 8:40 PM", "8:40 PM - 9:00 PM", "9:00 PM - 9:20 PM", "9:20 PM - 9:40 PM", "9:40 PM - 10:00 PM"],
      "Wednesday": ["8:00 PM - 8:20 PM", "8:20 PM - 8:40 PM", "8:40 PM - 9:00 PM", "9:00 PM - 9:20 PM", "9:20 PM - 9:40 PM", "9:40 PM - 10:00 PM"],
      "Thursday": ["8:00 PM - 8:20 PM", "8:20 PM - 8:40 PM", "8:40 PM - 9:00 PM", "9:00 PM - 9:20 PM", "9:20 PM - 9:40 PM", "9:40 PM - 10:00 PM"],
      "Friday": ["8:00 PM - 8:20 PM", "8:20 PM - 8:40 PM", "8:40 PM - 9:00 PM", "9:00 PM - 9:20 PM", "9:20 PM - 9:40 PM", "9:40 PM - 10:00 PM"],
      "Saturday": ["8:00 PM - 8:20 PM", "8:20 PM - 8:40 PM", "8:40 PM - 9:00 PM", "9:00 PM - 9:20 PM", "9:20 PM - 9:40 PM", "9:40 PM - 10:00 PM"],
      "Sunday": ["8:00 PM - 8:20 PM", "8:20 PM - 8:40 PM", "8:40 PM - 9:00 PM", "9:00 PM - 9:20 PM", "9:20 PM - 9:40 PM", "9:40 PM - 10:00 PM"]
    }

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='mentor_profile')
    phone_number = models.CharField(max_length=15, blank=True)  # Optional
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default_dp.jpg', null=True, blank=True)

    google_refresh_token = models.TextField(null=True, blank=True)  # Add this


    # Academic Information
    country = models.CharField(max_length=100, blank=True)
    university = models.CharField(max_length=255, blank=True)    #######
    college = models.CharField(max_length=255, blank=True)    #######

    degree = models.CharField(max_length=100, blank=True)  #######
    major = models.CharField(max_length=100, blank=True)    ########
    year_of_admission = models.IntegerField(null=True, blank=True)   ########
    college_id = models.CharField(max_length=100, blank=True)  # Optional
    
    # About Information
    about = models.TextField(blank=True)  # Add this line

    # Mentorship Information
    expertise = models.CharField(max_length=255, blank=True)  # Optional

    availability = JSONField(default=default_availability, blank=True)  # Store availability as a dict
    
    # session_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Optional   ######
    
    # session_fee = models.DecimalField(
    #     max_digits=10, 
    #     decimal_places=2, 
    #     default=200.00
    # )  # Default set to 200 INR

    # session_time = models.CharField(max_length=50, default='30 Mins') 
    # currency = models.CharField(max_length=3, default='INR')  # Store currency code (e.g., 'INR', 'USD')
    
    rating = models.FloatField(default=0.0)

    #add +1 everytime a session is booked
    ###### THIS LOGIC HAS BEEN NOT IMPLEMENTED YET !!!!!!!!!!!!!!!!!!!!!
    calls_booked = models.IntegerField(default=0)

    # Entrance Exam Info
    entrance_exam_given = models.CharField(max_length=100, blank=True)  # Optional
    rank = models.IntegerField(null=True, blank=True)  # Optional
    score = models.FloatField(null=True, blank=True)  # Optional


    def get_slots_for_date(self, date, slot_length_minutes=None):
        from datetime import datetime, timedelta
        slot_length = slot_length_minutes or self.default_session_duration
        slots = []

        availabilities = self.availabilities.filter(day_of_week=date.weekday())
        existing_bookings = self.bookings.filter(
            start_datetime__date=date,
            status__in=['pending', 'confirmed']
        )
        booked_ranges = [(b.start_datetime.time(), b.end_datetime.time()) for b in existing_bookings]

        for availability in availabilities:
            start = datetime.combine(date, availability.start_time)
            end = datetime.combine(date, availability.end_time)

            while start + timedelta(minutes=slot_length) <= end:
                slot_start = start
                slot_end = start + timedelta(minutes=slot_length)

                if not any(booked_start <= slot_start.time() < booked_end for booked_start, booked_end in booked_ranges):
                    slots.append({"start": slot_start, "end": slot_end})

                start = slot_end
        return slots
    
    
    def save(self, *args, **kwargs):
        # Save the mentor first to get an ID (needed for availability)
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            # Create default availability for weekdays
            weekday_hours = [
                (0, time(19, 0), time(23, 30)),  # Monday 7 PM - 12 AM
                (1, time(19, 0), time(23, 30)),
                (2, time(19, 0), time(23, 30)),
                (3, time(19, 0), time(23, 30)),
                (4, time(19, 0), time(23, 30)),
                # Weekend hours
                (5, time(10, 0), time(23, 30)),  # Saturday 10 AM - 12 PM
                (6, time(10, 0), time(23, 30)),  # Sunday 10 AM - 12 PM
            ]

            for day, start, end in weekday_hours:
                MentorAvailability.objects.create(
                    mentor=self,
                    day_of_week=day,
                    start_time=start,
                    end_time=end
                )


    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.user.username}"

    class Meta:
        verbose_name = "Mentor"
        verbose_name_plural = "Mentors"


class Mentee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='mentee_profile')
    phone_number = models.CharField(max_length=15, blank=True)  # Optional
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default_dp.jpg', null=True, blank=True)

    google_refresh_token = models.TextField(null=True, blank=True)  # Add this


    # Academic Information
    university = models.CharField(max_length=255, blank=True)  # Optional
    college = models.CharField(max_length=255, blank=True)  # Optional

    degree = models.CharField(max_length=100, blank=True)  # Optional
    major = models.CharField(max_length=100, blank=True)  # Optional
    year_of_study = models.IntegerField(null=True, blank=True)  # Optional
    college_id = models.CharField(max_length=100, blank=True)  # Optional

    # Mentorship Preferences
    desired_expertise = models.CharField(max_length=255, blank=True)  # Optional
    preferred_session_times = models.TextField(blank=True)  # Optional
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Optional

    # Additional Information
    goals = models.TextField(blank=True)  # Optional
    feedback = models.TextField(blank=True)  # Optional

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.university}"

    class Meta:
        verbose_name = "Mentee"
        verbose_name_plural = "Mentees"




from django.db.models.signals import post_save
from django.dispatch import receiver

class SessionOption(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name="session_options")
    duration_minutes = models.PositiveIntegerField()  # e.g., 20, 30, 60
    fee = models.DecimalField(max_digits=10, decimal_places=2)  # price for this duration
    currency = models.CharField(max_length=3, default="INR")

    class Meta:
        unique_together = ("mentor", "duration_minutes")

    def clean(self):
        if self.fee < 200:
            raise ValidationError("Session fee must be at least 200 INR.")

    def __str__(self):
        return f"{self.mentor.user.username} - {self.duration_minutes} mins @ {self.fee} {self.currency}"



# --- Signal to create default session options ---
@receiver(post_save, sender=Mentor)
def create_default_session_options(sender, instance, created, **kwargs):
    if created:
        defaults = [
            {"duration_minutes": 15, "fee": 200, "currency": "INR"},
            {"duration_minutes": 30, "fee": 300, "currency": "INR"},
        ]
        for option in defaults:
            SessionOption.objects.get_or_create(
                mentor=instance,
                duration_minutes=option["duration_minutes"],
                defaults={"fee": option["fee"], "currency": option["currency"]},
            )




class MentorAvailability(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name="availabilities")
    # day_of_week = models.IntegerField(choices=[
    #     (0, "Monday"), (1, "Tuesday"), (2, "Wednesday"),
    #     (3, "Thursday"), (4, "Friday"), (5, "Saturday"), (6, "Sunday")
    # ])
    day_of_week = models.IntegerField(choices=[
    (0, "Sunday"), (1, "Monday"), (2, "Tuesday"),
    (3, "Wednesday"), (4, "Thursday"),
    (5, "Friday"), (6, "Saturday")
])
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        if self.start_time and self.end_time:
            return f"{self.mentor.user.username} - {self.get_day_of_week_display()} {self.start_time} to {self.end_time}"
        else:
            return f"{self.mentor.user.username} - {self.get_day_of_week_display()} No slot"





class Feedback(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    mentee = models.ForeignKey(Mentee, on_delete=models.CASCADE, related_name='feedbacks')
    # session_date = models.DateTimeField(null=True, blank=True)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_visible = models.BooleanField(default=True)
    
 
    # class Meta:
    #     unique_together = ('mentor', 'mentee') #'session_date'

    def __str__(self):
        return f"Feedback from {self.mentee.user.username} for {self.mentor.user.username}"




class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Use CustomUser instead of User
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP {self.code} for {self.user.username}"





from django.db import models
from django.utils import timezone

class Post(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(CustomUser, related_name="liked_posts", blank=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"Post by {self.mentor.user.username} at {self.created_at}"





class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.author.username} on post {self.post.id}"





# from django.db import models
# from django.utils import timezone
# from django.contrib.contenttypes.models import ContentType
# from django.contrib.contenttypes.fields import GenericForeignKey

# class Comment(models.Model):
#     author = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
#     text = models.TextField()
#     created_at = models.DateTimeField(default=timezone.now)

#     # Generic foreign key (can link to Post, Feedback, etc.)
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey("content_type", "object_id")

#     def __str__(self):
#         return f"Comment by {self.author.username} on {self.content_object}"
