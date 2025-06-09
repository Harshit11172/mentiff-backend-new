# mentorship/models.py


from django.db import models
from users.models import CustomUser
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from datetime import time
from payments.utils import handle_successful_session


class Session(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('missed', 'Missed'),
    )

    mentor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mentor_sessions')
    mentee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mentee_sessions')

    session_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    date = models.DateField(default=timezone.now)  # today's date
    start_time = models.TimeField(default=time(9, 0))  # 9:00 AM
    duration_minutes = models.PositiveIntegerField(default=20)  # e.g., 60

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mentor.username} with {self.mentee.username} on {self.date} at {self.start_time}"

     # ✅ Add this method here
    def get_end_time(self):
        return (datetime.combine(self.date, self.start_time) + timedelta(minutes=self.duration_minutes)).time()



    # ADD PAYMENT TRIGGER HERE TO MENTOR 
    # ADD PAYMENT TRIGGER HERE TO MENTOR 
    # ADD PAYMENT TRIGGER HERE TO MENTOR 
    # ADD PAYMENT TRIGGER HERE TO MENTOR 
    # ADD PAYMENT TRIGGER HERE TO MENTOR 
    # ADD PAYMENT TRIGGER HERE TO MENTOR BELOW
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not is_new:
            old = Session.objects.get(pk=self.pk)
            if old.status != 'completed' and self.status == 'completed':
                # Trigger payment logic
                handle_successful_session(
                    session_id=self.session_id,
                    mentor=self.mentor,
                    mentee=self.mentee,
                    total_amount=self.amount_paid
                )
        super().save(*args, **kwargs)