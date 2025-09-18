"""
Сериализаторы для базы знаний.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from app.models import (
    KnowledgeCategory, KnowledgeArticle, KnowledgeArticleAttachment,
    KnowledgeArticleRating, KnowledgeArticleView, KnowledgeSearch
)

User = get_user_model()


class KnowledgeCategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий базы знаний."""
    
    articles_count = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeCategory
        fields = [
            'id', 'name', 'description', 'parent', 'order',
            'is_active', 'created_at', 'updated_at',
            'articles_count', 'children_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_articles_count(self, obj):
        """Количество статей в категории."""
        return obj.articles.filter(status='published').count()
    
    def get_children_count(self, obj):
        """Количество подкатегорий."""
        return obj.children.filter(is_active=True).count()


class KnowledgeArticleAttachmentSerializer(serializers.ModelSerializer):
    """Сериализатор для вложений статей."""
    
    class Meta:
        model = KnowledgeArticleAttachment
        fields = [
            'id', 'file', 'filename', 'file_size', 'mime_type', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class KnowledgeArticleRatingSerializer(serializers.ModelSerializer):
    """Сериализатор для оценок статей."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = KnowledgeArticleRating
        fields = [
            'id', 'rating', 'comment', 'user', 'user_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class KnowledgeArticleListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка статей."""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    helpful_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeArticle
        fields = [
            'id', 'title', 'slug', 'excerpt', 'category', 'category_name',
            'author', 'author_name', 'status', 'view_count', 'helpful_count',
            'not_helpful_count', 'published_at', 'created_at', 'updated_at',
            'tags', 'average_rating', 'helpful_percentage'
        ]
    
    def get_average_rating(self, obj):
        """Средняя оценка статьи."""
        ratings = obj.ratings.all()
        if ratings.exists():
            return sum(r.rating for r in ratings) / ratings.count()
        return 0
    
    def get_helpful_percentage(self, obj):
        """Процент полезности статьи."""
        total_ratings = obj.helpful_count + obj.not_helpful_count
        if total_ratings > 0:
            return (obj.helpful_count / total_ratings) * 100
        return 0


class KnowledgeArticleDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра статьи."""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_avatar = serializers.ImageField(source='author.avatar', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)
    attachments = KnowledgeArticleAttachmentSerializer(many=True, read_only=True)
    ratings = KnowledgeArticleRatingSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    helpful_percentage = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeArticle
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'category', 'category_name',
            'author', 'author_name', 'author_avatar', 'status', 'meta_title',
            'meta_description', 'keywords', 'view_count', 'helpful_count',
            'not_helpful_count', 'published_at', 'created_at', 'updated_at',
            'custom_fields', 'tags', 'attachments', 'ratings', 'average_rating',
            'helpful_percentage', 'user_rating'
        ]
    
    def get_average_rating(self, obj):
        """Средняя оценка статьи."""
        ratings = obj.ratings.all()
        if ratings.exists():
            return sum(r.rating for r in ratings) / ratings.count()
        return 0
    
    def get_helpful_percentage(self, obj):
        """Процент полезности статьи."""
        total_ratings = obj.helpful_count + obj.not_helpful_count
        if total_ratings > 0:
            return (obj.helpful_count / total_ratings) * 100
        return 0
    
    def get_user_rating(self, obj):
        """Оценка текущего пользователя."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                rating = obj.ratings.get(user=request.user)
                return {
                    'rating': rating.rating,
                    'comment': rating.comment,
                    'created_at': rating.created_at
                }
            except KnowledgeArticleRating.DoesNotExist:
                return None
        return None


class KnowledgeArticleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания статьи."""
    
    class Meta:
        model = KnowledgeArticle
        fields = [
            'title', 'content', 'excerpt', 'category', 'status',
            'meta_title', 'meta_description', 'keywords', 'custom_fields', 'tags'
        ]
    
    def create(self, validated_data):
        """Создание статьи."""
        validated_data['author'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class KnowledgeArticleUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления статьи."""
    
    class Meta:
        model = KnowledgeArticle
        fields = [
            'title', 'content', 'excerpt', 'category', 'status',
            'meta_title', 'meta_description', 'keywords', 'custom_fields', 'tags'
        ]
    
    def update(self, instance, validated_data):
        """Обновление статьи."""
        # Обновляем время публикации при изменении статуса
        if 'status' in validated_data:
            if validated_data['status'] == 'published' and not instance.published_at:
                from django.utils import timezone
                validated_data['published_at'] = timezone.now()
            elif validated_data['status'] != 'published':
                validated_data['published_at'] = None
        
        return super().update(instance, validated_data)


class KnowledgeArticleRatingCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания оценки статьи."""
    
    class Meta:
        model = KnowledgeArticleRating
        fields = ['rating', 'comment']
    
    def create(self, validated_data):
        """Создание оценки."""
        validated_data['user'] = self.context['request'].user
        validated_data['article'] = self.context['article']
        return super().create(validated_data)


class KnowledgeSearchSerializer(serializers.ModelSerializer):
    """Сериализатор для поиска в базе знаний."""
    
    class Meta:
        model = KnowledgeSearch
        fields = ['query', 'results_count', 'searched_at']
        read_only_fields = ['results_count', 'searched_at']


class KnowledgeSearchRequestSerializer(serializers.Serializer):
    """Сериализатор для запроса поиска."""
    
    query = serializers.CharField(max_length=255)
    category = serializers.PrimaryKeyRelatedField(
        queryset=KnowledgeCategory.objects.all(),
        required=False
    )
    tags = serializers.CharField(required=False, allow_blank=True)
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    min_rating = serializers.FloatField(required=False, min_value=1, max_value=5)
    sort_by = serializers.ChoiceField(
        choices=[
            ('relevance', 'Релевантность'),
            ('date', 'Дата'),
            ('rating', 'Рейтинг'),
            ('views', 'Просмотры'),
            ('helpful', 'Полезность')
        ],
        default='relevance'
    )
    
    def validate(self, attrs):
        """Валидация параметров поиска."""
        if attrs.get('date_from') and attrs.get('date_to'):
            if attrs['date_from'] > attrs['date_to']:
                raise serializers.ValidationError("Дата начала не может быть больше даты окончания")
        return attrs


class KnowledgeStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики базы знаний."""
    
    total_articles = serializers.IntegerField()
    published_articles = serializers.IntegerField()
    draft_articles = serializers.IntegerField()
    archived_articles = serializers.IntegerField()
    
    total_categories = serializers.IntegerField()
    active_categories = serializers.IntegerField()
    
    total_views = serializers.IntegerField()
    total_ratings = serializers.IntegerField()
    average_rating = serializers.FloatField()
    
    most_viewed_articles = serializers.ListField()
    most_rated_articles = serializers.ListField()
    most_helpful_articles = serializers.ListField()
    
    recent_articles = serializers.ListField()
    recent_searches = serializers.ListField()


class KnowledgeCategoryTreeSerializer(serializers.ModelSerializer):
    """Сериализатор для дерева категорий."""
    
    children = serializers.SerializerMethodField()
    articles_count = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeCategory
        fields = [
            'id', 'name', 'description', 'order', 'is_active',
            'articles_count', 'children'
        ]
    
    def get_children(self, obj):
        """Получение дочерних категорий."""
        children = obj.children.filter(is_active=True).order_by('order', 'name')
        return KnowledgeCategoryTreeSerializer(children, many=True).data
    
    def get_articles_count(self, obj):
        """Количество статей в категории."""
        return obj.articles.filter(status='published').count()
