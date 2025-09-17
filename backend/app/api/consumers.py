"""
WebSocket consumers for WorkerNet Portal.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


class TicketConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for ticket updates."""
    
    async def connect(self):
        """Connect to ticket WebSocket."""
        self.ticket_id = self.scope['url_route']['kwargs']['ticket_id']
        self.ticket_group_name = f'ticket_{self.ticket_id}'
        
        # Join ticket group
        await self.channel_layer.group_add(
            self.ticket_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Disconnect from ticket WebSocket."""
        # Leave ticket group
        await self.channel_layer.group_discard(
            self.ticket_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket."""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'comment':
                await self.handle_comment(text_data_json)
            elif message_type == 'status_update':
                await self.handle_status_update(text_data_json)
            elif message_type == 'assignment':
                await self.handle_assignment(text_data_json)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def handle_comment(self, data):
        """Handle new comment."""
        comment_data = data.get('comment', {})
        
        # Save comment to database
        comment = await self.save_comment(comment_data)
        
        # Send comment to group
        await self.channel_layer.group_send(
            self.ticket_group_name,
            {
                'type': 'comment_added',
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'author': comment.author.username,
                    'created_at': comment.created_at.isoformat(),
                    'is_internal': comment.is_internal
                }
            }
        )
    
    async def handle_status_update(self, data):
        """Handle status update."""
        status = data.get('status')
        
        # Update ticket status
        await self.update_ticket_status(status)
        
        # Send status update to group
        await self.channel_layer.group_send(
            self.ticket_group_name,
            {
                'type': 'status_updated',
                'status': status
            }
        )
    
    async def handle_assignment(self, data):
        """Handle ticket assignment."""
        user_id = data.get('user_id')
        
        # Update ticket assignment
        await self.update_ticket_assignment(user_id)
        
        # Send assignment update to group
        await self.channel_layer.group_send(
            self.ticket_group_name,
            {
                'type': 'assignment_updated',
                'assigned_to': user_id
            }
        )
    
    async def comment_added(self, event):
        """Send comment to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'comment_added',
            'comment': event['comment']
        }))
    
    async def status_updated(self, event):
        """Send status update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'status_updated',
            'status': event['status']
        }))
    
    async def assignment_updated(self, event):
        """Send assignment update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'assignment_updated',
            'assigned_to': event['assigned_to']
        }))
    
    @database_sync_to_async
    def save_comment(self, comment_data):
        """Save comment to database."""
        from app.models.ticket import Ticket, TicketComment
        
        ticket = Ticket.objects.get(ticket_id=self.ticket_id)
        comment = TicketComment.objects.create(
            ticket=ticket,
            author=self.scope['user'],
            content=comment_data.get('content', ''),
            is_internal=comment_data.get('is_internal', False)
        )
        return comment
    
    @database_sync_to_async
    def update_ticket_status(self, status):
        """Update ticket status."""
        from app.models.ticket import Ticket
        
        ticket = Ticket.objects.get(ticket_id=self.ticket_id)
        ticket.status = status
        ticket.save()
    
    @database_sync_to_async
    def update_ticket_assignment(self, user_id):
        """Update ticket assignment."""
        from app.models.ticket import Ticket
        
        ticket = Ticket.objects.get(ticket_id=self.ticket_id)
        if user_id:
            user = User.objects.get(id=user_id)
            ticket.assigned_to = user
        else:
            ticket.assigned_to = None
        ticket.save()


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for notifications."""
    
    async def connect(self):
        """Connect to notification WebSocket."""
        if self.scope['user'] == AnonymousUser():
            await self.close()
            return
        
        self.user_id = self.scope['user'].id
        self.notification_group_name = f'notifications_{self.user_id}'
        
        # Join notification group
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Disconnect from notification WebSocket."""
        # Leave notification group
        await self.channel_layer.group_discard(
            self.notification_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket."""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'mark_read':
                await self.handle_mark_read(text_data_json)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def handle_mark_read(self, data):
        """Handle mark notification as read."""
        notification_id = data.get('notification_id')
        
        # Mark notification as read
        await self.mark_notification_read(notification_id)
        
        # Send confirmation
        await self.send(text_data=json.dumps({
            'type': 'notification_marked_read',
            'notification_id': notification_id
        }))
    
    async def notification_created(self, event):
        """Send notification to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'notification_created',
            'notification': event['notification']
        }))
    
    async def notification_updated(self, event):
        """Send notification update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'notification_updated',
            'notification': event['notification']
        }))
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read."""
        from app.models.notification import Notification
        
        try:
            notification = Notification.objects.get(id=notification_id, user_id=self.user_id)
            notification.is_read = True
            notification.save()
        except Notification.DoesNotExist:
            pass


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for chat support."""
    
    async def connect(self):
        """Connect to chat WebSocket."""
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Disconnect from chat WebSocket."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket."""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(text_data_json)
            elif message_type == 'typing':
                await self.handle_typing(text_data_json)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def handle_chat_message(self, data):
        """Handle chat message."""
        message_data = data.get('message', {})
        
        # Save message to database
        message = await self.save_chat_message(message_data)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender': message.sender.username,
                    'timestamp': message.timestamp.isoformat(),
                    'message_type': message.message_type
                }
            }
        )
    
    async def handle_typing(self, data):
        """Handle typing indicator."""
        is_typing = data.get('is_typing', False)
        user = self.scope['user']
        
        # Send typing indicator to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing',
                'user': user.username,
                'is_typing': is_typing
            }
        )
    
    async def chat_message(self, event):
        """Send chat message to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))
    
    async def typing(self, event):
        """Send typing indicator to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user': event['user'],
            'is_typing': event['is_typing']
        }))
    
    @database_sync_to_async
    def save_chat_message(self, message_data):
        """Save chat message to database."""
        from app.models.chat import ChatMessage
        
        message = ChatMessage.objects.create(
            room_name=self.room_name,
            sender=self.scope['user'],
            content=message_data.get('content', ''),
            message_type=message_data.get('message_type', 'text')
        )
        return message
