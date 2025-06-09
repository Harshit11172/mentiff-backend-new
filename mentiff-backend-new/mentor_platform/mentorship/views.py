from rest_framework import generics, permissions, status
from rest_framework.response import Response
from decimal import Decimal
from django.conf import settings
from payments.models import PlatformEarnings
from .models import Session
from .serializers import SessionSerializer


class SessionCreateView(generics.CreateAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Save session with mentee as current user
        session = serializer.save(mentee=self.request.user)

        # Calculate fees
        total_amount = session.amount_paid
        platform_fee = (total_amount * settings.PLATFORM_FEE_PERCENT) / Decimal('100.0')
        service_charge = (total_amount * settings.SERVICE_CHARGE_PERCENT) / Decimal('100.0')

        # Update platform earnings (singleton, pk=1)
        platform, _ = PlatformEarnings.objects.get_or_create(pk=1)
        platform.total_earnings = Decimal(platform.total_earnings) + (platform_fee + service_charge)
        platform.total_balance = Decimal(platform.total_balance) + total_amount
        platform.withdrawable_balance = Decimal(platform.withdrawable_balance) + (platform_fee + service_charge)
        platform.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
