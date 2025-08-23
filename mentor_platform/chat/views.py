
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
from rest_framework.decorators import action
from django.db.models import Count

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


    @action(detail=False, methods=['get'], url_path='top')
    def top_groups(self, request):
        """
        Returns top groups sorted by number of messages (GroupMessage model).
        Example: /api/universities/groups/top/?limit=5
        """
        limit = request.query_params.get('limit', 10)
        try:
            limit = int(limit)
        except ValueError:
            return Response({"detail": "Invalid limit parameter."}, status=status.HTTP_400_BAD_REQUEST)

        # Annotate each group with the number of messages
        top_groups = (
            Group.objects
            .annotate(message_count=Count('groupmessage'))  # reverse FK: GroupMessage → Group
            .order_by('-message_count')[:limit]
        )

        serializer = self.get_serializer(top_groups, many=True)
        return Response(serializer.data)

    


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





# class CreateOrAddMentorToGroupView(APIView):
#     """
#     This view handles creating a new group (if not exists) based on the college name,
#     adding the mentor to the group, and updating the group's member and mentor counts.
#     """

#     def post(self, request, *args, **kwargs):
#         # Extract the data from the request body
#         print(request.body)
#         college = request.data.get('college')
#         country = request.data.get('country')
#         mentor_id = request.data.get('mentor_id')
#         group_name = request.data.get('university_short_name')

#         print('Hello from CreateOrAddMentorToGroupView')
#         # Validate input data
#         if not college or not country or not mentor_id:
#             raise ValidationError("Missing required fields: college, country, and username.")
        
#         try:
#             # 1. Check if the group with the given college exists
#             group, created = Group.objects.get_or_create(
#                 college=college,
#                 defaults={
#                     'country': country,
#                     'group_name': college,  # Assuming group_name is based on the college
#                     'member_count': 1,      # Initial count with the mentor
#                     'mentor_count': 1,      # Initially just one mentor
#                     'mentee_count': 0       # No mentees initially
#                 }
#             )
            
#             # 2. Get the mentor user
#             try:
#                 mentor_user = User.objects.get(id=mentor_id)
#             except User.DoesNotExist:
#                 return Response({"error": "Mentor not found."}, status=status.HTTP_404_NOT_FOUND)

#             # 3. Create the mentor profile if not already created
            
#             # mentor = Mentor.objects.create(user=mentor_user, additional_details=mentor_additional_details)

#             # 4. Create the Membership entry to add the mentor to the group
#             membership = Membership.objects.create(
#                 user=mentor_user, 
#                 group=group, 
#                 user_type='mentor'
#             )

#             # 5. Update the mentor count in the group
#             group.update_mentor_count()
#             group.update_member_count()  # Update overall member count

#             # 6. Return the success response with updated group details
#             return Response({
#                 "message": "Mentor added to group successfully.",
#                 "group": {
#                     "group_name": group.group_name,
#                     "college": group.college,
#                     "mentor_count": group.mentor_count,
#                     "member_count": group.member_count,
#                     "mentee_count": group.mentee_count,
#                 }
#             }, status=status.HTTP_201_CREATED)
        
