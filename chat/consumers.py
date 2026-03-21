from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import hashlib
import json
from .models import Message


def make_group_name(room_name):
    """将房间名转为 channel layer 允许的 ASCII group name"""
    h = hashlib.md5(room_name.encode()).hexdigest()[:12]
    return f'chat_{h}'


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.username = "nobody"
        if "user" in self.scope and self.scope["user"].is_authenticated:
            self.username = self.scope["user"].username
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = make_group_name(self.room_name)

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        import datetime
        currentDT = datetime.datetime.now()
        datetime_str = currentDT.strftime("%Y-%m-%d %H:%M:%S")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': "用户 %s 加入 %s 房间" % (self.username, self.room_name),
                'username': "BOT",
                'datetime': datetime_str
            }
        )

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def save_message(self, message, username, room_name, room_group_name):
        from django.contrib.auth.models import User
        msg = Message()
        msg.message = message
        msg.username = username
        msg.room_name = room_name
        msg.room_group_name = room_group_name
        if username != "nobody":
            try:
                msg.user = User.objects.get(username=username)
            except User.DoesNotExist:
                pass
        msg.save()

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        import datetime
        from .tasks import execute
        if text_data is None:
            return
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        if len(message) == 0:
            return

        if "from_bot" in text_data_json:
            username = "BOT"
        else:
            username = self.username

        if message[0] == '/' and '=' in message:
            command = message.split('=')[0]
            parameter = message.split('=')[1]
            execute.s(command, parameter, self.room_group_name).apply_async(serializer="pickle")

        currentDT = datetime.datetime.now()
        datetime_str = currentDT.strftime("%Y-%m-%d %H:%M:%S")

        if "from_bot" not in text_data_json:
            await self.save_message(message, username, self.room_name, self.room_group_name)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'datetime': datetime_str
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        datetime = event['datetime']
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'datetime': datetime,
        }))
