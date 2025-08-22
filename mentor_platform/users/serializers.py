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

    feedback_count = serializers.SerializerMethodField()

    class Meta:
        model = Mentor
        fields = [
            'id', 'user', 'phone_number', 'profile_picture', 'country' ,'university',
            'degree', 'major', 'year_of_admission', 'college_id', 'expertise',
            'availability', 'rating', 'entrance_exam_given',
            'rank', 'score', 'calls_booked', 'feedback_count', 'about'
        ]


    def get_feedback_count(self, obj):
        return Feedback.objects.filter(mentor=obj).count()
    

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



# from rest_framework import serializers
# from .models import Feedback, Mentor

# class FeedbackSerializer(serializers.ModelSerializer):
#     mentor = serializers.PrimaryKeyRelatedField(queryset=Mentor.objects.all())
#     mentee = serializers.PrimaryKeyRelatedField(read_only=True)  # Mentee set automatically in view

#     class Meta:
#         model = Feedback
#         fields = [
#             'id',
#             'mentor',
#             'mentee',
#             'session_date',
#             'rating',
#             'comments',
#             'created_at',
#             'updated_at',
#             'is_visible'
#         ]
#         read_only_fields = ['created_at', 'updated_at', 'is_visible']


from rest_framework import serializers
from .models import Feedback, Mentor, Mentee

from rest_framework import serializers
from .models import Feedback, Mentor

class FeedbackSerializer(serializers.ModelSerializer):
    mentor = serializers.PrimaryKeyRelatedField(queryset=Mentor.objects.all())
    mentee = serializers.PrimaryKeyRelatedField(read_only=True)

    # Custom field for full name
    mentee_name = serializers.SerializerMethodField(read_only=True)
    mentor_name = serializers.CharField(source="mentor.user.get_full_name", read_only=True)

    class Meta:
        model = Feedback
        fields = [
            'id',
            'mentor',
            'mentor_name',
            'mentee',
            'mentee_name',   # 👈 new field
            # 'session_date',
            'rating',
            'comments',
            'created_at',
            'updated_at',
            'is_visible'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_visible']

    def get_mentee_name(self, obj):
        """Return mentee full name (first + last)"""
        if obj.mentee and obj.mentee.user:
            return f"{obj.mentee.user.first_name} {obj.mentee.user.last_name}".strip()
        return obj.mentee.user.username if obj.mentee and obj.mentee.user else None






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




from rest_framework import serializers
from .models import Post, Comment



class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    author_image = serializers.ImageField(source="author.profile_picture", read_only=True)


    class Meta:
        model = Comment
        fields = ["id", "post", "author", "author_username", "author_image",  "text", "created_at"]  # ✅ include post
        read_only_fields = ["id", "author", "author_username", "author_image", "created_at"]


# from rest_framework import serializers
# from .models import Comment

# class CommentSerializer(serializers.ModelSerializer):
#     author_username = serializers.CharField(source="author.username", read_only=True)

#     class Meta:
#         model = Comment
#         fields = ["id", "author", "author_username", "text", "created_at", "content_type", "object_id"]
#         read_only_fields = ["author", "created_at"]



class PostSerializer(serializers.ModelSerializer):
    mentor_name = serializers.CharField(source="mentor.user.username", read_only=True)
    mentor_image = serializers.ImageField(source="mentor.user.profile_picture", read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "mentor", "mentor_name", "mentor_image", "content", "created_at", "likes_count", "liked_by_user", "comments"]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_liked_by_user(self, obj):
        user = self.context.get("request").user
        return user in obj.likes.all() if user.is_authenticated else False





from .models import MentorAvailability, Mentor

# Serializer for MentorAvailability model
class MentorAvailabilitySerializer(serializers.ModelSerializer):
    
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = MentorAvailability
        fields = ['id', 'mentor', 'day_of_week', 'day_of_week_display', 'start_time', 'end_time']
        read_only_fields = ['mentor']


from rest_framework import serializers
from .models import SessionOption

class SessionOptionSerializer(serializers.ModelSerializer):
    mentor_name = serializers.CharField(source="mentor.user.username", read_only=True)

    class Meta:
        model = SessionOption
        fields = ["id", "mentor", "mentor_name", "duration_minutes", "fee", "currency"]

