from rest_framework import serializers
from .models import Group, GroupMessage, Membership
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta


User = get_user_model() 

class GroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'group_name', 'college', 'logo', 'country', 'url', 'member_count', 'mentor_count', 'mentee_count']


class GroupMessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.username')  # Use the username field from the sender
    profile_picture = serializers.ImageField(source='sender.profile_picture', allow_null=True)  # Adjusted to reference the user

    class Meta:
        model = GroupMessage
        fields = ['group', 'sender', 'message', 'timestamp', 'profile_picture']


    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Format timestamp
        timestamp = instance.timestamp
        now = timezone.now()
        diff = now - timestamp

        if diff < timedelta(minutes=1):
            formatted_time = "Just now"
        elif diff < timedelta(hours=1):
            minutes_ago = diff.seconds // 60
            formatted_time = f"{minutes_ago} minutes ago"
        elif timestamp.date() == now.date():
            formatted_time = f"Today at {timestamp.strftime('%I:%M %p')}"
        elif timestamp.date() == (now - timedelta(days=1)).date():
            formatted_time = f"Yesterday at {timestamp.strftime('%I:%M %p')}"
        else:
            formatted_time = timestamp.strftime('%B %d, %Y at %I:%M %p')  # Include time

        representation['timestamp'] = formatted_time  # Update the formatted timestamp
        return representation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


# class MembershipSerializer(serializers.ModelSerializer):
#     user = UserSerializer(read_only=True)  
#     user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)

#     class Meta:
#         model = Membership
#         fields = ['user', 'user_id', 'user_type', 'username', 'email', 'first_name', 'last_name', 'last_login', 'date_joined', 'is_active', 'user_permissions']


class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)
    username = serializers.CharField(source='user.username', read_only=True)  # From User model
    email = serializers.EmailField(source='user.email', read_only=True)        # From User model
    first_name = serializers.CharField(source='user.first_name', read_only=True)  # From User model
    last_name = serializers.CharField(source='user.last_name', read_only=True)    # From User model
    last_login = serializers.DateTimeField(source='user.last_login', read_only=True)  # From User model
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)  # From User model
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)      # From User model
    user_permissions = serializers.PrimaryKeyRelatedField(source='user.user_permissions', read_only=True, many=True)  # From User model
    profile_picture = serializers.ImageField(source='user.profile_picture', read_only=True)  # New profile picture field

    class Meta:
        model = Membership
        fields = ['user', 'user_id', 'username', 'user_type', 'email', 'first_name', 'last_name', 'profile_picture', 'last_login', 'date_joined', 'is_active', 'user_permissions']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Include mentor-specific fields if user_type is 'mentor'
        if instance.user.user_type == 'mentor':
            # Adding mentor-specific fields
            representation['expertise'] = instance.user.mentor_profile.expertise  # Expertise area
            representation['session_fee'] = instance.user.mentor_profile.session_fee  # Fee for sessions
            representation['session_time'] = instance.user.mentor_profile.session_time  # sessions time
            representation['currency'] = instance.user.mentor_profile.currency  # currency
            representation['university'] = instance.user.mentor_profile.university  # University name
            representation['degree'] = instance.user.mentor_profile.degree  # Degree obtained
            representation['major'] = instance.user.mentor_profile.major  # Major subject
            representation['year_of_admission'] = instance.user.mentor_profile.year_of_admission  # Year of admission
            # representation['available_days'] = instance.user.mentor_profile.available_days  # Available days
            # representation['available_hours'] = instance.user.mentor_profile.available_hours  # Available hours
            representation['phone_number'] = instance.user.mentor_profile.phone_number  # Phone number
            representation['about'] = instance.user.mentor_profile.about  # about me
            representation['availability'] = instance.user.mentor_profile.availability  # availability


        return representation
    

class GroupSerializer(serializers.ModelSerializer):
    admins = UserSerializer(many=True)
    members = MembershipSerializer(many=True, required=False, source='membership_set')

    class Meta:
        model = Group
        fields = [
            'id', 'group_name', 'admins', 'members', 
            'college','logo', 'country', 'url', 
            'member_count', 'mentor_count', 'mentee_count'
        ]


class MemberDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Assuming you already have UserSerializer defined

    class Meta:
        model = Membership
        fields = ['user', 'user_type']
