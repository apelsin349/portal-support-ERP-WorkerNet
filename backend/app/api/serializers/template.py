"""
Сериализаторы для шаблонов ответов.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from app.models import (
    ResponseTemplate, TemplateVariable, TemplateUsage, TemplateCategory,
    TemplateVersion
)

User = get_user_model()


class TemplateVariableSerializer(serializers.ModelSerializer):
    """Сериализатор для переменных шаблонов."""
    
    class Meta:
        model = TemplateVariable
        fields = [
            'id', 'name', 'description', 'variable_type', 'default_value',
            'is_required', 'validation_rule', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TemplateCategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий шаблонов."""
    
    templates_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TemplateCategory
        fields = [
            'id', 'name', 'description', 'is_active', 'templates_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_templates_count(self, obj):
        """Количество шаблонов в категории."""
        return obj.templates.filter(is_active=True).count()


class TemplateVersionSerializer(serializers.ModelSerializer):
    """Сериализатор для версий шаблонов."""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = TemplateVersion
        fields = [
            'id', 'template', 'version_number', 'content', 'author', 'author_name',
            'change_log', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TemplateUsageSerializer(serializers.ModelSerializer):
    """Сериализатор для использования шаблонов."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = TemplateUsage
        fields = [
            'id', 'template', 'template_name', 'user', 'user_name',
            'used_at', 'context', 'variables_used'
        ]
        read_only_fields = ['id', 'used_at']


class ResponseTemplateListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка шаблонов ответов."""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    usage_count = serializers.SerializerMethodField()
    last_used = serializers.SerializerMethodField()
    
    class Meta:
        model = ResponseTemplate
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'author', 'author_name', 'is_active', 'usage_count',
            'last_used', 'created_at', 'updated_at'
        ]
    
    def get_usage_count(self, obj):
        """Количество использований шаблона."""
        return obj.usage.count()
    
    def get_last_used(self, obj):
        """Последнее использование шаблона."""
        last_usage = obj.usage.order_by('-used_at').first()
        if last_usage:
            return last_usage.used_at
        return None


class ResponseTemplateDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра шаблонов ответов."""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_avatar = serializers.ImageField(source='author.avatar', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    variables = TemplateVariableSerializer(many=True, read_only=True)
    versions = TemplateVersionSerializer(many=True, read_only=True)
    usage = TemplateUsageSerializer(many=True, read_only=True)
    
    usage_count = serializers.SerializerMethodField()
    last_used = serializers.SerializerMethodField()
    
    class Meta:
        model = ResponseTemplate
        fields = [
            'id', 'name', 'description', 'content', 'category', 'category_name',
            'author', 'author_name', 'author_avatar', 'is_active', 'tags',
            'variables', 'versions', 'usage', 'usage_count', 'last_used',
            'created_at', 'updated_at'
        ]
    
    def get_usage_count(self, obj):
        """Количество использований шаблона."""
        return obj.usage.count()
    
    def get_last_used(self, obj):
        """Последнее использование шаблона."""
        last_usage = obj.usage.order_by('-used_at').first()
        if last_usage:
            return last_usage.used_at
        return None


class ResponseTemplateCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания шаблонов ответов."""
    
    class Meta:
        model = ResponseTemplate
        fields = [
            'name', 'description', 'content', 'category', 'is_active', 'tags'
        ]
    
    def create(self, validated_data):
        """Создание шаблона ответа."""
        validated_data['author'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class ResponseTemplateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления шаблонов ответов."""
    
    class Meta:
        model = ResponseTemplate
        fields = [
            'name', 'description', 'content', 'category', 'is_active', 'tags'
        ]
    
    def update(self, instance, validated_data):
        """Обновление шаблона ответа."""
        # Создаем новую версию при изменении контента
        if 'content' in validated_data and validated_data['content'] != instance.content:
            # Создаем новую версию
            TemplateVersion.objects.create(
                template=instance,
                version_number=instance.versions.count() + 1,
                content=validated_data['content'],
                author=self.context['request'].user,
                change_log=f"Обновление шаблона: {validated_data.get('name', instance.name)}",
                tenant=self.context['request'].user.tenant
            )
        
        return super().update(instance, validated_data)


class TemplateUsageCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания использования шаблонов."""
    
    class Meta:
        model = TemplateUsage
        fields = ['context', 'variables_used']
    
    def create(self, validated_data):
        """Создание использования шаблона."""
        validated_data['user'] = self.context['request'].user
        validated_data['template'] = self.context['template']
        return super().create(validated_data)


class TemplateSearchSerializer(serializers.Serializer):
    """Сериализатор для поиска шаблонов."""
    
    query = serializers.CharField(max_length=255)
    category = serializers.PrimaryKeyRelatedField(
        queryset=TemplateCategory.objects.all(),
        required=False
    )
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )
    tags = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)
    
    def validate(self, attrs):
        """Валидация параметров поиска."""
        return attrs


class TemplateStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики шаблонов."""
    
    total_templates = serializers.IntegerField()
    active_templates = serializers.IntegerField()
    inactive_templates = serializers.IntegerField()
    
    templates_by_category = serializers.DictField()
    templates_by_author = serializers.DictField()
    
    most_used_templates = serializers.ListField()
    recent_templates = serializers.ListField()
    
    usage_stats = serializers.DictField()


class TemplateReportSerializer(serializers.Serializer):
    """Сериализатор для отчета по шаблонам."""
    
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    
    total_templates = serializers.IntegerField()
    templates_created = serializers.IntegerField()
    templates_updated = serializers.IntegerField()
    
    usage_count = serializers.IntegerField()
    usage_by_template = serializers.DictField()
    usage_by_user = serializers.DictField()
    
    top_templates = serializers.ListField()
    recommendations = serializers.ListField()


class TemplatePreviewSerializer(serializers.Serializer):
    """Сериализатор для предварительного просмотра шаблона."""
    
    template_id = serializers.IntegerField()
    variables = serializers.DictField()
    preview_content = serializers.CharField()
    
    def validate(self, attrs):
        """Валидация параметров предварительного просмотра."""
        template_id = attrs.get('template_id')
        variables = attrs.get('variables', {})
        
        try:
            template = ResponseTemplate.objects.get(id=template_id)
        except ResponseTemplate.DoesNotExist:
            raise serializers.ValidationError("Шаблон не найден")
        
        # Проверяем обязательные переменные
        required_variables = template.variables.filter(is_required=True)
        for variable in required_variables:
            if variable.name not in variables:
                raise serializers.ValidationError(
                    f"Обязательная переменная {variable.name} не указана"
                )
        
        return attrs
