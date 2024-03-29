import json

from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
from accounts.models import User
from .models import Chat

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
    
    def disconnect(self, close_code):
        # Leave room
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from web socket
    def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        room = data['room_name']
        sender_type = data['sender_type']
        
        user = User.objects.get(username=username)

        async_to_sync(self.save_message)(user, room, message, sender_type)

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'sender_type':sender_type
            }
        )
    
    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        username = event['username']
        sender_type = event['sender_type']
        
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'sender_type':sender_type
        }))

    @sync_to_async
    def save_message(self, user, room, message, sender_type):
        Chat.objects.create(sender=user, room_name=room, message=message, sender_type=sender_type)