from agora_token_builder import RtcTokenBuilder
from django.conf import settings
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from django.utils import timezone
from .models import Mentor, Mentee, Booking
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.urls import reverse



class TokenGenerationView(generics.GenericAPIView):

    # permission_classes = [IsAuthenticated]  # Only allow authenticated users

    def get(self, request):
        channel_name = request.query_params.get('channel')
        uid = request.user.id
        
        if not channel_name:
            return Response({"error": "Channel name is required"}, status=400)

        AGORA_APP_ID = settings.AGORA_APP_ID
        AGORA_APP_CERTIFICATE = settings.AGORA_APP_CERTIFICATE

        token = RtcTokenBuilder.buildTokenWithUid(
            AGORA_APP_ID,
            AGORA_APP_CERTIFICATE,
            channel_name,
            uid,
            1,  # Use 1 for Attendee role
            3600  # Token expiration time in seconds
        )

        return Response({"token": token})




class CallViewSet(viewsets.ViewSet):

    # permission_classes = [IsAuthenticated]  # Only allow authenticated users

    def generate_user_token(self, channel_name, user_id):
        return RtcTokenBuilder.buildTokenWithUid(
            settings.AGORA_APP_ID,
            settings.AGORA_APP_CERTIFICATE,
            channel_name,
            user_id,
            1,  # Use Attendee role
            3600
        )

    def request_call(self, request, mentor_id):
        user = request.user

        mentee = None  # Initialize mentee
        mentor = None  # Initialize mentor

        if hasattr(user, 'mentee_profile'):
            mentee = user.mentee_profile
            role = 'mentee'
        elif hasattr(user, 'mentor_profile'):
            mentor = user.mentor_profile
            role = 'mentor'
        else:
            raise PermissionDenied("User must be either a mentee or a mentor.")

        try:
            mentor = Mentor.objects.get(id=mentor_id)

        except Mentor.DoesNotExist:
            return Response({"error": "Mentor not found."}, status=404)


        # Get the current time and define the end time
        current_time = timezone.now()
        end_time = current_time + timezone.timedelta(minutes=150)

        
        # Query for upcoming confirmed bookings within the next 150 minutes for the specified mentor
        try:
            booking = Booking.objects.get(
                mentor=mentor,
                status='confirmed',
                scheduled_time__range=(current_time, end_time)
            )
            mentee = booking.mentee  # Get the mentee associated with the booking
        except Booking.DoesNotExist:
            return Response({"error": "No confirmed bookings within the next 150 minutes."}, status=404)


        current_time = timezone.now()
        time_difference = (booking.scheduled_time - current_time).total_seconds() / 60  # Difference in minutes

        if time_difference > 1500:
            return Response({"error": "Call can only be initiated 1500 minutes before the scheduled time."}, status=403)

        channel_name = f"call-{mentor.id}-{mentee.id}-{booking.id}"


        # Generate token for the caller
        user_token = self.generate_user_token(channel_name, mentee.user.id if role == 'mentee' else mentor.user.id)


        # # Create the meeting link
        # meeting_link = f"{request.build_absolute_uri(reverse('your_meeting_view_name'))}?channel={channel_name}&token={user_token}"
    
        # # Send email to mentor and mentee
        # subject = "Your Scheduled Call Link"
        # message = f"Hi,\n\nYou have a scheduled call. Click the link below to join:\n{meeting_link}\n\nThanks!"
        
        # send_mail(subject, message, settings.EMAIL_HOST_USER, [mentor.user.email, mentee.user.email])

        return Response({
            "mentor_id": mentor.id,
            "mentee_id": mentee.id,
            "channel_name": channel_name,
            "user_token": user_token,
            # "meeting_link": meeting_link
        })
    

    def accept_call(self, request, channel_name):
        user = request.user

        if hasattr(user, 'mentee_profile'):
            mentee = user.mentee_profile
            role = 'mentee'
        elif hasattr(user, 'mentor_profile'):
            mentor = user.mentor_profile
            role = 'mentor'
        else:
            raise PermissionDenied("User must be either a mentee or a mentor.")

        # Check if the call can be accepted based on the existing bookings
        try:
            booking = Booking.objects.get(channel_name=channel_name)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found."}, status=404)

        # Generate token for the caller
        user_token = self.generate_user_token(channel_name, mentee.user.id if role == 'mentee' else mentor.user.id)
        
        # # Create the meeting link
        # meeting_link = f"{request.build_absolute_uri(reverse('your_meeting_view_name'))}?channel={channel_name}&token={user_token}"

        # # Send email to mentor and mentee
        # subject = "Your Scheduled Call Link"
        # message = f"Hi,\n\nYou have a scheduled call. Click the link below to join:\n{meeting_link}\n\nThanks!"
        
        # send_mail(subject, message, settings.EMAIL_HOST_USER, [mentor.user.email, mentee.user.email])

        return Response({
            "mentor_id": mentor.id,
            "mentee_id": mentee.id,
            "channel_name": channel_name,
            "user_token": user_token,
            # "meeting_link": meeting_link
        })










