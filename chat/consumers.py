import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from django.core.cache import cache

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        user1 = self.scope['user'].username 
        user2 = self.room_name
        self.room_group_name = f"chat_{''.join(sorted([user1, user2]))}"

        # Set user as online
        await self.set_user_online(self.scope['user'].username)

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Broadcast user's online status
        await self.channel_layer.group_send(
            'presence',
            {
                'type': 'user_status',
                'user': self.scope['user'].username,
                'status': 'online'
            }
        )

        # Mark messages as delivered when user connects to chat
        await self.mark_messages_as_delivered()

    async def disconnect(self, close_code):
        # Set user as offline
        await self.set_user_offline(self.scope['user'].username)

        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Broadcast user's offline status
        await self.channel_layer.group_send(
            'presence',
            {
                'type': 'user_status',
                'user': self.scope['user'].username,
                'status': 'offline'
            }
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = self.scope['user']  
        receiver = await self.get_receiver_user()

        # Save message and get its status
        saved_message = await self.save_message(sender, receiver, message)
        message_status = await self.get_message_status(saved_message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'sender': sender.username,
                'receiver': receiver.username,
                'message': message,
                'status': message_status
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']
        status = event.get('status', 'sent')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'sender': sender,
            'receiver': receiver,
            'message': message,
            'status': status
        }))

    async def user_status(self, event):
        # Send status update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'status',
            'user': event['user'],
            'status': event['status']
        }))

    @sync_to_async
    def save_message(self, sender, receiver, message):
        msg = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=message,
            status=Message.SENT
        )
        return msg

    @sync_to_async
    def get_message_status(self, message):
        return message.status

    @sync_to_async
    def mark_messages_as_delivered(self):
        # Mark all unread messages in this chat as delivered
        Message.objects.filter(
            receiver=self.scope['user'],
            sender__username=self.room_name,
            status=Message.SENT
        ).update(status=Message.DELIVERED)

    @sync_to_async
    def mark_messages_as_read(self):
        # Mark all delivered messages in this chat as read
        Message.objects.filter(
            receiver=self.scope['user'],
            sender__username=self.room_name,
            status=Message.DELIVERED
        ).update(status=Message.READ)

    @sync_to_async
    def get_receiver_user(self):
        return User.objects.get(username=self.room_name)

    @sync_to_async
    def set_user_online(self, username):
        cache.set(f'user_status_{username}', 'online', timeout=None)

    @sync_to_async
    def set_user_offline(self, username):
        cache.set(f'user_status_{username}', 'offline', timeout=None)