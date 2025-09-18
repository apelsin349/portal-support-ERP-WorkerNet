"""
Сериализаторы для управления инцидентами.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from app.models import (
    Incident, IncidentUpdate, IncidentAttachment, IncidentTimeline,
    IncidentEscalation, IncidentSLA
)

User = get_user_model()


class IncidentAttachmentSerializer(serializers.ModelSerializer):
    """Сериализатор для вложений инцидентов."""
    
    class Meta:
        model = IncidentAttachment
        fields = [
            'id', 'file', 'filename', 'file_size', 'mime_type', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class IncidentUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновлений инцидентов."""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_avatar = serializers.ImageField(source='author.avatar', read_only=True)
    
    class Meta:
        model = IncidentUpdate
        fields = [
            'id', 'incident', 'author', 'author_name', 'author_avatar',
            'update_type', 'title', 'content', 'is_public',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class IncidentUpdateCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания обновлений инцидентов."""
    
    class Meta:
        model = IncidentUpdate
        fields = ['update_type', 'title', 'content', 'is_public']
    
    def create(self, validated_data):
        """Создание обновления инцидента."""
        validated_data['author'] = self.context['request'].user
        validated_data['incident'] = self.context['incident']
        return super().create(validated_data)


class IncidentTimelineSerializer(serializers.ModelSerializer):
    """Сериализатор для временной шкалы инцидентов."""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = IncidentTimeline
        fields = [
            'id', 'incident', 'event_type', 'description', 'author', 'author_name',
            'metadata', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class IncidentSLASerializer(serializers.ModelSerializer):
    """Сериализатор для SLA правил инцидентов."""
    
    class Meta:
        model = IncidentSLA
        fields = [
            'id', 'name', 'description', 'severity',
            'response_time_minutes', 'resolution_time_minutes',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class IncidentEscalationSerializer(serializers.ModelSerializer):
    """Сериализатор для эскалации инцидентов."""
    
    escalated_by_name = serializers.CharField(source='escalated_by.get_full_name', read_only=True)
    escalated_to_name = serializers.CharField(source='escalated_to.get_full_name', read_only=True)
    
    class Meta:
        model = IncidentEscalation
        fields = [
            'id', 'incident', 'level', 'reason',
            'escalated_by', 'escalated_by_name',
            'escalated_to', 'escalated_to_name',
            'is_acknowledged', 'acknowledged_at', 'escalated_at'
        ]
        read_only_fields = ['id', 'escalated_at', 'acknowledged_at']


class IncidentEscalationCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания эскалации инцидентов."""
    
    class Meta:
        model = IncidentEscalation
        fields = ['level', 'escalated_to', 'reason']
    
    def create(self, validated_data):
        """Создание эскалации инцидента."""
        validated_data['escalated_by'] = self.context['request'].user
        validated_data['incident'] = self.context['incident']
        return super().create(validated_data)


class IncidentListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка инцидентов."""
    
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Incident
        fields = [
            'id', 'incident_id', 'title', 'description', 'severity', 'severity_display',
            'status', 'status_display', 'category', 'category_display',
            'reported_by', 'reported_by_name', 'assigned_to', 'assigned_to_name',
            'detected_at', 'resolved_at', 'created_at', 'updated_at'
        ]


class IncidentDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра инцидентов."""
    
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    reported_by_avatar = serializers.ImageField(source='reported_by.avatar', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    assigned_to_avatar = serializers.ImageField(source='assigned_to.avatar', read_only=True)
    
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    updates = IncidentUpdateSerializer(many=True, read_only=True)
    attachments = IncidentAttachmentSerializer(many=True, read_only=True)
    timeline = IncidentTimelineSerializer(many=True, read_only=True)
    escalations = IncidentEscalationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Incident
        fields = [
            'id', 'incident_id', 'title', 'description', 'severity', 'severity_display',
            'status', 'status_display', 'category', 'category_display',
            'reported_by', 'reported_by_name', 'reported_by_avatar',
            'assigned_to', 'assigned_to_name', 'assigned_to_avatar',
            'detected_at', 'resolved_at', 'created_at', 'updated_at',
            'updates', 'attachments', 'timeline', 'escalations'
        ]


class IncidentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания инцидентов."""
    
    class Meta:
        model = Incident
        fields = [
            'title', 'description', 'severity', 'category', 'assigned_to', 'detected_at'
        ]
    
    def create(self, validated_data):
        """Создание инцидента."""
        validated_data['reported_by'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class IncidentUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления инцидентов."""
    
    class Meta:
        model = Incident
        fields = [
            'title', 'description', 'severity', 'status', 'category', 'assigned_to'
        ]
    
    def update(self, instance, validated_data):
        """Обновление инцидента."""
        # Обновляем время решения при изменении статуса
        if 'status' in validated_data:
            if validated_data['status'] == 'resolved' and not instance.resolved_at:
                from django.utils import timezone
                validated_data['resolved_at'] = timezone.now()
            elif validated_data['status'] != 'resolved':
                validated_data['resolved_at'] = None
        
        return super().update(instance, validated_data)


class IncidentStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики инцидентов."""
    
    total_incidents = serializers.IntegerField()
    open_incidents = serializers.IntegerField()
    resolved_incidents = serializers.IntegerField()
    closed_incidents = serializers.IntegerField()
    
    incidents_by_severity = serializers.DictField()
    incidents_by_status = serializers.DictField()
    incidents_by_category = serializers.DictField()
    
    average_resolution_time = serializers.FloatField()
    resolution_time_by_severity = serializers.DictField()
    
    top_assignees = serializers.ListField()
    recent_incidents = serializers.ListField()


class IncidentReportSerializer(serializers.Serializer):
    """Сериализатор для отчета по инцидентам."""
    
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    
    total_incidents = serializers.IntegerField()
    incidents_by_severity = serializers.DictField()
    incidents_by_status = serializers.DictField()
    
    resolution_times = serializers.DictField()
    escalation_count = serializers.IntegerField()
    
    top_incidents = serializers.ListField()
    recommendations = serializers.ListField()


class IncidentSearchSerializer(serializers.Serializer):
    """Сериализатор для поиска инцидентов."""
    
    query = serializers.CharField(max_length=255)
    severity = serializers.ChoiceField(
        choices=Incident.SEVERITY_CHOICES,
        required=False
    )
    status = serializers.ChoiceField(
        choices=Incident.STATUS_CHOICES,
        required=False
    )
    category = serializers.ChoiceField(
        choices=Incident.CATEGORY_CHOICES,
        required=False
    )
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )
    reporter = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    
    def validate(self, attrs):
        """Валидация параметров поиска."""
        if attrs.get('date_from') and attrs.get('date_to'):
            if attrs['date_from'] > attrs['date_to']:
                raise serializers.ValidationError(
                    "Дата начала не может быть больше даты окончания"
                )
        return attrs
