"""
Сериализаторы для системы мониторинга производительности.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from app.models import (
    PerformanceMetric, PerformanceAlert, PerformanceTrace,
    PerformanceDashboard, PerformanceReport, PerformanceThreshold
)

User = get_user_model()


class PerformanceMetricSerializer(serializers.ModelSerializer):
    """Сериализатор для метрик производительности."""
    
    class Meta:
        model = PerformanceMetric
        fields = [
            'id', 'name', 'value', 'unit', 'category', 'tags',
            'timestamp', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PerformanceMetricCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания метрик производительности."""
    
    class Meta:
        model = PerformanceMetric
        fields = ['name', 'value', 'unit', 'category', 'tags', 'metadata']
    
    def create(self, validated_data):
        """Создание метрики производительности."""
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class PerformanceAlertSerializer(serializers.ModelSerializer):
    """Сериализатор для алертов производительности."""
    
    class Meta:
        model = PerformanceAlert
        fields = [
            'id', 'metric', 'threshold', 'current_value', 'severity',
            'message', 'is_resolved', 'resolved_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'resolved_at']


class PerformanceAlertCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания алертов производительности."""
    
    class Meta:
        model = PerformanceAlert
        fields = ['metric', 'threshold', 'current_value', 'severity', 'message']
    
    def create(self, validated_data):
        """Создание алерта производительности."""
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class PerformanceTraceSerializer(serializers.ModelSerializer):
    """Сериализатор для трейсов производительности."""
    
    class Meta:
        model = PerformanceTrace
        fields = [
            'id', 'trace_id', 'operation', 'duration', 'status',
            'start_time', 'end_time', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PerformanceTraceCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания трейсов производительности."""
    
    class Meta:
        model = PerformanceTrace
        fields = ['trace_id', 'operation', 'duration', 'status', 'metadata']
    
    def create(self, validated_data):
        """Создание трейса производительности."""
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class PerformanceDashboardSerializer(serializers.ModelSerializer):
    """Сериализатор для дашбордов производительности."""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    widgets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PerformanceDashboard
        fields = [
            'id', 'name', 'description', 'layout', 'widgets',
            'author', 'author_name', 'is_public', 'widgets_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_widgets_count(self, obj):
        """Количество виджетов в дашборде."""
        return len(obj.widgets) if obj.widgets else 0


class PerformanceDashboardCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания дашбордов производительности."""
    
    class Meta:
        model = PerformanceDashboard
        fields = ['name', 'description', 'layout', 'widgets', 'is_public']
    
    def create(self, validated_data):
        """Создание дашборда производительности."""
        validated_data['author'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class PerformanceReportSerializer(serializers.ModelSerializer):
    """Сериализатор для отчетов производительности."""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = PerformanceReport
        fields = [
            'id', 'name', 'description', 'report_type', 'period_start',
            'period_end', 'data', 'author', 'author_name', 'is_public',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Создание отчета производительности."""
        validated_data['author'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class PerformanceThresholdSerializer(serializers.ModelSerializer):
    """Сериализатор для пороговых значений производительности."""
    
    class Meta:
        model = PerformanceThreshold
        fields = [
            'id', 'metric_name', 'threshold_value', 'operator',
            'severity', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Создание порогового значения."""
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class PerformanceStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики производительности."""
    
    total_metrics = serializers.IntegerField()
    active_alerts = serializers.IntegerField()
    resolved_alerts = serializers.IntegerField()
    
    metrics_by_category = serializers.DictField()
    alerts_by_severity = serializers.DictField()
    
    average_response_time = serializers.FloatField()
    uptime_percentage = serializers.FloatField()
    
    top_operations = serializers.ListField()
    recent_metrics = serializers.ListField()


class PerformanceReportDataSerializer(serializers.Serializer):
    """Сериализатор для данных отчета производительности."""
    
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    
    total_metrics = serializers.IntegerField()
    metrics_by_category = serializers.DictField()
    
    response_time_stats = serializers.DictField()
    error_rate = serializers.FloatField()
    
    top_operations = serializers.ListField()
    performance_trends = serializers.DictField()
    
    recommendations = serializers.ListField()


class PerformanceSearchSerializer(serializers.Serializer):
    """Сериализатор для поиска производительности."""
    
    query = serializers.CharField(max_length=255)
    category = serializers.CharField(required=False)
    metric_name = serializers.CharField(required=False)
    severity = serializers.CharField(required=False)
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


class PerformanceWidgetSerializer(serializers.Serializer):
    """Сериализатор для виджетов производительности."""
    
    widget_type = serializers.CharField()
    title = serializers.CharField()
    data = serializers.DictField()
    position = serializers.DictField()
    size = serializers.DictField()
    config = serializers.DictField()


class PerformanceDashboardWidgetSerializer(serializers.Serializer):
    """Сериализатор для виджетов дашборда производительности."""
    
    dashboard_id = serializers.IntegerField()
    widgets = serializers.ListField(child=PerformanceWidgetSerializer())
    
    def validate_dashboard_id(self, value):
        """Валидация ID дашборда."""
        try:
            PerformanceDashboard.objects.get(id=value)
        except PerformanceDashboard.DoesNotExist:
            raise serializers.ValidationError("Дашборд не найден")
        return value
