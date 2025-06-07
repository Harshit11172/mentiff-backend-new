from django.contrib import admin
from .models import Booking

class BookingAdmin(admin.ModelAdmin):
    list_display = ('mentee', 'mentor', 'scheduled_time', 'duration', 'status', 'created_at', 'booking_amount')  # Add any other fields you want to display
    list_filter = ('status', 'scheduled_time')  # Optional: Add filters for easier navigation
    search_fields = ('mentee__user__username', 'mentor__user__username')  # Optional: Add search functionality

admin.site.register(Booking, BookingAdmin)
