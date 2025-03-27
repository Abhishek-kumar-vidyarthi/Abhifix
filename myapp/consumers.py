# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            
            self.user_id = self.scope['url_route']['kwargs']['user_id']
            self.group_name = f'user_{self.user_id}'

            
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            # Accept the WebSocket connection
            await self.accept()
            print(f"WebSocket connected for user {self.user_id}")  # Debugging
        except Exception as e:
            print(f"WebSocket connection error: {e}")  # Debugging
            await self.close()  # Close the connection if there's an error

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected for user {self.user_id} with code {close_code}")  # Debugging
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass  # Handle incoming messages (if needed)

    async def notification_message(self, event):
        message = event['message']

        # Send message to the client
        await self.send(text_data=json.dumps({
            'message': message
        }))