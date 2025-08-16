from datetime import datetime, timedelta
from .models import MentorAvailability, Booking


def generate_slots_for_day(mentor, date, slot_length_minutes):
    slots = []
    weekday = date.weekday()

    # Get mentor's availability for that weekday
    availabilities = MentorAvailability.objects.filter(mentor=mentor, day_of_week=weekday)

    # Get existing bookings for that date
    existing_bookings = Booking.objects.filter(
        mentor=mentor,
        start_datetime__date=date,
        status__in=['pending', 'confirmed']
    )

    # Convert bookings to (start, end) tuples in time format
    booked_ranges = [(b.start_datetime.time(), b.end_datetime.time()) for b in existing_bookings]

    for availability in availabilities:
        start = datetime.combine(date, availability.start_time)
        end = datetime.combine(date, availability.end_time)

        while start + timedelta(minutes=slot_length_minutes) <= end:
            slot_start = start
            slot_end = start + timedelta(minutes=slot_length_minutes)

            # Check if slot overlaps with any booked slot
            if not any(
                booked_start <= slot_start.time() < booked_end
                for booked_start, booked_end in booked_ranges
            ):
                slots.append({
                    "start": slot_start.isoformat(),
                    "end": slot_end.isoformat()
                })

            start = slot_end

    return slots