#         except IntegrityError as e:
#             # Catch database integrity errors
#             return Response({"error": f"Database error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class CreateOrAddMentorToGroupView(APIView):
    """
    This view handles creating a new group (if not exists) based on the college name,
    adding the mentor to the group, and updating the group's member and mentor counts.
    """

    def post(self, request, *args, **kwargs):
        # Extract the data from the request body
        print(request.body)
        
        # Basic required fields
        college = request.data.get('college')
        country = request.data.get('country')
        mentor_id = request.data.get('mentor_id')
        
        # University data fields from frontend
        university_name = request.data.get('university_name')
        university_city = request.data.get('university_city')
        university_state = request.data.get('university_state')
        university_country = request.data.get('university_country')
        university_domain = request.data.get('university_domain')
        university_url = request.data.get('university_url')
        university_short_name = request.data.get('university_short_name')
        university_category = request.data.get('university_category', [])

        print('Hello from CreateOrAddMentorToGroupView')
        
        # Validate input data
        if not college or not country or not mentor_id:
            raise ValidationError("Missing required fields: college, country, and mentor_id.")
        
        try:
            # 1. Check if the group with the given college exists
            group, created = Group.objects.get_or_create(
                college=college,
                defaults={
                    # Use university data if available, otherwise fallback to basic data
                    'group_name': university_short_name or college,
                    'country': university_country or country,
                    'city': university_city or '',
                    'state': university_state or '',
                    'url': university_url or '',
                    'domain': university_domain or '',
                    'category': ', '.join(university_category) if isinstance(university_category, list) else university_category or '',
                    
                    # Initial counts
                    'member_count': 1,      # Initial count with the mentor
                    'mentor_count': 1,      # Initially just one mentor
                    'mentee_count': 0       # No mentees initially
                }
            )
            
            # If group already exists but we have new university data, update it
            if not created and university_name:
                # Update group with complete university information if available
                update_fields = {}
                
                if university_short_name and not group.group_name:
                    update_fields['group_name'] = university_short_name
                if university_country and not group.country:
                    update_fields['country'] = university_country
                if university_city and not group.city:
                    update_fields['city'] = university_city
                if university_state and not group.state:
                    update_fields['state'] = university_state
                if university_url and not group.url:
                    update_fields['url'] = university_url
                if university_domain and not group.domain:
                    update_fields['domain'] = university_domain
                if university_category and not group.category:
                    update_fields['category'] = ', '.join(university_category) if isinstance(university_category, list) else university_category
                
                # Update the group if there are fields to update
                if update_fields:
                    for field, value in update_fields.items():
                        setattr(group, field, value)
                    group.save()
                    print(f"Updated group with university data: {update_fields}")
            
            # 2. Get the mentor user
            try:
                mentor_user = User.objects.get(id=mentor_id)
            except User.DoesNotExist:
                return Response({"error": "Mentor not found."}, status=status.HTTP_404_NOT_FOUND)

            # 3. Check if mentor is already a member of this group
            existing_membership = Membership.objects.filter(
                user=mentor_user, 
                group=group
            ).first()
            
            if existing_membership:
                return Response({
                    "message": "Mentor is already a member of this group.",
                    "group_id": group.id,
                    "group": {
                        "group_name": group.group_name,
                        "college": group.college,
                        "city": group.city,
                        "state": group.state,
                        "country": group.country,
                        "url": group.url,
                        "domain": group.domain,
                        "category": group.category,
                        "mentor_count": group.mentor_count,
                        "member_count": group.member_count,
                        "mentee_count": group.mentee_count,
                    }
                }, status=status.HTTP_200_OK)

            # 4. Create the Membership entry to add the mentor to the group
            membership = Membership.objects.create(
                user=mentor_user, 
                group=group, 
                user_type='mentor'
            )

            # 5. Update the counts in the group only if this is a new membership
            if created:
                # For new groups, counts are already set in defaults
                pass
            else:
                # For existing groups, update the counts
                group.update_mentor_count()
                group.update_member_count()

            # 6. Return the success response with updated group details
            return Response({
                "message": "Mentor added to group successfully." if not created else "New group created and mentor added successfully.",
                "group_id": group.id,
                "group_created": created,
                "group": {
                    "group_name": group.group_name,
                    "college": group.college,
                    "city": group.city,
                    "state": group.state,
                    "country": group.country,
                    "url": group.url,
                    "domain": group.domain,
                    "category": group.category,
                    "mentor_count": group.mentor_count,
                    "member_count": group.member_count,
                    "mentee_count": group.mentee_count,
                }
            }, status=status.HTTP_201_CREATED)
        
        except IntegrityError as e:
            # Catch database integrity errors
            return Response({"error": f"Database error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            # Catch any other unexpected errors
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)