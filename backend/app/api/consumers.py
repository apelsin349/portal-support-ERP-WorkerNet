"""
WebSocket-консюмеры для портала WorkerNet.
Обрабатывают уведомления в реальном времени, обновления тикетов и чат.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

User = get_user_model()


class TicketConsumer(AsyncWebsocketConsumer):
    """Консюмер WebSocket для обновлений по тикетам."""
    
    async def connect(self):
        """Подключение к каналу обновлений конкретного тикета."""
        self.ticket_id = self.scope['url_route']['kwargs']['ticket_id']
        self.ticket_group_name = f'ticket_{self.ticket_id}'
        
        # Подписка на группу тикета
        await self.channel_layer.group_add(
            self.ticket_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Отключение от канала обновлений тикета."""
        # Отписка от группы тикета
        await self.channel_layer.group_discard(
            self.ticket_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Приём сообщения от клиента WebSocket."""
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
        """Обработка добавления нового комментария."""
        comment_data = data.get('comment', {})
        
        # Сохранить комментарий в БД
        comment = await self.save_comment(comment_data)
        
        # Отправить комментарий всем подписчикам группы тикета
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
        """Обработка изменения статуса тикета."""
        status = data.get('status')
        
        # Обновить статус тикета
        await self.update_ticket_status(status)
        
        # Разослать обновление статуса подписчикам
        await self.channel_layer.group_send(
            self.ticket_group_name,
            {
                'type': 'status_updated',
                'status': status
            }
        )
    
    async def handle_assignment(self, data):
        """Обработка назначения ответственного по тикету."""
        user_id = data.get('user_id')
        
        # Обновить назначение
        await self.update_ticket_assignment(user_id)
        
        # Разослать обновление назначения подписчикам
        await self.channel_layer.group_send(
            self.ticket_group_name,
            {
                'type': 'assignment_updated',
                'assigned_to': user_id
            }
        )
    
    async def comment_added(self, event):
        """Отправить событие о новом комментарии клиенту."""
        await self.send(text_data=json.dumps({
            'type': 'comment_added',
            'comment': event['comment']
        }))
    
    async def status_updated(self, event):
        """Отправить событие об обновлении статуса клиенту."""
        await self.send(text_data=json.dumps({
            'type': 'status_updated',
            'status': event['status']
        }))
    
    async def assignment_updated(self, event):
        """Отправить событие об изменении назначения клиенту."""
        await self.send(text_data=json.dumps({
            'type': 'assignment_updated',
            'assigned_to': event['assigned_to']
        }))
    
    @database_sync_to_async
    def save_comment(self, comment_data):
        """Сохранить комментарий в базе данных."""
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
        """Обновить статус тикета."""
        from app.models.ticket import Ticket
        
        ticket = Ticket.objects.get(ticket_id=self.ticket_id)
        ticket.status = status
        ticket.save()
    
    @database_sync_to_async
    def update_ticket_assignment(self, user_id):
        """Обновить назначение ответственного по тикету."""
        from app.models.ticket import Ticket
        
        ticket = Ticket.objects.get(ticket_id=self.ticket_id)
        if user_id:
            user = User.objects.get(id=user_id)
            ticket.assigned_to = user
        else:
            ticket.assigned_to = None
        ticket.save()


class NotificationConsumer(AsyncWebsocketConsumer):
    """Консюмер WebSocket для пользовательских уведомлений."""
    
    async def connect(self):
        """Подключение к личному каналу уведомлений пользователя."""
        if self.scope['user'] == AnonymousUser():
            await self.close()
            return
        
        self.user_id = self.scope['user'].id
        self.notification_group_name = f'notifications_{self.user_id}'
        
        # Подписка на группу уведомлений пользователя
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Отключение от канала уведомлений."""
        # Отписка от группы уведомлений
        await self.channel_layer.group_discard(
            self.notification_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Приём сообщения от клиента WebSocket."""
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
        """Отметить уведомление как прочитанное."""
        notification_id = data.get('notification_id')
        
        # Mark notification as read
        await self.mark_notification_read(notification_id)
        
        # Send confirmation
        await self.send(text_data=json.dumps({
            'type': 'notification_marked_read',
            'notification_id': notification_id
        }))
    
    async def notification_created(self, event):
        """Отправить событие о создании уведомления клиенту."""
        await self.send(text_data=json.dumps({
            'type': 'notification_created',
            'notification': event['notification']
        }))
    
    async def notification_updated(self, event):
        """Отправить событие об обновлении уведомления клиенту."""
        await self.send(text_data=json.dumps({
            'type': 'notification_updated',
            'notification': event['notification']
        }))
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Пометить уведомление как прочитанное."""
        from app.models.notification import Notification
        
        try:
            notification = Notification.objects.get(id=notification_id, user_id=self.user_id)
            notification.is_read = True
            notification.save()
        except Notification.DoesNotExist:
            pass


class ChatConsumer(AsyncWebsocketConsumer):
    """Консюмер WebSocket для чата службы поддержки."""
    
    async def connect(self):
        """Подключение к комнате чата."""
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Подписка на группу комнаты чата
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Отключение от комнаты чата."""
        # Отписка от группы комнаты
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Приём сообщения от клиента WebSocket."""
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
        """Обработка отправки сообщения чата."""
        message_data = data.get('message', {})
        
        # Сохранить сообщение в БД
        message = await self.save_chat_message(message_data)
        
        # Разослать сообщение подписчикам комнаты
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
        """Обработка индикатора набора текста."""
        is_typing = data.get('is_typing', False)
        user = self.scope['user']
        
        # Отправить индикатор набора в группу комнаты
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing',
                'user': user.username,
                'is_typing': is_typing
            }
        )
    
    async def chat_message(self, event):
        """Отправить сообщение чата клиенту."""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))
    
    async def typing(self, event):
        """Отправить индикатор набора клиенту."""
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user': event['user'],
            'is_typing': event['is_typing']
        }))
    
    @database_sync_to_async
    def save_chat_message(self, message_data):
        """Сохранить сообщение чата в базе данных."""
        from app.models.chat import ChatMessage
        
        message = ChatMessage.objects.create(
            room_name=self.room_name,
            sender=self.scope['user'],
            content=message_data.get('content', ''),
            message_type=message_data.get('message_type', 'text')
        )
        return message
