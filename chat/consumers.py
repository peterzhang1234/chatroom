from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        if "user" in self.scope:
            self.username = self.scope["user"].username
            self.user = self.scope["user"]
        else:
            self.username = "nobody"
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        import datetime

        currentDT = datetime.datetime.now()
        datetime = currentDT.strftime("%Y-%m-%d %H:%M:%S")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': "用户 %s 加入 %s 房间" % (self.username, self.room_name,),
                'username': "BOT",
                'datetime': datetime
            }
        )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        import datetime
        from .tasks import execute
        text_data_json = json.loads(text_data)
        print(text_data)
        message = text_data_json['message']
        if len(message) == 0:
            return False

        if "from_bot" in text_data_json:
            username = "BOT"
        else:
            username = self.username

        if message[0] == '/' and '=' in message:
            command = message.split('=')[0]
            parameter = message.split('=')[1]
            execute.s(command, parameter, self.room_group_name).apply_async(serializer="pickle")
        currentDT = datetime.datetime.now()
        datetime = currentDT.strftime("%Y-%m-%d %H:%M:%S")
        # Send message to room group
        msg = Message()
        msg.message = message
        if not "from_bot" in text_data_json:
            msg.user = self.user
        msg.username = self.username
        msg.room_name = self.room_name
        msg.room_group_name = self.room_group_name
        msg.save()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'datetime': datetime
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        datetime = event['datetime']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'datetime': datetime,
        }))