from rest_framework.permissions import IsAuthenticated
from .models import Booking
from .serializers import BookingSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, serializers



class BookingListView(generics.ListAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]  # Require authentication



# views.py
from django.http import JsonResponse
from django.views import View
from .models import Booking  # Import your Booking model

class CallView(View):
    def get(self, request, call_id):
        try:
            # Fetch the booking based on call_id
            booking = Booking.objects.get(call_link__contains=call_id)
            
            # Prepare the response data
            response_data = {
                'mentor_id': booking.mentor.id,
                'mentee_id': booking.mentee.id,
                'scheduled_time': booking.scheduled_time.isoformat(),
                'duration': booking.duration,
                'call_link': booking.call_link,
                # Add any other necessary details
            }
            return JsonResponse(response_data, status=200)
        
        except Booking.DoesNotExist:
            return JsonResponse({'error': 'Call not found'}, status=404)



# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# views.py

from django.conf import settings
from .utils.google_calendar import create_google_calendar_event, CalendarConflictError
from datetime import datetime, timedelta


# class BookingCreateView_V1_NeedDomain(generics.CreateAPIView):
#     queryset = Booking.objects.all()    
#     serializer_class = BookingSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         print("API hit for booking create")
#         mentee_id = self.request.data.get('mentee')
#         mentor_id = self.request.data.get('mentor')

#         try:
#             mentee = Mentee.objects.get(id=mentee_id)
#             mentor = Mentor.objects.get(id=mentor_id)
#             print(mentee, mentor)

#             print(mentor.google_refresh_token)
            
#             # if not mentor.google_refresh_token:
#             #     raise serializers.ValidationError("Mentor has not connected Google Calendar.")

#             booking = serializer.save(mentee=mentee, mentor=mentor)

#             print("Booking create started")

#             # Use actual scheduled time from booking
#             start_time = booking.scheduled_time
#             end_time = start_time + timedelta(minutes=booking.duration)

#             print(start_time, end_time)

#             meet_link = create_google_calendar_event(
#                 summary="Mentorship Session",
#                 start_time=start_time,
#                 end_time=end_time,
#                 attendees=[mentee.user.email, mentor.user.email]
#                 # refresh_token=mentor.google_refresh_token,
#                 # client_id=settings.GOOGLE_CLIENT_ID,
#                 # client_secret=settings.GOOGLE_CLIENT_SECRET
#             )
            

#             booking.call_link = meet_link
#             booking.status = 'confirmed'
#             booking.save(update_fields=['call_link', 'status'])
 
#         except Mentee.DoesNotExist:
#             raise serializers.ValidationError("Mentee does not exist.")
#         except Mentor.DoesNotExist:
#             raise serializers.ValidationError("Mentor does not exist.")





# class BookingCreateView(generics.CreateAPIView):
#     queryset = Booking.objects.all()    
#     serializer_class = BookingSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         print("API hit for booking create")
#         mentee_id = self.request.data.get('mentee')
#         mentor_id = self.request.data.get('mentor')

#         try:
#             mentee = Mentee.objects.get(id=mentee_id)
#             mentor = Mentor.objects.get(id=mentor_id)
#             print(mentee, mentor)

#             print(mentor.google_refresh_token)
            
#             if not mentor.google_refresh_token:
#                 raise serializers.ValidationError("Mentor has not connected Google Calendar.")

#             booking = serializer.save(mentee=mentee, mentor=mentor)

#             print("Booking create started")

#             # Use actual scheduled time from booking
#             start_time = booking.scheduled_time
#             end_time = start_time + timedelta(minutes=booking.duration)

#             print(start_time, end_time)

#             meet_link = create_google_calendar_event(
#                 summary="Mentorship Session",
#                 start_time=start_time,
#                 end_time=end_time,
#                 attendees=[mentee.user.email, mentor.user.email],
#                 refresh_token=mentor.google_refresh_token,
#                 client_id=settings.GOOGLE_CLIENT_ID,
#                 client_secret=settings.GOOGLE_CLIENT_SECRET
#             )
            

