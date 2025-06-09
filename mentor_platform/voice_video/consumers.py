import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("in call consumer!!!!")
        print(self.scope['url_route'])
        self.room_id = self.scope['url_route']['kwargs']['call_id']
        
        self.room_group_name = f'call_{self.room_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data['type']
        print("Under receive in consumer of call")
        print(message_type)
        
        if message_type in ['offer', 'answer', 'ice_candidate']:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': message_type,
                    'data': data
                }
            )

    async def offer(self, event):
        await self.send(text_data=json.dumps(event['data']))

    async def answer(self, event):
        await self.send(text_data=json.dumps(event['data']))

    async def ice_candidate(self, event):
        await self.send(text_data=json.dumps(event['data']))
