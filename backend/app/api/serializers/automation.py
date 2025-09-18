"""
Сериализаторы для системы автоматизации.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from app.models import (
    AutomationRule, AutomationExecution, AutomationCondition,
    AutomationAction, AutomationTemplate, AutomationSchedule
)

User = get_user_model()


class AutomationConditionSerializer(serializers.ModelSerializer):
    """Сериализатор для условий автоматизации."""
    
    class Meta:
        model = AutomationCondition
        fields = [
            'id', 'rule', 'field', 'operator', 'value', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AutomationConditionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания условий автоматизации."""
    
    class Meta:
        model = AutomationCondition
        fields = ['field', 'operator', 'value', 'order']
    
    def create(self, validated_data):
        """Создание условия автоматизации."""
        validated_data['rule'] = self.context['rule']
        return super().create(validated_data)


class AutomationActionSerializer(serializers.ModelSerializer):
    """Сериализатор для действий автоматизации."""
    
    class Meta:
        model = AutomationAction
        fields = [
            'id', 'rule', 'action_type', 'parameters', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AutomationActionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания действий автоматизации."""
    
    class Meta:
        model = AutomationAction
        fields = ['action_type', 'parameters', 'order']
    
    def create(self, validated_data):
        """Создание действия автоматизации."""
        validated_data['rule'] = self.context['rule']
        return super().create(validated_data)


class AutomationRuleListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка правил автоматизации."""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    executions_count = serializers.SerializerMethodField()
    last_execution = serializers.SerializerMethodField()
    
    class Meta:
        model = AutomationRule
        fields = [
            'id', 'name', 'description', 'is_active', 'priority',
            'author', 'author_name', 'executions_count', 'last_execution',
            'created_at', 'updated_at'
        ]
    
    def get_executions_count(self, obj):
        """Количество выполнений правила."""
        return obj.executions.count()
    
    def get_last_execution(self, obj):
        """Последнее выполнение правила."""
        last_execution = obj.executions.order_by('-executed_at').first()
        if last_execution:
            return last_execution.executed_at
        return None


class AutomationRuleDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра правил автоматизации."""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_avatar = serializers.ImageField(source='author.avatar', read_only=True)
    
    conditions = AutomationConditionSerializer(many=True, read_only=True)
    actions = AutomationActionSerializer(many=True, read_only=True)
    executions = serializers.SerializerMethodField()
    
    executions_count = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = AutomationRule
        fields = [
            'id', 'name', 'description', 'is_active', 'priority',
            'trigger_event', 'conditions', 'actions', 'author',
            'author_name', 'author_avatar', 'executions', 'executions_count',
            'success_rate', 'created_at', 'updated_at'
        ]
    
    def get_executions(self, obj):
        """Выполнения правила."""
        executions = obj.executions.all().order_by('-executed_at')[:10]
        return AutomationExecutionSerializer(executions, many=True).data
    
    def get_executions_count(self, obj):
        """Количество выполнений правила."""
        return obj.executions.count()
    
    def get_success_rate(self, obj):
        """Процент успешных выполнений."""
        total_executions = obj.executions.count()
        if total_executions == 0:
            return 0
        
        successful_executions = obj.executions.filter(status='success').count()
        return (successful_executions / total_executions) * 100


class AutomationRuleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания правил автоматизации."""
    
    conditions = AutomationConditionCreateSerializer(many=True, write_only=True)
    actions = AutomationActionCreateSerializer(many=True, write_only=True)
    
    class Meta:
        model = AutomationRule
        fields = [
            'name', 'description', 'is_active', 'priority',
            'trigger_event', 'conditions', 'actions'
        ]
    
    def create(self, validated_data):
        """Создание правила автоматизации с условиями и действиями."""
        conditions_data = validated_data.pop('conditions')
        actions_data = validated_data.pop('actions')
        
        validated_data['author'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].user.tenant
        rule = super().create(validated_data)
        
        # Создаем условия
        for condition_data in conditions_data:
            AutomationCondition.objects.create(rule=rule, **condition_data)
        
        # Создаем действия
        for action_data in actions_data:
            AutomationAction.objects.create(rule=rule, **action_data)
        
        return rule


class AutomationRuleUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления правил автоматизации."""
    
    class Meta:
        model = AutomationRule
        fields = [
            'name', 'description', 'is_active', 'priority', 'trigger_event'
        ]


class AutomationExecutionSerializer(serializers.ModelSerializer):
    """Сериализатор для выполнений автоматизации."""
    
    rule_name = serializers.CharField(source='rule.name', read_only=True)
    executed_by_name = serializers.CharField(source='executed_by.get_full_name', read_only=True)
    
    class Meta:
        model = AutomationExecution
        fields = [
            'id', 'rule', 'rule_name', 'executed_by', 'executed_by_name',
            'status', 'result', 'error_message', 'executed_at', 'duration'
        ]
        read_only_fields = ['id', 'executed_at', 'duration']


class AutomationExecutionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания выполнений автоматизации."""
    
    class Meta:
        model = AutomationExecution
        fields = ['rule', 'status', 'result', 'error_message']
    
    def create(self, validated_data):
        """Создание выполнения автоматизации."""
        validated_data['executed_by'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class AutomationTemplateSerializer(serializers.ModelSerializer):
    """Сериализатор для шаблонов автоматизации."""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    usage_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AutomationTemplate
        fields = [
            'id', 'name', 'description', 'template_data', 'category',
            'author', 'author_name', 'is_public', 'usage_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_usage_count(self, obj):
        """Количество использований шаблона."""
        return obj.usage.count()


class AutomationTemplateCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания шаблонов автоматизации."""
    
    class Meta:
        model = AutomationTemplate
        fields = [
            'name', 'description', 'template_data', 'category', 'is_public'
        ]
    
    def create(self, validated_data):
        """Создание шаблона автоматизации."""
        validated_data['author'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class AutomationScheduleSerializer(serializers.ModelSerializer):
    """Сериализатор для расписаний автоматизации."""
    
    rule_name = serializers.CharField(source='rule.name', read_only=True)
    
    class Meta:
        model = AutomationSchedule
        fields = [
            'id', 'rule', 'rule_name', 'schedule_type', 'schedule_data',
            'is_active', 'next_run', 'last_run', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'next_run', 'last_run', 'created_at', 'updated_at']


class AutomationScheduleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания расписаний автоматизации."""
    
    class Meta:
        model = AutomationSchedule
        fields = ['rule', 'schedule_type', 'schedule_data', 'is_active']
    
    def create(self, validated_data):
        """Создание расписания автоматизации."""
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class AutomationStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики автоматизации."""
    
    total_rules = serializers.IntegerField()
    active_rules = serializers.IntegerField()
    inactive_rules = serializers.IntegerField()
    
    total_executions = serializers.IntegerField()
    successful_executions = serializers.IntegerField()
    failed_executions = serializers.IntegerField()
    
    success_rate = serializers.FloatField()
    average_execution_time = serializers.FloatField()
    
    rules_by_trigger = serializers.DictField()
    executions_by_hour = serializers.DictField()
    
    top_rules = serializers.ListField()
    recent_executions = serializers.ListField()


class AutomationReportSerializer(serializers.Serializer):
    """Сериализатор для отчета по автоматизации."""
    
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    
    total_rules = serializers.IntegerField()
    rules_created = serializers.IntegerField()
    rules_updated = serializers.IntegerField()
    
    total_executions = serializers.IntegerField()
    executions_by_rule = serializers.DictField()
    executions_by_status = serializers.DictField()
    
    performance_metrics = serializers.DictField()
    recommendations = serializers.ListField()


class AutomationSearchSerializer(serializers.Serializer):
    """Сериализатор для поиска автоматизации."""
    
    query = serializers.CharField(max_length=255)
    trigger_event = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)
    author = serializers.PrimaryKeyRelatedField(
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
