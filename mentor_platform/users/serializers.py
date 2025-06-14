# serializers.py

from rest_framework import serializers
from .models import CustomUser, Mentor, Mentee, Feedback
from django.conf import settings

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'profile_picture' ,'last_name', 'email', 'user_type']


class MentorSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()  # Nested serializer to include user details

    class Meta:
        model = Mentor
        fields = [
            'id', 'user', 'phone_number', 'profile_picture', 'university',
            'degree', 'major', 'year_of_admission', 'college_id', 'expertise',
            'availability', 'session_fee', 'rating', 'entrance_exam_given',
            'rank', 'score'
        ]
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        # Update Mentor fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update User fields if user_data is provided
        if user_data:
            user_instance = instance.user  # Get the existing user instance
            for attr, value in user_data.items():
                # Only update fields that are being sent in the request
                if attr in user_instance.__dict__:  # Check if attribute exists
                    setattr(user_instance, attr, value)  # Update user fields
            user_instance.save()  # Save the updated user instance

        return instance


    

class MenteeSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)  # Nested serializer to include user details

    class Meta:
        model = Mentee
        fields = [
            'id', 'user', 'phone_number', 'profile_picture', 'university',
            'degree', 'major', 'year_of_study', 'college_id', 'desired_expertise',
            'preferred_session_times', 'budget', 'goals', 'feedback'
        ]



class FeedbackSerializer(serializers.ModelSerializer):
    mentor = serializers.PrimaryKeyRelatedField(queryset=Mentor.objects.all())
    mentee = serializers.PrimaryKeyRelatedField(read_only=True)  # Make mentee read-only

    class Meta:
        model = Feedback
        fields = ['id', 'mentor', 'mentee', 'session_date', 'rating', 'comments']


##-------login/logout/signup---------

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'user_type')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user

##  New ------------------------------------


from django.core.mail import send_mail
from django.urls import reverse
from django.utils.crypto import get_random_string

class MentorSignupSerializer(serializers.ModelSerializer):

    # university = serializers.CharField(required=False, allow_blank=True)
    # degree = serializers.CharField(required=False, allow_blank=True)
    # year_of_admission = serializers.IntegerField(required=False, allow_null=True)
    # country = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        validated_data['user_type'] = 'mentor'
        validated_data['is_active'] = False  # Set to inactive until verified
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        
        # Generate verification token
        token = get_random_string(length=32)
        user.verification_token = token
        user.save()

        # Send verification email
        # verification_link = f"{settings.API_BASE_URL_FRONTEND}/register?verify-email?token={token}"
        verification_link = f"{settings.API_BASE_URL_FRONTEND}/register?verify-email=true&token={token}&user=mentor"

        print(verification_link)
        
        send_mail(
            'Verify your College Email',
            f'Please click the link to verify your email: {verification_link}',
            'mentout@gmail.com',
            [user.email],
            fail_silently=False,
        )

        return user


class MenteeSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        validated_data['user_type'] = 'mentee'
        validated_data['is_active'] = False  # Set to inactive until verified
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        # Generate verification token
        token = get_random_string(length=32)
        user.verification_token = token
        user.save()

        # Send verification email
        
        # verification_link = f"{settings.API_BASE_URL_FRONTEND}/verify-email?token={token}"
        verification_link = f"{settings.API_BASE_URL_FRONTEND}/register?verify-email=true&token={token}&user=mentee"

        print(f"1st time Verification link is: {verification_link}")

        send_mail(
            'Verify your College Email',
            f'Please click the link to verify your email as a Mentee: {verification_link}',
             'mentout@gmail.com',
            [user.email],
            fail_silently=False,
        )

        return user


