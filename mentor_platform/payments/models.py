from django.db import models
from django.utils import timezone
from users.models import Mentee, Mentor
from django.conf import settings

###
####
### NOT USING THISSSSSS!!!!!!!! USING TRANSACTION LOG 
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




###
####
### NOT USING THISSSSSS!!!!!!!!
# class SessionPayment(models.Model):
#     mentor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_payments')
#     mentee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='made_payments')
#     session_id = models.CharField(max_length=100, unique=True)
    
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     platform_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     service_charge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     mentor_earning = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

#     payment_date = models.DateTimeField(auto_now_add=True)
#     is_disbursed = models.BooleanField(default=False)

    
#     def calculate_fees(self):
#         platform_fee = (self.total_amount * settings.PLATFORM_FEE_PERCENT) / Decimal('100.0')
#         service_charge = (self.total_amount * settings.SERVICE_CHARGE_PERCENT) / Decimal('100.0')
#         mentor_earning = self.total_amount - platform_fee - service_charge
#         return platform_fee, service_charge, mentor_earning

#     def save(self, *args, **kwargs):
#         if not self.pk:  # On creation
#             platform_fee, service_charge, mentor_earning = self.calculate_fees()
#             self.platform_fee = platform_fee
#             self.service_charge = service_charge
#             self.mentor_earning = mentor_earning
#         super().save(*args, **kwargs)




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







from django.db import models
from django.conf import settings
from decimal import Decimal
from users.models import CustomUser




from django.db import models
from django.conf import settings
from decimal import Decimal





# Why this setup is good:

# SessionPayment = 1 record per booked session. Business-friendly: total amount, platform fee, mentor earning.

# TransactionLog = multiple records per session if retries, failures, refunds happen. Keeps audit trail.

# raw_response stores PhonePe API response → essential for debugging & reconciliation.

# Refunds are tracked both at SessionPayment (latest status) and in TransactionLog (per-event).

# 👉 Industry-level practice:

# Business object (SessionPayment): clean, one record per service delivered.

# TransactionLog: raw truth, every interaction with gateway, never deleted.

# Do you also want me to show you how the workflow will look? (initiate → callback → update SessionPayment + log TransactionLog → handle refunds)



class SessionPayment(models.Model):
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='received_payments'
    )
    mentee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='made_payments'
    )
    session_id = models.CharField(max_length=100, unique=True)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    mentor_earning = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    payment_date = models.DateTimeField(auto_now_add=True)
    is_disbursed = models.BooleanField(default=False)

    # New fields
    currency = models.CharField(max_length=10, default="INR")
    payment_method = models.CharField(max_length=50, blank=True, null=True)  # UPI, Card, Netbanking, etc.
    refund_id = models.CharField(max_length=100, blank=True, null=True)
    refund_status = models.CharField(max_length=50, blank=True, null=True)

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







class TransactionLog(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("INITIATED", "Initiated"),
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    ]

    session_payment = models.ForeignKey(
        SessionPayment,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    transaction_id = models.CharField(max_length=100, unique=True)  # From PhonePe
    order_id = models.CharField(max_length=100, blank=True, null=True)  # internal mapping
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    payment_method = models.CharField(max_length=50, blank=True, null=True)

    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="INITIATED")
    raw_response = models.JSONField(blank=True, null=True)  # store full PhonePe response

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Refund tracking
    refund_id = models.CharField(max_length=100, blank=True, null=True)
    refund_status = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"
