# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import GroupMessage, Group
from users.models import CustomUser
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist

async def get_user_instance(username):
    return await database_sync_to_async(CustomUser.objects.get)(username=username)


async def get_group_instance(group_id):
    return await database_sync_to_async(Group.objects.get)(id=group_id)


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        print("New grp request")
        print(self)

        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.user = self.scope["user"]

        # Join group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        try:
            group = await get_group_instance(self.group_name)
        except ObjectDoesNotExist:
            print(f"Group {self.group_name} does not exist.")
            return  # Handle this case as needed

        sender = text_data_json['sender']

        # Get sender user instance
        try:
            sender_user = await get_user_instance(sender)
        except ObjectDoesNotExist:
            print(f"User {sender} does not exist.")
            return  # Handle this case as needed
       
        # Save the message to the database
        group_message = GroupMessage(
            group=group,  # Assuming this is a field in your model
            message=text_data_json['message'],
            sender=sender_user,
            timestamp=text_data_json['timestamp'],
            profile_picture=text_data_json.get('profile_picture')  # Use .get() for safety
        )

        await database_sync_to_async(group_message.save)()
        
        # Send message to group
        await self.channel_layer.group_send(
            self.group_name, 
            {
                "message": text_data_json['message'],
                "sender": text_data_json['sender'],
                "timestamp": text_data_json['timestamp'],
                "type": "chat_message",
                "profile_picture" : text_data_json['profile_picture']
            })

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": event['message'],
      "sender": event['sender'],
      "timestamp": event['timestamp'],
      "type": "chat_message",
      "profile_picture" : event['profile_picture']
        }))


class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'private_chat_{self.user_id}'

        # Join private chat group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = self.scope['user'].username

        # Send message to private chat group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'private_chat_message',
                'message': message,
                'sender': sender
            }
        )

    async def private_chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
