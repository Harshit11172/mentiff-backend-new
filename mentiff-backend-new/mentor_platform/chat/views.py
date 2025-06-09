
# chat/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Group, GroupMessage
from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Group, Membership
from .serializers import GroupListSerializer, GroupSerializer, MemberDetailSerializer, GroupMessageSerializer
from rest_framework import viewsets
from users.models import OTP


class GroupChatView(LoginRequiredMixin, View):
    login_url = '/api/users/login/'  # Redirect to this URL if not logged in
    redirect_field_name = 'next'  # Redirect to the original URL after login

    def get(self, request, group_id="1"):
        print(f"Request user: {request.user}")
        print(f"User is authenticated: {request.user.is_authenticated}")
        print(f"Session data: {request.session.items()}") 

        group = get_object_or_404(Group, id=group_id)
        messages = GroupMessage.objects.filter(group=group).order_by('timestamp')
        print("I'm here in GroupChatView")

        # return redirect(f'/chat/{group_id}/')
        return render(request, 'chat/group_chat.html', {'group': group, 'messages': messages})


class JoinGroupView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        user = request.user

        # Check if the user is already a member
        if not Membership.objects.filter(user=user, group=group).exists():
            # Create a membership
            Membership.objects.create(user=user, group=group, user_type=user.user_type)

        return Response({"message": "Joined the group successfully."}, status=200)
    

# class GroupListViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = Group.objects.prefetch_related('membership_set__user')  # Pre-fetch memberships and associated users
    
#     # Use different serializers for listing and detail views
#     def get_serializer_class(self):
#         if self.action == 'retrieve':
       
#             return GroupSerializer  # Use GroupSerializer for detail view
#         return GroupListSerializer  # Use GroupListSerializer for list view

#     def retrieve(self, request, *args, **kwargs):
#         # Retrieve the specific group
#         return super().retrieve(request, *args, **kwargs)


class GroupListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.prefetch_related('membership_set__user')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GroupSerializer  # Detailed view
        return GroupListSerializer  # Listing view

    def get_permissions(self):
        if self.action == 'retrieve':
            self.authentication_classes = [TokenAuthentication]
            return [IsAuthenticated()]
        return []  # Allow public access for listing


class GroupMembersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MemberDetailSerializer

    def get_queryset(self):
        group_id = self.kwargs.get('group_id')
        return Membership.objects.filter(group_id=group_id).select_related('user')


class GroupMessageListView(generics.ListAPIView):
    serializer_class = GroupMessageSerializer

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        return GroupMessage.objects.filter(group_id=group_id).order_by('timestamp')
    


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from .models import Group, Membership
from django.db import IntegrityError

User = get_user_model()

class CreateOrAddMentorToGroupView(APIView):
    """
    This view handles creating a new group (if not exists) based on the college name,
    adding the mentor to the group, and updating the group's member and mentor counts.
    """

    def post(self, request, *args, **kwargs):
        # Extract the data from the request body
        print(request.body)
        college = request.data.get('college')
        country = request.data.get('country')
        mentor_id = request.data.get('mentor_id')

        print('Hello from CreateOrAddMentorToGroupView')
        # Validate input data
        if not college or not country or not mentor_id:
            raise ValidationError("Missing required fields: college, country, and username.")
        
        try:
            # 1. Check if the group with the given college exists
            group, created = Group.objects.get_or_create(
                college=college,
                defaults={
                    'country': country,
                    'group_name': college,  # Assuming group_name is based on the college
                    'member_count': 1,      # Initial count with the mentor
                    'mentor_count': 1,      # Initially just one mentor
                    'mentee_count': 0       # No mentees initially
                }
            )
            
            # 2. Get the mentor user
            try:
                mentor_user = User.objects.get(id=mentor_id)
            except User.DoesNotExist:
                return Response({"error": "Mentor not found."}, status=status.HTTP_404_NOT_FOUND)

            # 3. Create the mentor profile if not already created
            
            # mentor = Mentor.objects.create(user=mentor_user, additional_details=mentor_additional_details)

            # 4. Create the Membership entry to add the mentor to the group
            membership = Membership.objects.create(
                user=mentor_user, 
                group=group, 
                user_type='mentor'
            )

            # 5. Update the mentor count in the group
            group.update_mentor_count()
            group.update_member_count()  # Update overall member count

            # 6. Return the success response with updated group details
            return Response({
                "message": "Mentor added to group successfully.",
                "group": {
                    "group_name": group.group_name,
                    "college": group.college,
                    "mentor_count": group.mentor_count,
                    "member_count": group.member_count,
                    "mentee_count": group.mentee_count,
                }
            }, status=status.HTTP_201_CREATED)
        
        except IntegrityError as e:
            # Catch database integrity errors
            return Response({"error": f"Database error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
