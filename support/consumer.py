import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import AnonymousTicket, TicketMessage

class AnonymousTicketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ticket_token = self.scope['url_route']['kwargs']['ticket_token']
        self.ticket_group_name = f'chat_{self.ticket_token}'

        is_valid = await self.check_ticket_exists(self.ticket_token)

        if not is_valid:
            await self.close()
            return
        
        await self.channel_layer.group_add(self.ticket_group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.ticket_group_name, self.channel_name)

    async def receive(self, text_data, bytes_data):
        data = json.loads(text_data)
        message = data['message']

        await self.save_message(self.ticket_token, message, 'user')


        await self.channel_layer.group_send(
            self.ticket_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': 'user',
            }
        )
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamps': event.get("timestamp")
        }))

    @database_sync_to_async
    def check_ticket_exists(self, token):
        try:
            return AnonymousTicket.objects.filter(token=token).exists()
        except ValueError:
            return False
        
    @database_sync_to_async
    def save_message(self, token, content, sender_type):
        try:
            ticket = AnonymousTicket.objects.filter(token=token)
            TicketMessage.objects.create(
                ticket=ticket,
                sender_type=sender_type,
                content=content
            )
        except AnonymousTicket.DoesNotExist:
            print(f"Error: Ticket with token {token} not found for saving message.")