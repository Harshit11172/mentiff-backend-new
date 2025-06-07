from django.db import models
from django.utils import timezone
from users.models import Mentee, Mentor
from django.conf import settings


class Transaction(models.Model):
    mentee = models.ForeignKey(Mentee, on_delete=models.CASCADE, related_name='transactions')
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='transactions')
    session_fee = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(default=timezone.now)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    session_date = models.DateTimeField()  # Date and time of the mentoring session
    notes = models.TextField(blank=True)  # Optional field for any additional notes

    def __str__(self):
        return f"Transaction: {self.mentee.user.username} paid {self.session_fee} to {self.mentor.user.username} on {self.transaction_date}"

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ['-transaction_date']  # Order by most recent transaction first



from django.db import models
from users.models import CustomUser  # Import your custom user model

class AccountDetails(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='account_details')
    bank_name = models.CharField(max_length=255)
    account_holder_name = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=30)
    ifsc_code = models.CharField(max_length=15)
    upi_id = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Account Details for {self.user.username}"