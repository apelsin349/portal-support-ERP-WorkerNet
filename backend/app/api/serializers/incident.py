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
            'update_type', 'title', 'description', 'is_internal',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class IncidentUpdateCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания обновлений инцидентов."""
    
    class Meta:
        model = IncidentUpdate
        fields = ['update_type', 'title', 'description', 'is_internal']
    
    def create(self, validated_data):
        """Создание обновления инцидента."""
        validated_data['author'] = self.context['request'].user
        validated_data['incident'] = self.context['incident']
        return super().create(validated_data)


class IncidentTimelineSerializer(serializers.ModelSerializer):
    """Сериализатор для временной шкалы инцидентов."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = IncidentTimeline
        fields = [
            'id', 'incident', 'user', 'user_name', 'action', 'description',
            'timestamp', 'metadata'
        ]
        read_only_fields = ['id', 'timestamp']


class IncidentSLASerializer(serializers.ModelSerializer):
    """Сериализатор для SLA инцидентов."""
    
    sla_name = serializers.CharField(source='sla.name', read_only=True)
    
    class Meta:
        model = IncidentSLA
        fields = [
            'id', 'incident', 'sla', 'sla_name', 'assigned_at',
            'response_deadline', 'resolution_deadline',
            'response_time_actual', 'resolution_time_actual',
            'is_response_met', 'is_resolution_met'
        ]
        read_only_fields = [
            'id', 'assigned_at', 'response_deadline', 'resolution_deadline',
            'response_time_actual', 'resolution_time_actual',
            'is_response_met', 'is_resolution_met'
        ]


class IncidentEscalationSerializer(serializers.ModelSerializer):
    """Сериализатор для эскалации инцидентов."""
    
    escalated_by_name = serializers.CharField(source='escalated_by.get_full_name', read_only=True)
    escalated_to_name = serializers.CharField(source='escalated_to.get_full_name', read_only=True)
    
    class Meta:
        model = IncidentEscalation
        fields = [
            'id', 'incident', 'escalated_by', 'escalated_by_name',
            'escalated_to', 'escalated_to_name', 'reason', 'priority',
            'escalated_at', 'resolved_at', 'status'
        ]
        read_only_fields = ['id', 'escalated_at', 'resolved_at']


class IncidentEscalationCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания эскалации инцидентов."""
    
    class Meta:
        model = IncidentEscalation
        fields = ['escalated_to', 'reason', 'priority']
    
    def create(self, validated_data):
        """Создание эскалации инцидента."""
        validated_data['escalated_by'] = self.context['request'].user
        validated_data['incident'] = self.context['incident']
        return super().create(validated_data)


class IncidentListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка инцидентов."""
    
    reporter_name = serializers.CharField(source='reporter.get_full_name', read_only=True)
    assignee_name = serializers.CharField(source='assignee.get_full_name', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Incident
        fields = [
            'id', 'title', 'description', 'severity', 'severity_display',
            'status', 'status_display', 'priority', 'priority_display',
            'reporter', 'reporter_name', 'assignee', 'assignee_name',
            'reported_at', 'resolved_at', 'created_at', 'updated_at'
        ]


class IncidentDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра инцидентов."""
    
    reporter_name = serializers.CharField(source='reporter.get_full_name', read_only=True)
    reporter_avatar = serializers.ImageField(source='reporter.avatar', read_only=True)
    assignee_name = serializers.CharField(source='assignee.get_full_name', read_only=True)
    assignee_avatar = serializers.ImageField(source='assignee.avatar', read_only=True)
    
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    updates = IncidentUpdateSerializer(many=True, read_only=True)
    attachments = IncidentAttachmentSerializer(many=True, read_only=True)
    timeline = IncidentTimelineSerializer(many=True, read_only=True)
    escalations = IncidentEscalationSerializer(many=True, read_only=True)
    sla_info = IncidentSLASerializer(read_only=True)
    
    class Meta:
        model = Incident
        fields = [
            'id', 'title', 'description', 'severity', 'severity_display',
            'status', 'status_display', 'priority', 'priority_display',
            'reporter', 'reporter_name', 'reporter_avatar',
            'assignee', 'assignee_name', 'assignee_avatar',
            'reported_at', 'resolved_at', 'created_at', 'updated_at',
            'updates', 'attachments', 'timeline', 'escalations', 'sla_info'
        ]


class IncidentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания инцидентов."""
    
    class Meta:
        model = Incident
        fields = [
            'title', 'description', 'severity', 'priority', 'assignee'
        ]
    
    def create(self, validated_data):
        """Создание инцидента."""
        validated_data['reporter'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class IncidentUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления инцидентов."""
    
    class Meta:
        model = Incident
        fields = [
            'title', 'description', 'severity', 'status', 'priority', 'assignee'
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
    incidents_by_priority = serializers.DictField()
    
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
    priority = serializers.ChoiceField(
        choices=Incident.PRIORITY_CHOICES,
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
