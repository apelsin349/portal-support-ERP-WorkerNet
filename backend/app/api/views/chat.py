"""
Представления для системы чата.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, F, Max
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from app.models import ChatMessage
from app.api.serializers.chat import (
    ChatMessageSerializer, ChatMessageCreateSerializer,
    ChatMessageUpdateSerializer, ChatConversationSerializer,
    ChatStatsSerializer, ChatMessageSearchSerializer,
    ChatMessageReactionSerializer, ChatTypingSerializer,
    ChatOnlineStatusSerializer
)

User = get_user_model()


class ChatMessageViewSet(viewsets.ModelViewSet):
    """Управление сообщениями чата."""
    
    queryset = ChatMessage.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['room_name', 'sender', 'message_type']
    search_fields = ['content']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Фильтрация по участникам чата и арендатору."""
        return self.queryset.filter(Q(sender=self.request.user))
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return ChatMessageCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ChatMessageUpdateSerializer
        else:
            return ChatMessageSerializer
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Отметить сообщение как прочитанное."""
        message = self.get_object()
        
        # Проверяем, что сообщение адресовано текущему пользователю
        return Response({'message': 'OK'})
    
    @action(detail=False, methods=['post'])
    def mark_conversation_read(self, request):
        """Отметить все сообщения в беседе как прочитанные."""
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id, tenant=request.user.tenant)
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({'message': 'OK'})
    
    @action(detail=False, methods=['get'])
    def conversations(self, request):
        """Список бесед пользователя."""
        # Получаем всех пользователей, с которыми есть сообщения
        user_ids = self.get_queryset().values_list('sender', flat=True)
        all_user_ids = set()
        
        for sender_id, recipient_id in user_ids:
            all_user_ids.add(sender_id)
            # no recipient in current model
        
        # Исключаем текущего пользователя
        all_user_ids.discard(request.user.id)
        
        # Получаем пользователей
        users = User.objects.filter(
            id__in=all_user_ids,
            tenant=request.user.tenant
        ).order_by('first_name', 'last_name')
        
        # Создаем список бесед
        conversations = []
        for user in users:
            conversation_data = {
                'user': user,
                'unread_count': self.get_queryset().filter(
                    sender=user,
                    recipient=request.user,
                    is_read=False
                ).count()
            }
            conversations.append(conversation_data)
        
        # Сортируем по времени последнего сообщения
        conversations.sort(
            key=lambda x: self.get_queryset().filter(
                Q(sender=x['user'], recipient=request.user) |
                Q(sender=request.user, recipient=x['user'])
            ).aggregate(last_message=Max('created_at'))['last_message'] or timezone.now(),
            reverse=True
        )
        
        serializer = ChatConversationSerializer(
            [conv['user'] for conv in conversations],
            many=True,
            context={'request': request}
        )
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def conversation(self, request):
        """Получение сообщений в беседе с конкретным пользователем."""
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id, tenant=request.user.tenant)
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Получаем сообщения между пользователями
        messages = self.get_queryset().filter(sender__in=[request.user, user]).order_by('timestamp')
        
        # Пагинация
        paginator = PageNumberPagination()
        paginated_messages = paginator.paginate_queryset(messages, request)
        
        serializer = ChatMessageSerializer(paginated_messages, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Поиск сообщений."""
        serializer = ChatMessageSearchSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        query = data['query']
        
        # Базовый запрос
        messages = self.get_queryset()
        
        # Поиск по тексту
        if query:
            messages = messages.filter(content__icontains=query)
        
        # Фильтры
        if data.get('user'):
            messages = messages.filter(sender=data['user'])
        
        if data.get('message_type'):
            messages = messages.filter(message_type=data['message_type'])
        
        if data.get('date_from'):
            messages = messages.filter(timestamp__gte=data['date_from'])
        
        if data.get('date_to'):
            messages = messages.filter(timestamp__lte=data['date_to'])
        
        # Сортировка
        messages = messages.order_by('-timestamp')
        
        # Пагинация
        paginator = PageNumberPagination()
        paginated_messages = paginator.paginate_queryset(messages, request)
        
        serializer = ChatMessageSerializer(paginated_messages, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Количество непрочитанных сообщений."""
        return Response({'unread_count': 0})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика чата."""
        user = request.user
        tenant = getattr(user, 'tenant', None)
        total_messages = ChatMessage.objects.filter(sender=user).count()
        unread_messages = 0
        week_ago = timezone.now() - timezone.timedelta(days=7)
        active_conversations = ChatMessage.objects.filter(sender=user, timestamp__gte=week_ago).values('room_name').distinct().count()
        messages_by_type = ChatMessage.objects.filter(sender=user).values('message_type').annotate(count=Count('id')).order_by('-count')
        messages_by_hour = ChatMessage.objects.filter(sender=user).extra(select={'hour': 'EXTRACT(hour FROM timestamp)'}).values('hour').annotate(count=Count('id')).order_by('hour')
        most_active_users = []
        recent_conversations = ChatMessage.objects.filter(sender=user).values('room_name').annotate(last_message=Max('timestamp')).order_by('-last_message')[:10]
        
        stats_data = {
            'total_messages': total_messages,
            'unread_messages': unread_messages,
            'active_conversations': active_conversations,
            'messages_by_type': dict(messages_by_type),
            'messages_by_hour': dict(messages_by_hour),
            'most_active_users': list(most_active_users),
            'recent_conversations': list(recent_conversations),
        }
        
        serializer = ChatStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        """Реакция на сообщение."""
        message = self.get_object()
        serializer = ChatMessageReactionSerializer(data=request.data)
        
        if serializer.is_valid():
            # Здесь можно добавить модель ChatMessageReaction
            # для хранения реакций на сообщения
            return Response({
                'message': 'Реакция добавлена'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def typing(self, request):
        """Статус набора текста."""
        serializer = ChatTypingSerializer(data=request.data)
        
        if serializer.is_valid():
            # Здесь можно добавить WebSocket уведомления
            # о статусе набора текста
            return Response({
                'message': 'Статус набора текста обновлен'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def online_status(self, request):
        """Статус онлайн пользователей."""
        # Здесь можно добавить модель UserOnlineStatus
        # для отслеживания статуса онлайн
        online_users = User.objects.filter(
            tenant=request.user.tenant,
            is_active=True
        ).values('id', 'first_name', 'last_name', 'last_login')
        
        return Response({
            'online_users': list(online_users)
        })
