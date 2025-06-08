# sessions/admin.py

from django.contrib import admin
from .models import Session
from payments.utils import handle_successful_session

@admin.action(description='Mark session as completed and pay mentor')
def complete_and_pay(modeladmin, request, queryset):
    for session in queryset:
        if session.status != 'completed':
            session.status = 'completed'
            session.save()

        from payments.models import SessionPayment
        if not SessionPayment.objects.filter(session_id=session.session_id).exists():
            handle_successful_session(
                session_id=session.session_id,
                mentor=session.mentor,
                mentee=session.mentee,
                total_amount=session.amount_paid
            )

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'mentor', 'mentee', 'date', 'start_time', 'get_end_time')
    actions = [complete_and_pay]
    
    def get_end_time(self, obj):
        return obj.get_end_time()
    get_end_time.short_description = 'End Time'



