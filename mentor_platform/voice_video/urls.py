from django.urls import path
from .views import GoogleOAuthCallbackView, ConnectCalendarView, TokenGenerationView, CallViewSet, BookingCreateView, BookingListView, CallView


# Create an instance of CallViewSet for the relevant actions
call_viewset = CallViewSet.as_view({
    'post': 'request_call',  # For starting a call
})

accept_viewset = CallViewSet.as_view({
    'post': 'accept_call',  # For accepting a call
})

urlpatterns = [
    path('generate-token/', TokenGenerationView.as_view(), name='generate_token'),
    path('start-call/<int:mentor_id>/', call_viewset, name='start_call'),  # Endpoint to start a call
    path('accept-call/<str:channel_name>/', accept_viewset, name='accept_call'),  # Endpoint to accept a call
    path('create/booking/', BookingCreateView.as_view(), name='booking-create'),
    path('list/bookings/', BookingListView.as_view(), name='booking-list'),
    path('call/<uuid:call_id>/', CallView.as_view(), name='call'),
    path('connect-calendar/', ConnectCalendarView.as_view(), name='connect-calendar'),
    path('oauth2callback/', GoogleOAuthCallbackView.as_view(), name='oauth2callback'),
]


