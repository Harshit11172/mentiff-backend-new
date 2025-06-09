# your_project_name/urls.py
from django.contrib import admin
from .views import GroupChatView, JoinGroupView, GroupListViewSet, GroupMembersView, GroupMessageListView, CreateOrAddMentorToGroupView
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Initialize the router
router = DefaultRouter()
router.register(r'universities/groups', GroupListViewSet, basename='group-list')

urlpatterns = [
    path('', include(router.urls)),  # Include the router URLs
    path('group/chat/', GroupChatView.as_view(), name='GroupChatView'),
    path('group/<int:group_id>/join/', JoinGroupView.as_view(), name='join_group'),
    path('groups/<int:group_id>/members/', GroupMembersView.as_view(), name='group-members'),
    path('group/messages/<int:group_id>/', GroupMessageListView.as_view(), name='group-messages'),
    path('group/add-mentor/', CreateOrAddMentorToGroupView.as_view(), name='add-mentor-to-group'),
]




# With this setup, the viewset will automatically handle requests like:

# GET /groups/ for listing all groups.
# GET /groups/{id}/ for retrieving a specific group by its ID.