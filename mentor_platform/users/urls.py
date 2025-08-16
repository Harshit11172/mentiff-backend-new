from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MentorViewSet, MenteeViewSet, FeedbackViewSet,
    MentorSignUpView, MenteeSignUpView, ResendVerificationEmailView,
    SignUpView, CustomAuthToken, LogoutView, MentorUpdateView,
    EmailVerificationView, FeedbackCreateView, MenteeUpdateView,
    RequestOTP, UserGroupsView,
    PostViewSet, CommentViewSet,
      MentorAvailabilityViewSet  # ✅ Import post and comment viewsets
)
from .views import SessionOptionViewSet


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'mentors', MentorViewSet)
router.register(r'mentees', MenteeViewSet)
router.register(r'feedbacks', FeedbackViewSet)

# ✅ Register post and comment endpoints
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'mentors/(?P<mentor_pk>\d+)/availabilities', MentorAvailabilityViewSet, basename='mentor-availabilities')
router.register(r'session-options', SessionOptionViewSet, basename="session-options")


urlpatterns = [
    path('', include(router.urls)),

    path('signup/', SignUpView.as_view(), name='signup'),
    path('signup/mentor/', MentorSignUpView.as_view(), name='mentorsignup'),
    path('signup/mentee/', MenteeSignUpView.as_view(), name='menteesignup'),

    path('login/', CustomAuthToken.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('verify-email/<str:token>/', EmailVerificationView.as_view(), name='verify_email'),
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='resend_verification'),

    path('post/feedback/', FeedbackCreateView.as_view(), name='post-feedback'),

    path('api/token/', CustomAuthToken.as_view(), name='custom_auth_token'),
    path('api/request-otp/', RequestOTP.as_view(), name='request_otp'),

    path('update/mentor/<int:pk>/', MentorUpdateView.as_view(), name='mentor-update'),
    path('update/mentee/<int:pk>/', MenteeUpdateView.as_view(), name='mentee-update'),

    path('<str:username>/', UserGroupsView.as_view(), name='user_groups'),
]
