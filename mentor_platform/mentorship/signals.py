# sessions/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Session
from payments.utils import handle_successful_session

@receiver(post_save, sender=Session)
def trigger_payment_on_completion(sender, instance, created, **kwargs):
    if not created and instance.status == 'completed':
        # Prevent double payouts
        from payments.models import SessionPayment
        if not SessionPayment.objects.filter(session_id=instance.session_id).exists():
            handle_successful_session(
                session_id=instance.session_id,
                mentor=instance.mentor,
                mentee=instance.mentee,
                total_amount=instance.amount_paid
            )
