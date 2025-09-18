"""
Сериализаторы для системы SLA.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from app.models import SLA, TicketSLA

User = get_user_model()


class SLASerializer(serializers.ModelSerializer):
    """Сериализатор для SLA."""
    
    class Meta:
        model = SLA
        fields = [
            'id', 'name', 'description', 'priority', 'response_time_hours',
            'resolution_time_hours', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SLACreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания SLA."""
    
    class Meta:
        model = SLA
        fields = [
            'name', 'description', 'priority', 'response_time_hours',
            'resolution_time_hours', 'is_active'
        ]
    
    def create(self, validated_data):
        """Создание SLA."""
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class TicketSLASerializer(serializers.ModelSerializer):
    """Сериализатор для связи тикета и SLA."""
    
    sla_name = serializers.CharField(source='sla.name', read_only=True)
    ticket_title = serializers.CharField(source='ticket.title', read_only=True)
    
    class Meta:
        model = TicketSLA
        fields = [
            'id', 'ticket', 'ticket_title', 'sla', 'sla_name',
            'assigned_at', 'response_deadline', 'resolution_deadline',
            'response_time_actual', 'resolution_time_actual',
            'is_response_met', 'is_resolution_met', 'created_at'
        ]
        read_only_fields = [
            'id', 'assigned_at', 'response_deadline', 'resolution_deadline',
            'response_time_actual', 'resolution_time_actual',
            'is_response_met', 'is_resolution_met', 'created_at'
        ]


class TicketSLACreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания связи тикета и SLA."""
    
    class Meta:
        model = TicketSLA
        fields = ['ticket', 'sla']
    
    def create(self, validated_data):
        """Создание связи тикета и SLA."""
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class SLAStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики SLA."""
    
    total_sla = serializers.IntegerField()
    active_sla = serializers.IntegerField()
    
    response_time_met = serializers.IntegerField()
    response_time_missed = serializers.IntegerField()
    response_time_percentage = serializers.FloatField()
    
    resolution_time_met = serializers.IntegerField()
    resolution_time_missed = serializers.IntegerField()
    resolution_time_percentage = serializers.FloatField()
    
    average_response_time = serializers.FloatField()
    average_resolution_time = serializers.FloatField()
    
    sla_performance = serializers.ListField()


class SLAViolationSerializer(serializers.Serializer):
    """Сериализатор для нарушений SLA."""
    
    ticket_id = serializers.IntegerField()
    ticket_title = serializers.CharField()
    sla_name = serializers.CharField()
    violation_type = serializers.CharField()
    expected_time = serializers.DateTimeField()
    actual_time = serializers.DateTimeField()
    delay_hours = serializers.FloatField()
    severity = serializers.CharField()


class SLAReportSerializer(serializers.Serializer):
    """Сериализатор для отчета по SLA."""
    
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    
    total_tickets = serializers.IntegerField()
    tickets_with_sla = serializers.IntegerField()
    
    response_time_stats = serializers.DictField()
    resolution_time_stats = serializers.DictField()
    
    violations = serializers.ListField()
    top_violations = serializers.ListField()
    
    recommendations = serializers.ListField()
