"""
Сериализаторы для системы тикетов.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from app.models import (
    Ticket, TicketComment, TicketAttachment, Tag, SLA, TicketSLA
)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class TicketAttachmentSerializer(serializers.ModelSerializer):
    """Сериализатор для вложений тикета."""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = TicketAttachment
        fields = [
            'id', 'file', 'filename', 'file_size', 'mime_type',
            'uploaded_by', 'uploaded_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'created_at']


class TicketCommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев тикета."""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_avatar = serializers.ImageField(source='author.avatar', read_only=True)
    
    class Meta:
        model = TicketComment
        fields = [
            'id', 'content', 'is_internal', 'author', 'author_name',
            'author_avatar', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']


class TicketCommentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания комментария."""
    
    class Meta:
        model = TicketComment
        fields = ['content', 'is_internal']
    
    def create(self, validated_data):
        """Создание комментария."""
        validated_data['author'] = self.context['request'].user
        validated_data['ticket'] = self.context['ticket']
        return super().create(validated_data)


class SLASerializer(serializers.ModelSerializer):
    """Сериализатор для SLA."""
    
    class Meta:
        model = SLA
        fields = [
            'id', 'name', 'description', 'response_time', 'resolution_time',
            'priority', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TicketSLASerializer(serializers.ModelSerializer):
    """Сериализатор для SLA тикета."""
    
    sla_name = serializers.CharField(source='sla.name', read_only=True)
    
    class Meta:
        model = TicketSLA
        fields = [
            'id', 'sla', 'sla_name', 'first_response_at', 'resolution_at',
            'is_breached', 'breach_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TicketListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка тикетов."""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    attachments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_id', 'title', 'priority', 'status', 'category',
            'created_by', 'created_by_name', 'assigned_to', 'assigned_to_name',
            'due_date', 'resolved_at', 'created_at', 'updated_at',
            'tags', 'comments_count', 'attachments_count'
        ]
    
    def get_comments_count(self, obj):
        """Количество комментариев."""
        return obj.comments.count()
    
    def get_attachments_count(self, obj):
        """Количество вложений."""
        return obj.attachments.count()


class TicketDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра тикета."""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = TicketCommentSerializer(many=True, read_only=True)
    attachments = TicketAttachmentSerializer(many=True, read_only=True)
    sla_tracking = TicketSLASerializer(read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_id', 'title', 'description', 'priority', 'status', 'category',
            'created_by', 'created_by_name', 'assigned_to', 'assigned_to_name',
            'sla_hours', 'due_date', 'resolved_at', 'created_at', 'updated_at',
            'custom_fields', 'tags', 'comments', 'attachments', 'sla_tracking'
        ]


class TicketCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания тикета."""
    
    class Meta:
        model = Ticket
        fields = [
            'title', 'description', 'priority', 'category',
            'assigned_to', 'sla_hours', 'custom_fields', 'tags'
        ]
    
    def create(self, validated_data):
        """Создание тикета."""
        validated_data['created_by'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class TicketUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления тикета."""
    
    class Meta:
        model = Ticket
        fields = [
            'title', 'description', 'priority', 'status', 'category',
            'assigned_to', 'sla_hours', 'due_date', 'custom_fields', 'tags'
        ]
    
    def update(self, instance, validated_data):
        """Обновление тикета."""
        # Обновляем время решения при изменении статуса
        if 'status' in validated_data:
            if validated_data['status'] in ['resolved', 'closed'] and not instance.resolved_at:
                from django.utils import timezone
                validated_data['resolved_at'] = timezone.now()
            elif validated_data['status'] not in ['resolved', 'closed']:
                validated_data['resolved_at'] = None
        
        return super().update(instance, validated_data)


class TicketAssignSerializer(serializers.Serializer):
    """Сериализатор для назначения тикета."""
    
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True
    )
    
    def validate_assigned_to(self, value):
        """Валидация назначения."""
        if value.tenant != self.context['request'].user.tenant:
            raise serializers.ValidationError("Пользователь не принадлежит к тому же тенанту")
        return value


class TicketStatusUpdateSerializer(serializers.Serializer):
    """Сериализатор для обновления статуса тикета."""
    
    status = serializers.ChoiceField(choices=Ticket.STATUS_CHOICES)
    comment = serializers.CharField(required=False, allow_blank=True)
    
    def validate_status(self, value):
        """Валидация статуса."""
        ticket = self.context['ticket']
        
        # Проверяем, можно ли перевести тикет в указанный статус
        if ticket.status == 'closed' and value != 'closed':
            raise serializers.ValidationError("Закрытый тикет нельзя изменить")
        
        return value


class TicketPriorityUpdateSerializer(serializers.Serializer):
    """Сериализатор для обновления приоритета тикета."""
    
    priority = serializers.ChoiceField(choices=Ticket.PRIORITY_CHOICES)
    comment = serializers.CharField(required=False, allow_blank=True)


class TicketSearchSerializer(serializers.Serializer):
    """Сериализатор для поиска тикетов."""
    
    query = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=Ticket.STATUS_CHOICES, required=False)
    priority = serializers.ChoiceField(choices=Ticket.PRIORITY_CHOICES, required=False)
    category = serializers.ChoiceField(choices=Ticket.CATEGORY_CHOICES, required=False)
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    tags = serializers.CharField(required=False, allow_blank=True)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    sla_breached = serializers.BooleanField(required=False)
    
    def validate(self, attrs):
        """Валидация параметров поиска."""
        if attrs.get('date_from') and attrs.get('date_to'):
            if attrs['date_from'] > attrs['date_to']:
                raise serializers.ValidationError("Дата начала не может быть больше даты окончания")
        return attrs


class TicketStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики тикетов."""
    
    total = serializers.IntegerField()
    open = serializers.IntegerField()
    in_progress = serializers.IntegerField()
    pending = serializers.IntegerField()
    resolved = serializers.IntegerField()
    closed = serializers.IntegerField()
    cancelled = serializers.IntegerField()
    
    # По приоритетам
    critical = serializers.IntegerField()
    urgent = serializers.IntegerField()
    high = serializers.IntegerField()
    medium = serializers.IntegerField()
    low = serializers.IntegerField()
    
    # SLA статистика
    sla_breached = serializers.IntegerField()
    sla_at_risk = serializers.IntegerField()
    sla_ok = serializers.IntegerField()
    
    # Временные метрики
    avg_response_time = serializers.DurationField()
    avg_resolution_time = serializers.DurationField()
    first_response_rate = serializers.FloatField()
    resolution_rate = serializers.FloatField()
