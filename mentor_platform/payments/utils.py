# payments/utils.py

from decimal import Decimal
from django.db import transaction
from .models import MentorEarning, SessionPayment
from django.conf import settings

# payments/utils.py

from decimal import Decimal
from django.db import transaction
from .models import SessionPayment, MentorEarning, PlatformEarnings



def handle_successful_session(session_id, mentor, mentee, total_amount):
    platform_fee = (Decimal(total_amount) * Decimal(settings.PLATFORM_FEE_PERCENT)) / Decimal('100.0')
    service_charge = (Decimal(total_amount) * Decimal(settings.SERVICE_CHARGE_PERCENT)) / Decimal('100.0')
    mentor_earning = Decimal(total_amount) - platform_fee - service_charge

    with transaction.atomic():
        # Avoid duplicate payment entries
        if SessionPayment.objects.filter(session_id=session_id).exists():
            return  # Payment already handled

        # Create session payment record
        SessionPayment.objects.create(
            session_id=session_id,
            mentor=mentor,
            mentee=mentee,
            total_amount=total_amount,
            platform_fee=platform_fee,
            service_charge=service_charge,
            mentor_earning=mentor_earning,
            is_disbursed=True,
        )

        # Update mentor's wallet or earnings
        mentor_wallet, _ = MentorEarning.objects.get_or_create(user=mentor)
        mentor_wallet.balance = Decimal(mentor_wallet.balance) + mentor_earning
        mentor_wallet.total_earnings = Decimal(mentor_wallet.total_earnings) + mentor_earning
        mentor_wallet.save()

        # Update platform TOTAL BALANCE
        platform, _ = PlatformEarnings.objects.get_or_create(pk=1)
        platform.total_balance -= mentor_earning
        platform.save() 




# payments/utils.py

from django.utils import timezone
from .models import WithdrawalRequest

def request_withdrawal(user, amount):
    MentorEarning = user.MentorEarning
    if MentorEarning.balance < amount:
        raise ValueError("Insufficient MentorEarning balance.")

    with transaction.atomic():
        MentorEarning.balance -= amount
        MentorEarning.save()

        request = WithdrawalRequest.objects.create(
            user=user,
            amount=amount,
            requested_at=timezone.now(),
            is_processed=False
        )

        return request
