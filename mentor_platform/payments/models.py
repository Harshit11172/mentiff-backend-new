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
    
    
# payments/models.py

class PlatformEarnings(models.Model):
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    total_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # <-- new field
    withdrawable_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # <-- new field

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Platform Earnings: ₹{self.total_earnings}"


# payments/models.py

class MentorEarning(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='MentorEarning')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_requested = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s MentorEarning"


# payments/models.py

from django.db import models
from users.models import CustomUser
from decimal import Decimal

class SessionPayment(models.Model):
    mentor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_payments')
    mentee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='made_payments')
    session_id = models.CharField(max_length=100, unique=True)
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    mentor_earning = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    payment_date = models.DateTimeField(auto_now_add=True)
    is_disbursed = models.BooleanField(default=False)

    
    def calculate_fees(self):
        platform_fee = (self.total_amount * settings.PLATFORM_FEE_PERCENT) / Decimal('100.0')
        service_charge = (self.total_amount * settings.SERVICE_CHARGE_PERCENT) / Decimal('100.0')
        mentor_earning = self.total_amount - platform_fee - service_charge
        return platform_fee, service_charge, mentor_earning

    def save(self, *args, **kwargs):
        if not self.pk:  # On creation
            platform_fee, service_charge, mentor_earning = self.calculate_fees()
            self.platform_fee = platform_fee
            self.service_charge = service_charge
            self.mentor_earning = mentor_earning
        super().save(*args, **kwargs)




class WithdrawalRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='withdrawal_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    requested_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)

    def clean(self):
        if self.amount > self.user.MentorEarning.balance:
            raise ValidationError("Withdrawal amount exceeds MentorEarning balance")

    def __str__(self):
        return f"{self.user.username} requested {self.amount}"
