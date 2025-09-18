"""
Сериализаторы для A/B тестирования.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from app.models import (
    FeatureFlag, ABTest, ABTestVariant, ABTestParticipant,
    ABTestEvent, ABTestMetric
)

User = get_user_model()


class FeatureFlagSerializer(serializers.ModelSerializer):
    """Сериализатор для флагов функций."""
    
    class Meta:
        model = FeatureFlag
        fields = [
            'id', 'name', 'description', 'is_enabled', 'rollout_percentage',
            'target_audience', 'conditions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FeatureFlagCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания флагов функций."""
    
    class Meta:
        model = FeatureFlag
        fields = [
            'name', 'description', 'is_enabled', 'rollout_percentage',
            'target_audience', 'conditions'
        ]
    
    def create(self, validated_data):
        """Создание флага функции."""
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class ABTestVariantSerializer(serializers.ModelSerializer):
    """Сериализатор для вариантов A/B теста."""
    
    class Meta:
        model = ABTestVariant
        fields = [
            'id', 'name', 'description', 'configuration', 'traffic_percentage',
            'is_control', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ABTestVariantCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания вариантов A/B теста."""
    
    class Meta:
        model = ABTestVariant
        fields = [
            'name', 'description', 'configuration', 'traffic_percentage',
            'is_control'
        ]


class ABTestSerializer(serializers.ModelSerializer):
    """Сериализатор для A/B тестов."""
    
    variants = ABTestVariantSerializer(many=True, read_only=True)
    participants_count = serializers.SerializerMethodField()
    conversion_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = ABTest
        fields = [
            'id', 'name', 'description', 'status', 'start_date', 'end_date',
            'target_audience', 'success_metrics', 'variants', 'participants_count',
            'conversion_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_participants_count(self, obj):
        """Количество участников теста."""
        return obj.participants.count()
    
    def get_conversion_rate(self, obj):
        """Конверсия теста."""
        total_participants = obj.participants.count()
        if total_participants == 0:
            return 0
        
        conversions = ABTestEvent.objects.filter(
            test=obj,
            event_type='conversion'
        ).count()
        
        return (conversions / total_participants) * 100


class ABTestCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания A/B тестов."""
    
    variants = ABTestVariantCreateSerializer(many=True, write_only=True)
    
    class Meta:
        model = ABTest
        fields = [
            'name', 'description', 'start_date', 'end_date',
            'target_audience', 'success_metrics', 'variants'
        ]
    
    def create(self, validated_data):
        """Создание A/B теста с вариантами."""
        variants_data = validated_data.pop('variants')
        validated_data['tenant'] = self.context['request'].user.tenant
        test = super().create(validated_data)
        
        for variant_data in variants_data:
            ABTestVariant.objects.create(test=test, **variant_data)
        
        return test


class ABTestParticipantSerializer(serializers.ModelSerializer):
    """Сериализатор для участников A/B теста."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True)
    
    class Meta:
        model = ABTestParticipant
        fields = [
            'id', 'user', 'user_name', 'variant', 'variant_name',
            'joined_at', 'is_active'
        ]
        read_only_fields = ['id', 'joined_at']


class ABTestEventSerializer(serializers.ModelSerializer):
    """Сериализатор для событий A/B теста."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True)
    
    class Meta:
        model = ABTestEvent
        fields = [
            'id', 'user', 'user_name', 'variant', 'variant_name',
            'event_type', 'event_data', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class ABTestEventCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания событий A/B теста."""
    
    class Meta:
        model = ABTestEvent
        fields = ['event_type', 'event_data']
    
    def create(self, validated_data):
        """Создание события A/B теста."""
        validated_data['user'] = self.context['request'].user
        validated_data['test'] = self.context['test']
        validated_data['variant'] = self.context['variant']
        return super().create(validated_data)


class ABTestMetricSerializer(serializers.ModelSerializer):
    """Сериализатор для метрик A/B теста."""
    
    class Meta:
        model = ABTestMetric
        fields = [
            'id', 'test', 'variant', 'metric_name', 'metric_value',
            'calculated_at'
        ]
        read_only_fields = ['id', 'calculated_at']


class ABTestStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики A/B теста."""
    
    test_id = serializers.IntegerField()
    test_name = serializers.CharField()
    status = serializers.CharField()
    
    total_participants = serializers.IntegerField()
    participants_by_variant = serializers.DictField()
    
    conversion_rates = serializers.DictField()
    statistical_significance = serializers.FloatField()
    
    winner_variant = serializers.CharField(allow_null=True)
    confidence_level = serializers.FloatField()
    
    recommendations = serializers.ListField()


class ABTestReportSerializer(serializers.Serializer):
    """Сериализатор для отчета A/B теста."""
    
    test_id = serializers.IntegerField()
    test_name = serializers.CharField()
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    
    variants_performance = serializers.ListField()
    key_metrics = serializers.DictField()
    
    statistical_analysis = serializers.DictField()
    business_impact = serializers.DictField()
    
    conclusions = serializers.ListField()
    next_steps = serializers.ListField()


class FeatureFlagUsageSerializer(serializers.Serializer):
    """Сериализатор для использования флагов функций."""
    
    flag_name = serializers.CharField()
    is_enabled = serializers.BooleanField()
    user_id = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    context = serializers.DictField()


class ABTestAssignmentSerializer(serializers.Serializer):
    """Сериализатор для назначения пользователя в A/B тест."""
    
    test_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False)
    force_variant = serializers.BooleanField(default=False)
