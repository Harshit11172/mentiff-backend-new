# # services/google_calendar.py

# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build
# from datetime import datetime, timedelta
# import uuid


# def create_google_calendar_event(summary, start_time, end_time, attendees, refresh_token, client_id, client_secret):
#     credentials = Credentials(
#         token=None,
#         refresh_token=refresh_token,
#         token_uri='https://oauth2.googleapis.com/token',
#         client_id=client_id,
#         client_secret=client_secret
#     )
#     credentials.refresh(Request())

#     service = build('calendar', 'v3', credentials=credentials)

#     event = {
#         'summary': summary,
#         'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
#         'end': {'dateTime': end_time.isoformat(), 'timeZone': 'UTC'},
#         'attendees': [{'email': email} for email in attendees],
#         'conferenceData': {
#             'createRequest': {
#                 'requestId': str(uuid.uuid4()),  # should be unique
#                 'conferenceSolutionKey': {'type': 'hangoutsMeet'}
#             }
#         }
#     }

#     event = service.events().insert(
#         calendarId='primary',
#         body=event,
#         conferenceDataVersion=1
#     ).execute()

#     return event.get('hangoutLink')




# services/google_calendar.py

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime
import uuid

class CalendarConflictError(Exception):
    """Custom exception for booking conflicts."""
    pass

def create_google_calendar_event(summary, start_time, end_time, attendees, refresh_token, client_id, client_secret):
    # Authenticate using stored refresh token
    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=client_id,
        client_secret=client_secret
    )
    credentials.refresh(Request())
    service = build('calendar', 'v3', credentials=credentials)

    # ---- STEP 1: Check for conflicts ----
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_time.isoformat(),
        timeMax=end_time.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    if events:
        # There is at least one conflicting event
        raise CalendarConflictError("There is already a booking in this time slot.")

    # ---- STEP 2: Create event ----
    event = {
        'summary': summary,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'UTC'},
        'attendees': [{'email': email} for email in attendees],
        'conferenceData': {
            'createRequest': {
                'requestId': str(uuid.uuid4()),
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        }
    }

    event = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1
    ).execute()

    return event.get('hangoutLink')





from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def create_google_calendar_event_v1_need_domain(summary, start_time, end_time, attendees ):
    credentials = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    ).with_subject('mentiff5@gmail.com')  # Impersonate a user in your domain

    service = build('calendar', 'v3', credentials=credentials)

    event = {
        'summary': summary,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'UTC'},
        'attendees': [{'email': email} for email in attendees],
        'conferenceData': {
            'createRequest': {
                'requestId': f"mentiff-{start_time.timestamp()}",
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        }
    }

    created_event = service.events().insert(
        calendarId='primary',  # Or a specific calendar you own
        body=event,
        conferenceDataVersion=1   
    ).execute()

    return created_event['hangoutLink']
