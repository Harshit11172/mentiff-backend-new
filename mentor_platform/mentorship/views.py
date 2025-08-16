from rest_framework import generics, permissions, status
from rest_framework.response import Response
from decimal import Decimal
from django.conf import settings
from payments.models import PlatformEarnings
from .models import Session
from .serializers import SessionSerializer
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from users.models import Mentor, MentorAvailability
from voice_video.models import Booking
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from users.models import MentorAvailability
from .serializers import MentorAvailabilitySerializer

from datetime import time






class MentorAvailabilityView(generics.GenericAPIView):
    serializer_class = MentorAvailabilitySerializer
    permission_classes = [IsAuthenticated]

    def get_mentor(self, request):
        """Get mentor instance for logged-in user."""
        try:
            return Mentor.objects.get(user=request.user)
        except Mentor.DoesNotExist:
            return None

    def get(self, request):
        mentor = self.get_mentor(request)
        if not mentor:
            return Response({"detail": "You are not a mentor."}, status=status.HTTP_403_FORBIDDEN)

        # If no availability exists, create default entries
        # if not MentorAvailability.objects.filter(mentor=mentor).exists():
        #     default_hours = [
        #         (0, time(19, 0), time(23, 30)),  # Monday 7 PM - 12 AM
        #         (1, time(19, 0), time(23, 30)),
        #         (2, time(19, 0), time(23, 30)),
        #         (3, time(19, 0), time(23, 30)),
        #         (4, time(19, 0), time(23, 30)),
        #         # Weekend hours
        #         (5, time(10, 0), time(23, 30)),  # Saturday 10 AM - 12 PM
        #         (6, time(10, 0), time(23, 30)),  # Sunday 10 AM - 12 PM
        #     ]
        #     for day, start, end in default_hours:
        #         MentorAvailability.objects.create(
        #             mentor=mentor,
        #             day_of_week=day,
        #             start_time=start,
        #             end_time=end
        #         )

        availabilities = MentorAvailability.objects.filter(mentor=mentor).order_by("day_of_week")
        serializer = self.get_serializer(availabilities, many=True)
        return Response(serializer.data)

    # def put(self, request):
    #     mentor = self.get_mentor(request)
    #     if not mentor:
    #         return Response({"detail": "You are not a mentor."}, status=status.HTTP_403_FORBIDDEN)

    #     availabilities_data = request.data.get("availabilities", [])
    #     if not availabilities_data:
    #         return Response({"detail": "No availability data provided."}, status=status.HTTP_400_BAD_REQUEST)

    #     for item in availabilities_data:
    #         try:
    #             availability = MentorAvailability.objects.get(id=item["id"], mentor=mentor)
    #             serializer = self.get_serializer(availability, data=item, partial=True)
    #             serializer.is_valid(raise_exception=True)
    #             serializer.save()
    #         except MentorAvailability.DoesNotExist:
    #             return Response({"detail": f"Availability with id {item.get('id')} not found."},
    #                             status=status.HTTP_404_NOT_FOUND)

    #     return Response({"detail": "Availabilities updated successfully."})

    def put(self, request):
        mentor = self.get_mentor(request)
        if not mentor:
            return Response({"detail": "You are not a mentor."},
                            status=status.HTTP_403_FORBIDDEN)

        availabilities_data = request.data.get("availabilities", [])
        print(availabilities_data)
        if not availabilities_data:
            return Response({"detail": "No availability data provided."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Extract IDs from the payload
        sent_ids = [item.get("id") for item in availabilities_data if item.get("id")]

        # Delete slots that belong to this mentor but are not in sent data
        MentorAvailability.objects.filter(mentor=mentor).exclude(id__in=sent_ids).delete()

        # Update existing slots and create new ones
        for item in availabilities_data:
            if "id" in item and item["id"]:
                # Update existing slot
                availability = MentorAvailability.objects.get(id=item["id"], mentor=mentor)
                serializer = self.get_serializer(availability, data=item, partial=True)
            else:
                # Create new slot
                serializer = self.get_serializer(data={**item, "mentor": mentor.id})

            serializer.is_valid(raise_exception=True)
            serializer.save(mentor=mentor)

        return Response({"detail": "Availabilities updated successfully."})



# from googleapiclient.discovery import build
# from google.oauth2 import service_account

# class AvailableSlotsView(View): 
    # """
    # Returns available slots for a mentor on a given date,
    # with user-selected slot duration (15 or 30 mins).
    # """    
    # serializer_class = SessionSerializer
    # permission_classes = [permissions.IsAuthenticated]

    # def get(self, request, mentor_id):
    #     date_str = request.GET.get("date")
    #     slot_duration = int(request.GET.get("duration", 30))  # minutes (default 30)
        
    #     if not date_str:
    #         return JsonResponse({"error": "Date parameter is required"}, status=400)
        
    #     try:
    #         selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    #     except ValueError:
    #         return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

    #     # Get mentor
    #     mentor = get_object_or_404(Mentor, id=mentor_id)

    #     # Get ALL availability blocks for this day
    #     # weekday = selected_date.weekday()  # 0 = Monday, 6 = Sunday

    #     # new (convert to Sunday=0 system)
    #     weekday = (selected_date.weekday() + 1) % 7

    #     availabilities = MentorAvailability.objects.filter(mentor=mentor, day_of_week=weekday)
    #     print(availabilities)
    #     if not availabilities.exists():
    #         return JsonResponse({"slots": []})  # No availability for this day

    #     slots = []

    #     # Loop through all availability ranges (e.g., 9–11, 12–1)
    #     for availability in availabilities:
    #         start_time = datetime.combine(selected_date, availability.start_time)
    #         end_time = datetime.combine(selected_date, availability.end_time)
    #         current_time = start_time

    #         while current_time + timedelta(minutes=slot_duration) <= end_time:
    #             slots.append(current_time.strftime("%H:%M"))
    #             current_time += timedelta(minutes=slot_duration)

    #     # Remove slots that are already booked
    #     booked_slots = Booking.objects.filter(
    #         mentor=mentor,
    #         scheduled_time__date=selected_date
    #     ).values_list("scheduled_time", flat=True)

    #     booked_times = {bt.strftime("%H:%M") for bt in booked_slots}
    #     available_slots = [slot for slot in slots if slot not in booked_times]

    #     return JsonResponse({"slots": available_slots})


from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from rest_framework import permissions

from .serializers import SessionSerializer

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


from django.utils.timezone import make_aware
from datetime import timezone

class AvailableSlotsView(View):
    """
    Returns available slots for a mentor on a given date,
    with user-selected slot duration (15 or 30 mins).
    Availability is reduced by:
    1. Existing Mentiff bookings
    2. Mentor's Google Calendar events (if connected)
    """

    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, mentor_id):
        date_str = request.GET.get("date")
        slot_duration = int(request.GET.get("duration", 30))  # minutes (default 30)

        if not date_str:
            return JsonResponse({"error": "Date parameter is required"}, status=400)

        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

        # Get mentor
        mentor = get_object_or_404(Mentor, id=mentor_id)

        # Convert weekday (Django: Monday=0 ... Sunday=6 → your system: Sunday=0 ... Saturday=6)
        weekday = (selected_date.weekday() + 1) % 7
        availabilities = MentorAvailability.objects.filter(mentor=mentor, day_of_week=weekday)

        if not availabilities.exists():
            return JsonResponse({"slots": []})

        # Generate all possible slots from availability
        slots = []
        for availability in availabilities:
            start_time = make_aware(datetime.combine(selected_date, availability.start_time))
            end_time = make_aware(datetime.combine(selected_date, availability.end_time))
            current_time = start_time

            while current_time + timedelta(minutes=slot_duration) <= end_time:
                slots.append(current_time)
                current_time += timedelta(minutes=slot_duration)

        print("Selected date:", selected_date, type(selected_date))
        print("All mentor bookings:", Booking.objects.filter(mentor=mentor).values("scheduled_time", "status"))

        # --- Remove booked slots from Mentiff DB ---
        booked_slots = Booking.objects.filter(
            mentor=mentor,
            scheduled_time__date=selected_date
        ).values_list("scheduled_time", flat=True)  

        print("DB Bookings slots are :")
        print(booked_slots)

        booked_times = {bt.replace(second=0, microsecond=0) for bt in booked_slots}
        print("DB Bookings times are :")
        print(booked_times)
        
        # keep all slots, don't filter out
        # just mark them later when formatting
        # slots = [s for s in slots if s not in booked_times]

        # --- Remove Google Calendar events if mentor connected ---
        if mentor.google_refresh_token:
            slots = self.filter_google_events(mentor, selected_date, slots, slot_duration, booked_times)


        return JsonResponse({
            "slots": [
                f"{s.strftime('%H:%M')} (Booked)" if s in booked_times else s.strftime("%H:%M")
                for s in slots
            ]
        })

    def filter_google_events(self, mentor, selected_date, slots, slot_duration, booked_times):
    
        """
        Removes slots that overlap with mentor's Google Calendar events.
        Assumes OAuth tokens are stored in mentor.google_refresh_token.
        """
        creds = Credentials(
            token=mentor.google_refresh_token,
            refresh_token=mentor.google_refresh_token,
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token",
        )

        service = build("calendar", "v3", credentials=creds)

        time_min = make_aware(datetime.combine(selected_date, datetime.min.time())).isoformat()
        time_max = make_aware(datetime.combine(selected_date, datetime.max.time())).isoformat()

        events_result = service.events().list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])
        busy_ranges = []

        for event in events:
            start = event["start"].get("dateTime")
            end = event["end"].get("dateTime")
            if start and end:
                start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
                busy_ranges.append((start_dt, end_dt))

        # Filter out overlapping slots
        available = []
        for slot in slots:
            slot_end = slot + timedelta(minutes=slot_duration)
            overlap = any(start < slot_end and slot < end for start, end in busy_ranges)

            # Keep slot if it’s not overlapping OR if it's already booked (so we can mark it later)
            if not overlap or slot in booked_times:
                available.append(slot)
        return available 





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