#             booking.call_link = meet_link
#             booking.status = 'confirmed'
#             booking.save(update_fields=['call_link', 'status'])
 
#         except Mentee.DoesNotExist:
#             raise serializers.ValidationError("Mentee does not exist.")
#         except Mentor.DoesNotExist:
#             raise serializers.ValidationError("Mentor does not exist.")




from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated

from .models import Booking, Mentee, Mentor
from .serializers import BookingSerializer


class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        print("API hit for booking create")
        mentee_id = self.request.data.get('mentee')
        mentor_id = self.request.data.get('mentor')

        try:
            mentee = Mentee.objects.get(id=mentee_id)
            mentor = Mentor.objects.get(id=mentor_id)
            print(mentee, mentor)

            if not mentor.google_refresh_token:
                raise serializers.ValidationError("Mentor has not connected Google Calendar.")

            # Use actual scheduled time from booking
            scheduled_time = serializer.validated_data.get("scheduled_time")
            duration = serializer.validated_data.get("duration")
            start_time = scheduled_time
            
            now = timezone.now()

            # Earliest and latest allowed booking times
            min_allowed_time = now + timedelta(hours=6)
            max_allowed_time = now + timedelta(days=7)

            if start_time < min_allowed_time:
                raise serializers.ValidationError(
                    "Bookings must be scheduled at least 6 hours in advance."
                )
            if start_time > max_allowed_time:
                raise serializers.ValidationError(
                    "Bookings cannot be scheduled more than 7 days in advance."
                )


            end_time = start_time + timedelta(minutes=duration)
            
            

            print(f"Checking booking from {start_time} to {end_time}")

            try:
                meet_link = create_google_calendar_event(
                    summary="Mentorship Session",
                    start_time=start_time,
                    end_time=end_time,
                    attendees=[mentee.user.email, mentor.user.email],
                    refresh_token=mentor.google_refresh_token,
                    client_id=settings.GOOGLE_CLIENT_ID,
                    client_secret=settings.GOOGLE_CLIENT_SECRET
                )
            except CalendarConflictError as e:
                raise serializers.ValidationError(str(e))

            # Save booking after Google event is created
            booking = serializer.save(
                mentee=mentee,
                mentor=mentor,
                call_link=meet_link,
                status='confirmed'
            )

            print("Booking confirmed:", booking)

        except Mentee.DoesNotExist:
            raise serializers.ValidationError("Mentee does not exist.")
        except Mentor.DoesNotExist:
            raise serializers.ValidationError("Mentor does not exist.")







# /////////////////////////////////

# booking/views.py

import os
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import google_auth_oauthlib.flow

# from mentor.models import Mentor  # Update path if needed


SCOPES = ['https://www.googleapis.com/auth/calendar']


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import google_auth_oauthlib.flow
from django.conf import settings



class ConnectCalendarView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=SCOPES
        )
        flow.redirect_uri = request.build_absolute_uri('/api/voice_video/oauth2callback/') 

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        print(state)
        request.session['google_oauth_state'] = state
        return Response({'authorization_url': authorization_url}, status=status.HTTP_200_OK)



from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.conf import settings
import google_auth_oauthlib.flow


# from .serializers import CustomUserSerializer  # adjust import to your app


class GoogleOAuthCallbackView(APIView):
    # permission_classes = [IsAuthenticated]
    print("Inside GoogleOAuthCallbackView")
    import os
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    def get(self, request):
        # Print everything for debugging
        print("SESSION:", dict(request.session))
        print("Expected state:", request.session.get('google_oauth_state'))
        print("Returned state:", request.GET.get('state'))

        state = request.session.get('google_oauth_state')

        if not state:
            return HttpResponse("OAuth state missing from session. Try restarting login.", status=400)

        state = request.session.get('google_oauth_state')
        print(state)


        print(settings.GOOGLE_CLIENT_SECRETS_FILE)
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            state=state
        )
        flow.redirect_uri = request.build_absolute_uri('/api/voice_video/oauth2callback/') 
        print(flow.redirect_uri)


        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)

        credentials = flow.credentials
        refresh_token = credentials.refresh_token

        if not refresh_token:
            return HttpResponse("No refresh token received. Try reconnecting with `prompt='consent'`.")
            
        try:
            mentor = Mentor.objects.get(user=request.user)
            mentor.google_refresh_token = refresh_token
            mentor.save()
        except Mentor.DoesNotExist:
            return HttpResponse("Mentor not found for this user.", status=404)

        return HttpResponse("Google calendar connected successfully! You can close this window.")



# ///////////////////////////////

