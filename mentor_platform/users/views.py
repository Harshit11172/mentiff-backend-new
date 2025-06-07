#views.py

from rest_framework import viewsets
from .models import Mentor, Mentee, Feedback
from voice_video.models import Booking
from .serializers import MentorSerializer, MenteeSerializer, FeedbackSerializer, MentorSignupSerializer, MenteeSignupSerializer
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError

#-------------login-Logout-Signup----------------------------------

from rest_framework import generics, permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import get_user_model
from .serializers import CustomUserSerializer  # Create this serializer
from rest_framework import status
from users.utils import send_otp_email  # You need to implement this
from users.models import OTP  # A model to store OTPs if needed
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from django.utils.crypto import get_random_string
from users.models import OTP  # Ensure this import is present
from users.utils import send_otp_email  # Implement this function to send OTPs

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

            # Prepare user data to return
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'profile_picture': request.build_absolute_uri(user.profile_picture.url) if user.profile_picture else None,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_type': user.user_type,
                'groups': group_data  # Include the group data here
            }

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

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except NotFound:
            return Response({"detail": "Mentor not found."}, status=status.HTTP_404_NOT_FOUND)


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


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer


class FeedbackCreateView(generics.CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    # permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = self.request.user
        print(f"User: {user.username}, User Type: {user.user_type}")

        if user.user_type != 'mentee':
            raise ValueError("User is not a mentee.")

        print(self.request.user.mentee_profile)
        
        try:
            mentee = user.mentee_profile

            # Get mentor from the request data
            mentor = self.request.data.get('mentor')
            if not mentor:
                raise ValidationError("Mentor ID is required.")

            try:
                mentor = Mentor.objects.get(id=mentor)
            except Mentor.DoesNotExist:
                raise ValidationError("Mentor not found.")

            # Check for completed bookings associated with the mentee and mentor
            completed_bookings = Booking.objects.filter(mentee=mentee, mentor=mentor, status='completed')
            if not completed_bookings.exists():
                raise ValidationError("You have no completed bookings with this mentor for feedback.")

            # Save feedback with the specified mentor
            serializer.save(mentee=mentee, mentor=mentor)

        except Mentee.DoesNotExist:
            raise ValidationError("You do not have an associated Mentee profile.")
        


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
                    year_of_admission=year_of_admission
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
        # verification_link = f"http://127.0.0.1:3000{reverse('verify_email', args=[token])}"

        verification_link = f"http://localhost:3000/verify-email?token={token}"

        print(f"Resend Verification link is: {verification_link}")
        
        send_mail(
            'Verify your College Email',
            f'Please click the link to verify your email: {verification_link}',
            'mentout@gmail.com',
            [user.email],
            fail_silently=False,
        )

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
