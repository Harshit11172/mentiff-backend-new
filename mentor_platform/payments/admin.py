from django.contrib import admin
from .models import (
    PlatformEarnings,
    MentorEarning,
    SessionPayment,
    WithdrawalRequest,
    AccountDetails
)

@admin.register(PlatformEarnings)
class PlatformEarningsAdmin(admin.ModelAdmin):
    list_display = ('total_earnings', 'total_balance', 'withdrawable_balance', 'updated_at')
    readonly_fields = ('updated_at',)


@admin.register(MentorEarning)
class MentorEarningAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'total_earnings','amount_requested', 'updated_at')
    search_fields = ('user__username',)


@admin.register(SessionPayment)
class SessionPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'session_id', 'mentor', 'mentee', 'total_amount',
        'platform_fee', 'service_charge', 'mentor_earning',
        'payment_date', 'is_disbursed'
    )
    search_fields = ('session_id', 'mentor__username', 'mentee__username')
    list_filter = ('is_disbursed', 'payment_date')


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'amount', 'requested_at', 'is_processed', 'processed_at'
    )
    list_filter = ('is_processed',)
    search_fields = ('user__username',)
    readonly_fields = ('requested_at',)


@admin.register(AccountDetails)
class AccountDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_holder_name', 'bank_name', 'bank_account_number', 'ifsc_code', 'upi_id')
    search_fields = ('user__username', 'account_holder_name', 'bank_account_number')
