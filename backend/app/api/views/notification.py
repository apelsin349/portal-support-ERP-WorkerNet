"""
Представления для системы уведомлений.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, F
from django.utils import timezone
from django.shortcuts import get_object_or_404

from app.models import Notification
from app.api.serializers.notification import (
    NotificationSerializer, NotificationCreateSerializer,
    NotificationUpdateSerializer, NotificationStatsSerializer,
    NotificationBulkUpdateSerializer, NotificationPreferencesSerializer
)


class NotificationViewSet(viewsets.ModelViewSet):
    """Управление уведомлениями."""
    
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'is_read', 'is_sent', 'priority']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'priority', 'is_read']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фильтрация по получателю и арендатору."""
        return self.queryset.filter(
            recipient=self.request.user,
            tenant=self.request.user.tenant
        )
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return NotificationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return NotificationUpdateSerializer
        else:
            return NotificationSerializer
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Отметить уведомление как прочитанное."""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=['is_read', 'read_at'])
        
        return Response({'message': 'Уведомление отмечено как прочитанное'})
    
    @action(detail=True, methods=['post'])
    def mark_unread(self, request, pk=None):
        """Отметить уведомление как непрочитанное."""
        notification = self.get_object()
        notification.is_read = False
        notification.read_at = None
        notification.save(update_fields=['is_read', 'read_at'])
        
        return Response({'message': 'Уведомление отмечено как непрочитанное'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Отметить все уведомления как прочитанные."""
        updated_count = self.get_queryset().filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'message': f'Отмечено как прочитанные: {updated_count} уведомлений'
        })
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Массовое обновление уведомлений."""
        serializer = NotificationBulkUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        notification_ids = data['notification_ids']
        action = data['action']
        
        # Фильтруем только уведомления пользователя
        notifications = self.get_queryset().filter(id__in=notification_ids)
        
        if action == 'mark_read':
            updated_count = notifications.filter(is_read=False).update(
                is_read=True,
                read_at=timezone.now()
            )
            message = f'Отмечено как прочитанные: {updated_count} уведомлений'
        
        elif action == 'mark_unread':
            updated_count = notifications.filter(is_read=True).update(
                is_read=False,
                read_at=None
            )
            message = f'Отмечено как непрочитанные: {updated_count} уведомлений'
        
        elif action == 'delete':
            deleted_count = notifications.count()
            notifications.delete()
            message = f'Удалено: {deleted_count} уведомлений'
        
        elif action == 'mark_sent':
            updated_count = notifications.filter(is_sent=False).update(
                is_sent=True,
                sent_at=timezone.now()
            )
            message = f'Отмечено как отправленные: {updated_count} уведомлений'
        
        else:
            return Response(
                {'error': 'Неизвестное действие'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({'message': message})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Количество непрочитанных уведомлений."""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика уведомлений."""
        user = request.user
        tenant = user.tenant
        
        # Общая статистика
        total_notifications = Notification.objects.filter(
            recipient=user, tenant=tenant
        ).count()
        
        unread_notifications = Notification.objects.filter(
            recipient=user, tenant=tenant, is_read=False
        ).count()
        
        sent_notifications = Notification.objects.filter(
            recipient=user, tenant=tenant, is_sent=True
        ).count()
        
        failed_notifications = Notification.objects.filter(
            recipient=user, tenant=tenant, is_sent=False
        ).count()
        
        # Статистика по типам
        notifications_by_type = Notification.objects.filter(
            recipient=user, tenant=tenant
        ).values('type').annotate(count=Count('id')).order_by('-count')
        
        # Статистика по приоритетам
        notifications_by_priority = Notification.objects.filter(
            recipient=user, tenant=tenant
        ).values('priority').annotate(count=Count('id')).order_by('-count')
        
        # Недавние уведомления
        recent_notifications = Notification.objects.filter(
            recipient=user, tenant=tenant
        ).order_by('-created_at')[:10]
        
        # Топ отправителей
        top_senders = Notification.objects.filter(
            recipient=user, tenant=tenant
        ).values('sender__first_name', 'sender__last_name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        stats_data = {
            'total_notifications': total_notifications,
            'unread_notifications': unread_notifications,
            'sent_notifications': sent_notifications,
            'failed_notifications': failed_notifications,
            'notifications_by_type': dict(notifications_by_type),
            'notifications_by_priority': dict(notifications_by_priority),
            'recent_notifications': NotificationSerializer(recent_notifications, many=True).data,
            'top_senders': list(top_senders),
        }
        
        serializer = NotificationStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get', 'post'])
    def preferences(self, request):
        """Настройки уведомлений пользователя."""
        if request.method == 'GET':
            # Получаем текущие настройки
            # Здесь можно добавить модель UserNotificationPreferences
            preferences = {
                'email_notifications': True,
                'push_notifications': True,
                'sms_notifications': False,
                'notification_types': {
                    'ticket_created': True,
                    'ticket_updated': True,
                    'ticket_assigned': True,
                    'ticket_resolved': True,
                    'knowledge_article_created': False,
                    'system_announcement': True,
                },
                'quiet_hours_start': None,
                'quiet_hours_end': None,
            }
            
            serializer = NotificationPreferencesSerializer(preferences)
            return Response(serializer.data)
        
        else:  # POST
            # Обновляем настройки
            serializer = NotificationPreferencesSerializer(data=request.data)
            
            if serializer.is_valid():
                # Здесь можно сохранить настройки в модель UserNotificationPreferences
                return Response({
                    'message': 'Настройки уведомлений обновлены'
                })
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Уведомления по типу."""
        notification_type = request.query_params.get('type')
        
        if not notification_type:
            return Response(
                {'error': 'Параметр type обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notifications = self.get_queryset().filter(type=notification_type)
        
        # Пагинация
        paginator = PageNumberPagination()
        paginated_notifications = paginator.paginate_queryset(notifications, request)
        
        serializer = NotificationSerializer(paginated_notifications, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def urgent(self, request):
        """Срочные уведомления."""
        notifications = self.get_queryset().filter(
            priority='urgent',
            is_read=False
        ).order_by('-created_at')
        
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
