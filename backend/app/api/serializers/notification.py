"""
Сериализаторы для системы уведомлений.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from app.models import Notification

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    """Сериализатор для уведомлений."""
    
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title', 'message', 'sender', 'sender_name',
            'recipient', 'recipient_name', 'is_read', 'is_sent',
            'priority', 'data', 'created_at', 'read_at', 'sent_at'
        ]
        read_only_fields = ['id', 'created_at', 'read_at', 'sent_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания уведомлений."""
    
    class Meta:
        model = Notification
        fields = [
            'type', 'title', 'message', 'recipient', 'priority', 'data'
        ]
    
    def create(self, validated_data):
        """Создание уведомления."""
        validated_data['sender'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления уведомлений."""
    
    class Meta:
        model = Notification
        fields = ['is_read', 'is_sent']
    
    def update(self, instance, validated_data):
        """Обновление уведомления."""
        if validated_data.get('is_read') and not instance.is_read:
            from django.utils import timezone
            validated_data['read_at'] = timezone.now()
        
        if validated_data.get('is_sent') and not instance.is_sent:
            from django.utils import timezone
            validated_data['sent_at'] = timezone.now()
        
        return super().update(instance, validated_data)


class NotificationStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики уведомлений."""
    
    total_notifications = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()
    sent_notifications = serializers.IntegerField()
    failed_notifications = serializers.IntegerField()
    
    notifications_by_type = serializers.DictField()
    notifications_by_priority = serializers.DictField()
    
    recent_notifications = serializers.ListField()
    top_senders = serializers.ListField()


class NotificationTemplateSerializer(serializers.Serializer):
    """Сериализатор для шаблонов уведомлений."""
    
    type = serializers.CharField()
    title_template = serializers.CharField()
    message_template = serializers.CharField()
    variables = serializers.ListField(child=serializers.CharField())
    is_active = serializers.BooleanField()


class NotificationBulkUpdateSerializer(serializers.Serializer):
    """Сериализатор для массового обновления уведомлений."""
    
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    action = serializers.ChoiceField(choices=[
        ('mark_read', 'Отметить как прочитанные'),
        ('mark_unread', 'Отметить как непрочитанные'),
        ('delete', 'Удалить'),
        ('mark_sent', 'Отметить как отправленные')
    ])
    
    def validate_notification_ids(self, value):
        """Валидация ID уведомлений."""
        if not value:
            raise serializers.ValidationError("Список ID не может быть пустым")
        return value


class NotificationPreferencesSerializer(serializers.Serializer):
    """Сериализатор для настроек уведомлений пользователя."""
    
    email_notifications = serializers.BooleanField()
    push_notifications = serializers.BooleanField()
    sms_notifications = serializers.BooleanField()
    
    notification_types = serializers.DictField(
        child=serializers.BooleanField()
    )
    
    quiet_hours_start = serializers.TimeField(required=False, allow_null=True)
    quiet_hours_end = serializers.TimeField(required=False, allow_null=True)
    
    def validate(self, attrs):
        """Валидация настроек уведомлений."""
        start = attrs.get('quiet_hours_start')
        end = attrs.get('quiet_hours_end')
        
        if start and end and start >= end:
            raise serializers.ValidationError(
                "Время начала тихого режима должно быть раньше времени окончания"
            )
        
        return attrs
