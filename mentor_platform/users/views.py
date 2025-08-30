#views.py

from rest_framework import viewsets
from .models import Mentor, Mentee, Feedback
from voice_video.models import Booking
from .serializers import MentorSerializer, MenteeSerializer, FeedbackSerializer, MentorSignupSerializer, MenteeSignupSerializer
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from django.conf import settings
#-------------login-Logout-Signup----------------------------------

from rest_framework import generics, permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import get_user_model
from .serializers import CustomUserSerializer  # Create this serializer
from rest_framework import status
from users.mail_utils import send_otp_email  # You need to implement this
from users.mail_utils import send_verification_email  # You need to implement this

from users.models import OTP  # A model to store OTPs if needed
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from django.utils.crypto import get_random_string
from users.models import OTP  # Ensure this import is present

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import serializers, generics
from rest_framework.response import Response
from django.core.mail import send_mail
from django.urls import reverse
from .models import CustomUser
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from chat.models import Membership
from rest_framework.decorators import action


User = get_user_model()


class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer  # Serializer to handle user creation
    permission_classes = [permissions.AllowAny]



class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({'error': 'Email and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid email or OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the OTP is valid
        try:
            otp_instance = OTP.objects.get(user=user, code=otp, is_verified=False)
            # Mark the OTP as verified
            otp_instance.is_verified = True
            otp_instance.save()
            
            # Check if the user is verified
            if not user.is_verified:
                print("User not verified")
                return Response({'error': 'Your account is not verified. Please check your email to verify your account.'}, status=status.HTTP_400_BAD_REQUEST)


            token, created = Token.objects.get_or_create(user=user)

            # Get groups where the user is a mentor
            # Filter the Membership table to find groups where the user is a mentor
            mentor_memberships = Membership.objects.filter(user=user, user_type='mentor')
            groups = [membership.group for membership in mentor_memberships]
            print(mentor_memberships)
            print(groups)
            
            # Prepare the group data
            group_data = []
            for group in groups:
                group_data.append({
                    'group_name': group.group_name,
                    'group_id': group.id,
                    'college': group.college,
                    'logo_url': request.build_absolute_uri(group.logo.url) if group.logo else None
                })
            
            mentor_id = None
            mentee_id = None
            about = None
            profile_picture = None

            if user.user_type == 'mentor' and hasattr(user, 'mentor_profile'):
                mentor_id = user.mentor_profile.id
                about = user.mentor_profile.about
                profile_picture = request.build_absolute_uri(user.mentor_profile.profile_picture.url) if user.mentor_profile.profile_picture else None
            elif user.user_type == 'mentee' and hasattr(user, 'mentee_profile'):
                mentee_id = user.mentee_profile.id
                profile_picture = request.build_absolute_uri(user.mentee_profile.profile_picture.url) if user.mentee_profile.profile_picture else None



            # Prepare user data to return
            user_data = {
                'id': user.id,
                'mentor_id': mentor_id,
                'mentee_id': mentee_id,
                'username': user.username,
                'email': user.email,
                'profile_picture': profile_picture,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_type': user.user_type,
                'groups': group_data # Include the group data here
               
            }
            # Only include "about" if it's a mentor
            if about is not None:
                user_data['about'] = about

            return Response({
                'token': token.key,
                'user': user_data
            })
        except OTP.DoesNotExist:
            return Response({'error': 'Invalid email or OTP.'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        return Response({
            'message': 'Send a POST request with "email" and "otp" to login.',
            'example': {
                'email': 'your_email@example.com',
                'otp': '123456'
            }
        }, status=status.HTTP_200_OK)

    def send_otp(self, user):
        otp_code = get_random_string(length=6, allowed_chars='0123456789')  # Generate a random OTP
        print("otp is: ")
        print(otp_code)
        OTP.objects.create(user=user, code=otp_code)  # Store the OTP in the database
        send_otp_email(user.email, otp_code)  # Send the OTP via email





class RequestOTP(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            # Generate OTP
            otp_code = get_random_string(length=6, allowed_chars='0123456789')
            print("otp is: ")
            print(otp_code)
            OTP.objects.create(user=user, code=otp_code)  # Save OTP to the database
            send_otp_email(user.email, otp_code)  # Send the OTP email

            return Response({'message': 'OTP sent to your email.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)


class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully."})

##-----------------------------------------------------------------


from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

class MentorViewSet(viewsets.ModelViewSet):
    queryset = Mentor.objects.all()
    serializer_class = MentorSerializer
    permission_classes = [AllowAny]


    def get_queryset(self):
        """
        Supports filtering mentors via query parameters:
        - ?country=
        - ?college=
        - ?gender=
        - ?degree=PhD,Masters
        - ?course=
        """
        queryset = super().get_queryset()
        request = self.request

        country = request.query_params.get("country")
        college = request.query_params.get("college")
        # gender = request.query_params.get("gender")
        degree = request.query_params.get("degree")  # comma-separated string
        course = request.query_params.get("course")  # optional
        # date = request.query_params.get("date")  # for future use

        if country:
            queryset = queryset.filter(country__iexact=country)

        if college:
            queryset = queryset.filter(university__iexact=college)

        # if gender:
        #     queryset = queryset.filter(user__gender__iexact=gender)

        if degree:
            degrees = [d.strip() for d in degree.split(",") if d.strip()]
            if degrees:
                queryset = queryset.filter(degree__in=degrees)

        if course:
            courses = [c.strip() for c in course.split(",") if c.strip()]
            queryset = queryset.filter(expertise__in=courses)

        # If you plan to filter by availability in the future:
        # if date:
        #     # Add logic to filter availability on that date
        #     pass

        return queryset


    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except NotFound:
            return Response({"detail": "Mentor not found."}, status=status.HTTP_404_NOT_FOUND)

    
    @action(detail=False, methods=['get'], url_path='top')
    def top_mentors(self, request):
        """
        Returns top mentors sorted by number of calls_booked in descending order.
        Example: /api/users/mentors/top/?limit=4
        """
        limit = request.query_params.get('limit', 4)

        try:
            limit = int(limit)
        except ValueError:
            return Response({"detail": "Invalid limit parameter."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the field exists and query safely
        top_mentors = Mentor.objects.all().order_by('-calls_booked')[:limit]
        serializer = self.get_serializer(top_mentors, many=True)
        return Response(serializer.data)



class MenteeViewSet(viewsets.ModelViewSet):
    queryset = Mentee.objects.all()
    serializer_class = MenteeSerializer
    # permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except NotFound:
            return Response({"detail": "Mentor not found."}, status=status.HTTP_404_NOT_FOUND)



class MentorUpdateView(generics.UpdateAPIView):
    queryset = Mentor.objects.all()
    serializer_class = MentorSerializer





class MenteeUpdateView(generics.UpdateAPIView):
    queryset = Mentee.objects.all()
    serializer_class = MenteeSerializer


from rest_framework import viewsets, generics, status
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Feedback, Mentor, Mentee
from .serializers import FeedbackSerializer




from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from .serializers import FeedbackSerializer




class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()   # 👈 add this line back
    serializer_class = FeedbackSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        mentor_id = self.request.query_params.get("mentor_id")

        # If ?mentor_id= is passed, return feedback for that mentor
        if mentor_id:
            return Feedback.objects.filter(mentor_id=mentor_id, is_visible=True)

        # Otherwise filter by logged-in user role
        if user.user_type == "mentee":
            return Feedback.objects.filter(mentee=user.mentee_profile)
        elif user.user_type == "mentor":
            return Feedback.objects.filter(mentor=user.mentor_profile)
        return Feedback.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.user_type != "mentee":
            raise PermissionDenied("Only mentees can submit feedback.")

        try:
            mentee = user.mentee_profile
        except Mentee.DoesNotExist:
            raise ValidationError("You do not have an associated Mentee profile.")

        mentor_id = self.request.data.get("mentor")
        if not mentor_id:
            raise ValidationError("Mentor ID is required.")

        try:
            mentor = Mentor.objects.get(id=mentor_id)
        except Mentor.DoesNotExist:
            raise ValidationError("Mentor not found.")

        # Ensure session is completed
        # completed_bookings = Booking.objects.filter(
        #     mentee=mentee,
        #     mentor=mentor,
        #     status="completed"
        # )
        # if not completed_bookings.exists():
        #     raise ValidationError(
        #         "You must complete a session with this mentor before giving feedback."
        #     )

        # Prevent duplicate feedback for same session_date
        session_date = self.request.data.get("session_date")
        if session_date:
            existing_feedback = Feedback.objects.filter(
                mentor=mentor, mentee=mentee, session_date=session_date
            ).exists()
            if existing_feedback:
                raise ValidationError("You’ve already submitted feedback for this session.")

        serializer.save(mentee=mentee, mentor=mentor)







# class FeedbackCreateView(generics.CreateAPIView):
#     queryset = Feedback.objects.all()
#     serializer_class = FeedbackSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         user = self.request.user

#         if user.user_type != 'mentee':
#             raise PermissionDenied("Only mentees can submit feedback.")

#         try:
#             mentee = user.mentee_profile
#         except Mentee.DoesNotExist:
#             raise ValidationError("You do not have an associated Mentee profile.")

#         mentor_id = self.request.data.get('mentor')
#         if not mentor_id:
#             raise ValidationError("Mentor ID is required.")

#         try:
#             mentor = Mentor.objects.get(id=mentor_id)
#         except Mentor.DoesNotExist:
#             raise ValidationError("Mentor not found.")

#         # Check for completed bookings
#         completed_bookings = Booking.objects.filter(
#             mentee=mentee,
#             mentor=mentor,
#             status='completed'
#         )

#         if not completed_bookings.exists():
#             raise ValidationError("You must complete a session with this mentor before giving feedback.")

#         # Check if feedback already exists for this mentor + mentee + session (optional)
#         session_date = self.request.data.get('session_date')
#         if session_date:
#             existing_feedback = Feedback.objects.filter(
#                 mentor=mentor,
#                 mentee=mentee,
#                 session_date=session_date
#             ).exists()
#             if existing_feedback:
#                 raise ValidationError("You’ve already submitted feedback for this session.")

#         serializer.save(mentee=mentee, mentor=mentor)






User = get_user_model()

class EmailVerificationView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        
        print("GET REQUEST FOR LINK VERIFICATION")

        try:
            user = User.objects.get(verification_token=token)

            if user.user_type == 'mentor':

                country = request.data.get("country", None)
                if country is None:
                    raise ValidationError({"error": "country is required."})
                
                university = request.data.get("university", None)
                if university is None:
                    raise ValidationError({"error": "university is required."}) 
                
                college = request.data.get("college", None)
                if university is None:
                    raise ValidationError({"error": "college is required."})
                
                degree = request.data.get("degree", None)
                if degree is None:
                    raise ValidationError({"error": "degree is required."})

                year_of_admission = request.data.get("year_of_admission", None)
                if year_of_admission is None:
                    raise ValidationError({"error": "year_of_admission is required."})

                university_short_name = request.data.get("university_short_name", None)


                university_city = request.data.get("university_city", None)


                university_domain = request.data.get("university_domain", None)
                    
                   
                university_state = request.data.get("university_state", None)
                   


            user.is_verified = True  # Mark as verified
            user.is_active = True  # Activate the account
            # user.verification_token = None  # Clear the token
            user.save()

            # Create profile based on user type
            if user.user_type == 'mentor':
                Mentor.objects.create(
                    user=user,
                    university=university,
                    country=country,
                    college=college,
                    degree=degree,
                    year_of_admission=year_of_admission,
                    #new added
                    university_short_name = university_short_name,
                    university_city=university_city,
                    university_state=university_state,
                    university_domain=university_domain

                )  
            elif user.user_type == 'mentee':
                Mentee.objects.create(
                    user = user
                ) 

            # Returning the entire user object (you can select which fields to return)
            user_data = {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email,
                "user_type": user.user_type,
                "is_verified": user.is_verified,
                "is_active": user.is_active,
                "verification_status": user.verification_status,
                "profile_picture": user.profile_picture.url if user.profile_picture else None,
                "message": "Email verified successfully!"
                # Add other relevant user fields as needed
            }

            return Response(user_data, status=200)

        except User.DoesNotExist:
            return Response({"error": "Invalid token or user already verified."}, status=400)

    def post(self, request, token):
        """
        Handle POST request to update the verification status based on the provided request body.
        """
        user = User.objects.get(verification_token=token)

        print("POST REQUEST FOR LINK VERIFICATION")
        print("user found as", user.user_type)
        
        verification_status = request.data.get("verification_status", None)

        if verification_status is None:
            raise ValidationError({"error": "verification_status is required."})

        if verification_status not in ['pending', 'verified', 'rejected']:
            raise ValidationError({"error": "Invalid verification_status value. Must be one of ['pending', 'verified', 'rejected']."})

        try:
            user = User.objects.get(verification_token=token)

            if verification_status == 'pending':
                # Set the user's verification status to 'pending'
                user.verification_status = 'pending'
                user.save()

                user_data = {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "username": user.username,
                    "user_type": user.user_type,
                    "is_verified": user.is_verified,
                    "is_active": user.is_active,
                    "verification_status": user.verification_status,
                    "profile_picture": user.profile_picture.url if user.profile_picture else None,
                    "message": "Verification status set to pending."
                    # Add other relevant user fields as needed
                }

                return Response(user_data, status=200)

            # Other status updates (optional):
            if verification_status == 'verified':
                if user.user_type == 'mentor':
                    country = request.data.get("country", None)
                    if country is None:
                        raise ValidationError({"error": "country is required."})
                    
                    university = request.data.get("university", None)
                    if university is None:
                        raise ValidationError({"error": "university is required."})
                    
                    college = request.data.get("college", None)
                    if university is None:
                        raise ValidationError({"error": "college is required."})
                    
                    degree = request.data.get("degree", None)
                    if degree is None:
                        raise ValidationError({"error": "degree is required."})

                    year_of_admission = request.data.get("year_of_admission", None)
                    if year_of_admission is None:
                        raise ValidationError({"error": "year_of_admission is required."})                    


                user.is_verified = True  # Set verified status
                user.is_active = True    # Activate the account
                user.verification_status = 'verified'  # Set the verification status to 'verified'
                user.verification_token = None  # Clear the token
                user.save()

                # Create profiles based on user type
                if user.user_type == 'mentor':
                    Mentor.objects.create(
                        user=user,
                        university=university,
                        college=college,
                        country=country,
                        degree=degree,
                        year_of_admission=year_of_admission
                    )
                
                elif user.user_type == 'mentee':
                    print("creating mentee object in db...")
                    Mentee.objects.create(user=user)
                
                
                # Returning the entire user object (you can select which fields to return)
                user_data = {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "user_type": user.user_type,
                    "username": user.username,
                    "is_verified": user.is_verified,
                    "is_active": user.is_active,
                    "verification_status": user.verification_status,
                    "profile_picture": user.profile_picture.url if user.profile_picture else None,
                    "message": "Email verified successfully!"
                    # Add other relevant user fields as needed
                }
                return Response(user_data, status=200)

            if verification_status == 'rejected':
                user.is_verified = False  # Set verification as failed
                user.is_active = False    # Deactivate the account
                user.verification_status = 'rejected'  # Set the status to rejected
                user.save()

                return Response({"message": "Verification failed or rejected."}, status=200)

        except User.DoesNotExist:
            return Response({"error": "Invalid token."}, status=400)

class MentorSignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = MentorSignupSerializer  # Serializer to handle user creation
    permission_classes = [permissions.AllowAny]


class MenteeSignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = MenteeSignupSerializer  # Serializer to handle user creation
    permission_classes = [permissions.AllowAny]


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        print("Email found for resending verification link")
        # Check if the user exists and is inactive (not verified)
        if not CustomUser.objects.filter(email=value, is_active=False).exists():
            raise serializers.ValidationError("This email is either not registered or already verified.")
        return value


class ResendVerificationEmailView(generics.GenericAPIView):
    serializer_class = ResendVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        user = CustomUser.objects.get(email=email)
        
        # Generate new verification token
        token = get_random_string(length=32)
        user.verification_token = token
        user.save()

        # Send verification email

        verification_link = f"{settings.API_BASE_URL_FRONTEND}/verify-email?token={token}"

        print(f"Resend Verification link is: {verification_link}")
        
        # send_mail(
        #     'Verify your College Email',
        #     f'Please click the link to verify your email: {verification_link}',
        #     'mentiff5@gmail.com',
        #     [user.email],
        #     fail_silently=False,
        # )

        # Replace your existing send_mail call with:
        
        success = send_verification_email(
            email=user.email,
            verification_link=verification_link,
            user_name=user.first_name if hasattr(user, 'first_name') else None  # Optional personalization
        )

        if success:
            # Email sent successfully
            messages.success(request, 'Verification email sent! Please check your inbox.')
        else:
            # Email failed to send
            messages.error(request, 'Failed to send verification email. Please try again.')

        return Response({"message": "Verification email resent."}, status=status.HTTP_200_OK)



from django.http import JsonResponse, Http404
from django.views import View
from .models import CustomUser, Mentor, Mentee


class UserGroupsView(View):
    def get(self, request, username):
        try:
            # Retrieve the user object based on the username
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            # If user does not exist, return a 404 error
            raise Http404("User not found")

        groups = set()  # We'll use a set to avoid duplicate group names

        # Check if the user has a mentor profile
        if hasattr(user, 'mentor_profile'):
            mentor = user.mentor_profile
            if mentor.university:
                groups.add(mentor.university)
            if mentor.college:
                groups.add(mentor.college)

        # Check if the user has a mentee profile
        if hasattr(user, 'mentee_profile'):
            mentee = user.mentee_profile
            if mentee.university:
                groups.add(mentee.university)
            if mentee.college:
                groups.add(mentee.college)

        # If no groups found, return a default message
        if not groups:
            groups.add("No university or college information")

        # Return the groups as a JSON response
        return JsonResponse({"username": username, "groups": list(groups)})



from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, MentorAvailabilitySerializer




class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        mentor_id = self.request.query_params.get("mentor_id")
        if mentor_id:
            return Post.objects.filter(mentor_id=mentor_id).order_by("-created_at")
        return Post.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'mentor_profile'):
            serializer.save(mentor=user.mentor_profile)

    @action(detail=True, methods=["post"], url_path='like', url_name='like')
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            return Response({"liked": False})
        else:
            post.likes.add(user)
            return Response({"liked": True})



class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_id = self.request.query_params.get("post_id")
        return Comment.objects.filter(post_id=post_id).order_by("created_at")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)




# from django.contrib.contenttypes.models import ContentType
# from rest_framework import viewsets
# from .models import Comment, Post, Feedback
# from .serializers import CommentSerializer

# class CommentViewSet(viewsets.ModelViewSet):
#     serializer_class = CommentSerializer
#     # permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         model = self.request.query_params.get("model")  # "post" or "feedback"
#         object_id = self.request.query_params.get("object_id")

#         if not (model and object_id):
#             return Comment.objects.none()

#         try:
#             content_type = ContentType.objects.get(model=model)
#         except ContentType.DoesNotExist:
#             return Comment.objects.none()

#         return Comment.objects.filter(
#             content_type=content_type, object_id=object_id
#         ).order_by("created_at")

#     def perform_create(self, serializer):
#         model = self.request.data.get("model")   # "post" or "feedback"
#         object_id = self.request.data.get("object_id")

#         content_type = ContentType.objects.get(model=model)

#         serializer.save(
#             author=self.request.user,
#             content_type=content_type,
#             object_id=object_id
#         )










from .models import MentorAvailability, Mentor
from django.shortcuts import get_object_or_404


# ViewSet to list, create, update, and delete availabilities for a mentor
class MentorAvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = MentorAvailabilitySerializer
    queryset = MentorAvailability.objects.all()
                            
    def get_queryset(self):
        # Filter by mentor if provided in URL kwargs
        mentor_id = self.kwargs.get('mentor_pk') or self.request.query_params.get('mentor_id')
        if mentor_id:
            return self.queryset.filter(mentor_id=mentor_id).order_by('day_of_week', 'start_time')
        return self.queryset.none()

    def perform_create(self, serializer):
        mentor_id = self.kwargs.get('mentor_pk') or self.request.data.get('mentor')
        mentor = get_object_or_404(Mentor, pk=mentor_id)
        serializer.save(mentor=mentor)

    @action(detail=False, methods=['put', 'patch'], url_path='bulk-update')
    def bulk_update(self, request, mentor_pk=None):
        """
        Custom action to update multiple availability entries in one request.
        Accepts list of availabilities with id or new ones without id.
        """
        availabilities = request.data.get('availabilities', [])
        if not isinstance(availabilities, list):
            return Response({'detail': 'availabilities must be a list'}, status=status.HTTP_400_BAD_REQUEST)

        response_data = []
        for item in availabilities:
            avail_id = item.get('id', None)
            # If id exists, update, else create new
            if avail_id:
                try:
                    availability = MentorAvailability.objects.get(id=avail_id, mentor_id=mentor_pk)
                except MentorAvailability.DoesNotExist:
                    continue  # Or handle error differently
                serializer = self.get_serializer(availability, data=item, partial=True)
            else:
                item['mentor'] = mentor_pk
                serializer = self.get_serializer(data=item)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response_data.append(serializer.data)
        return Response(response_data)



from rest_framework import viewsets, permissions, decorators, response
from .models import SessionOption
from .serializers import SessionOptionSerializer


# Now you’ll get:

# /api/session-options/mentor/5/ → all options for mentor with id=5

# /api/session-options/ → all session options (default list endpoint)

# /api/session-options/<pk>/ → a single session option (still works)

class SessionOptionViewSet(viewsets.ModelViewSet):
    queryset = SessionOption.objects.all()
    serializer_class = SessionOptionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # still allow filtering with ?mentor_id=
        mentor_id = self.request.query_params.get("mentor_id")
        if mentor_id:
            return self.queryset.filter(mentor_id=mentor_id)
        return self.queryset

    @decorators.action(detail=False, url_path="mentor/(?P<mentor_id>[^/.]+)")
    def by_mentor(self, request, mentor_id=None):
        """Return all session options for a given mentor ID"""
        sessions = self.queryset.filter(mentor_id=mentor_id)
        serializer = self.get_serializer(sessions, many=True)
        return response.Response(serializer.data)

    


# FOR GOOLGE DIRECT LOGIN


# authapp/views.py
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Mentee  # import your Mentee model
from .utils.auth_utils import generate_unique_username  # adjust import path if needed

User = get_user_model()

def issue_tokens_for_user(user):
    token, _ = Token.objects.get_or_create(user=user)

    return {token.key}


class GoogleMenteeAuthView(APIView):
    """
    POST /api/auth/google/
    Body: { "credential": "<google_id_token>" }
    Behavior:
      - If user with google_sub exists: log in (only if user_type == 'mentee').
      - Else if user with email exists:
          - mark is_verified=True, verification_status='verified'
          - attach google_sub
          - ensure user_type becomes 'mentee' (if blank/None) or if it's 'mentor'/'admin', return error
          - create Mentee profile if missing
      - Else (no user):
          - create new CustomUser with is_verified=True, verification_status='verified', user_type='mentee', username auto-generated
          - create associated Mentee profile
    """
    
    authentication_classes = []  # public
    permission_classes = []

    def post(self, request):
        print(f'payload from api is : {request.data}')
        token = request.data.get("credential") or request.data.get("id_token") or request.data.get("token")
        if not token:
            return Response({"detail": "Missing credential"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            print(f'login google client id is: {settings.LOGIN_GOOGLE_CLIENT_ID}')
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), settings.LOGIN_GOOGLE_CLIENT_ID)
        except Exception:
            return Response({"detail": "Invalid Google token"}, status=status.HTTP_401_UNAUTHORIZED)

        # Basic required fields
        google_sub = idinfo.get("sub")
        email = idinfo.get("email")
        email_verified = idinfo.get("email_verified", False)
        full_name = idinfo.get("name", "")
        first_name = idinfo.get("given_name", "") or (full_name.split(" ")[0] if full_name else "")
        last_name = idinfo.get("family_name", "") or (" ".join(full_name.split(" ")[1:]) if full_name and len(full_name.split(" "))>1 else "")
        picture = idinfo.get("picture", "")

        # sanity checks
        if not google_sub or not email or not email_verified:
            return Response({"detail": "Incomplete or unverified Google profile"}, status=status.HTTP_400_BAD_REQUEST)

        # Start DB transaction to ensure atomicity
        with transaction.atomic():
            # 1) Try by google_sub first (idempotent)
            user = User.objects.filter(google_sub=google_sub).first()

            if user:
                # Found a linked user
                # Only allow mentees for this endpoint
                if getattr(user, "user_type", None) != "mentee":
                    return Response({"detail": "This Google account is linked to a non-mentee user."}, status=status.HTTP_403_FORBIDDEN)

                # ensure verified flags are set
                user.is_verified = True
                user.verification_status = "verified"
                user.save(update_fields=["is_verified", "verification_status"])
                token = issue_tokens_for_user(user)
                mentor_id = None
                mentee_id = None
                about = None
                profile_picture = None

                if user.user_type == 'mentor' and hasattr(user, 'mentor_profile'):
                    mentor_id = user.mentor_profile.id
                    about = user.mentor_profile.about
                    profile_picture = request.build_absolute_uri(user.mentor_profile.profile_picture.url) if user.mentor_profile.profile_picture else None
                elif user.user_type == 'mentee' and hasattr(user, 'mentee_profile'):
                    mentee_id = user.mentee_profile.id
                    profile_picture = request.build_absolute_uri(user.mentee_profile.profile_picture.url) if user.mentee_profile.profile_picture else None

                resp = {
                    "user": {"id": user.id, "profile_picture": profile_picture, "mentee_id": mentee_id, "mentor_id": mentor_id,  "first_name": user.first_name, "last_name": user.last_name, "email": user.email, "username": user.username, "user_type": user.user_type},
                    "token": token
                }
                return Response(resp, status=status.HTTP_200_OK)

            # 2) Else try by email
            user_by_email = User.objects.filter(email__iexact=email).first()
            if user_by_email:
                # If this existing user is mentor/admin, block because you only want mentee to use this flow
                if getattr(user_by_email, "user_type", None) and user_by_email.user_type != "mentee":
                    return Response({"detail": "An account with this email exists as a mentor. Login via OTP!"}, status=status.HTTP_403_FORBIDDEN)

                # Attach google_sub, mark verified, and create mentee if missing
                user_by_email.google_sub = google_sub
                user_by_email.is_verified = True
                user_by_email.verification_status = "verified"
                # If user_type blank/None, set to mentee:
                if not getattr(user_by_email, "user_type", None):
                    user_by_email.user_type = "mentee"
                # Update name if empty
                if not user_by_email.first_name:
                    user_by_email.first_name = first_name
                if not user_by_email.last_name:
                    user_by_email.last_name = last_name
                user_by_email.save()

                # Ensure Mentee profile exists
                mentee = getattr(user_by_email, "mentee_profile", None)
                if mentee is None:
                    mentee_data = {"user": new_user}
                    if picture:  # if Google provided profile picture
                        mentee_data["profile_picture"] = picture  

                    Mentee.objects.create(**mentee_data)
                    mentor_id = None
                    mentee_id = None
                    about = None
                    profile_picture = None

                    if user_by_email.user_type == 'mentor' and hasattr(user_by_email, 'mentor_profile'):
                        mentor_id = user_by_email.mentor_profile.id
                        about = user_by_email.mentor_profile.about
                        profile_picture = request.build_absolute_uri(user_by_email.mentor_profile.profile_picture.url) if user_by_email.mentor_profile.profile_picture else None
                    elif user_by_email.user_type == 'mentee' and hasattr(user_by_email, 'mentee_profile'):
                        mentee_id = user_by_email.mentee_profile.id
                        profile_picture = request.build_absolute_uri(user_by_email.mentee_profile.profile_picture.url) if user_by_email.mentee_profile.profile_picture else None

                    token = issue_tokens_for_user(user_by_email)
                    resp = {
                        "user": {
                            "id": user_by_email.id,
                            "profile_picture": profile_picture,
                            "mentee_id": mentee_id,
                            "mentor_id": mentor_id,
                            "first_name": user_by_email.first_name,
                            "last_name": user_by_email.last_name,
                            "email": user_by_email.email,
                            "username": user_by_email.username,
                            "user_type": user_by_email.user_type,
                        },
                        "token": token
                    }
                    return Response(resp, status=status.HTTP_200_OK)


            # 3) No user exists -> create user + mentee (auto-verified)
            username = generate_unique_username(email)
            new_user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_verified=True,
                verification_status="verified",
                user_type="mentee",
                google_sub=google_sub,
            )

            # Create mentee entry (fill minimal required fields)
            Mentee.objects.create(user=new_user, profile_picture=None)
            
            mentor_id = None
            mentee_id = None
            about = None
            profile_picture = None

            if new_user.user_type == 'mentor' and hasattr(new_user, 'mentor_profile'):
                mentor_id = new_user.mentor_profile.id
                about = new_user.mentor_profile.about
                profile_picture = request.build_absolute_uri(new_user.mentor_profile.profile_picture.url) if new_user.mentor_profile.profile_picture else None
            elif new_user.user_type == 'mentee' and hasattr(new_user, 'mentee_profile'):
                mentee_id = new_user.mentee_profile.id
                profile_picture = request.build_absolute_uri(new_user.mentee_profile.profile_picture.url) if new_user.mentee_profile.profile_picture else None

            token = issue_tokens_for_user(new_user)
            resp = {
                "user": {
                    "id": new_user.id,
                    "profile_picture": profile_picture,
                    "mentee_id": mentee_id,
                    "mentor_id": mentor_id,
                    "first_name": new_user.first_name,
                    "last_name": new_user.last_name,
                    "email": new_user.email,
                    "username": new_user.username,
                    "user_type": new_user.user_type,
                },
                "token": token
            }
            return Response(resp, status=status.HTTP_201_CREATED)





# normal sign in response is {
#   "id": 10,
#   "mentor_id": null,
#   "mentee_id": 16,
#   "username": "mentee2",
#   "email": "rajnipathak0107@gmail.com",
#   "profile_picture": null,
#   "first_name": "R",
#   "last_name": "Pathak",
#   "user_type": "mentee",
#   "groups": []
# } 


# response from google sign in is :
# {
#   "id": 10,
#   "profile_picture": null,
#   "mentee_id": 16,
#   "mentor_id": null,
#   "first_name": "R",
#   "last_name": "Pathak",
#   "email": "rajnipathak0107@gmail.com",
#   "username": "mentee2",
#   "user_type": "mentee"
# }