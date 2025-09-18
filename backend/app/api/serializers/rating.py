"""
Сериализаторы для системы рейтингов.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from app.models import (
    TicketRating, AgentRating, ServiceRating, RatingCategory,
    RatingSurvey, RatingSurveyQuestion, RatingSurveyResponse
)

User = get_user_model()


class RatingCategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий рейтингов."""
    
    class Meta:
        model = RatingCategory
        fields = [
            'id', 'name', 'description', 'is_active', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TicketRatingSerializer(serializers.ModelSerializer):
    """Сериализатор для рейтингов тикетов."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    ticket_title = serializers.CharField(source='ticket.title', read_only=True)
    agent_name = serializers.CharField(source='agent.get_full_name', read_only=True)
    
    class Meta:
        model = TicketRating
        fields = [
            'id', 'ticket', 'ticket_title', 'user', 'user_name',
            'agent', 'agent_name', 'rating', 'comment', 'is_public',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TicketRatingCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рейтингов тикетов."""
    
    class Meta:
        model = TicketRating
        fields = ['ticket', 'agent', 'rating', 'comment', 'is_public']
    
    def create(self, validated_data):
        """Создание рейтинга тикета."""
        validated_data['user'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class AgentRatingSerializer(serializers.ModelSerializer):
    """Сериализатор для рейтингов агентов."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    agent_name = serializers.CharField(source='agent.get_full_name', read_only=True)
    
    class Meta:
        model = AgentRating
        fields = [
            'id', 'agent', 'agent_name', 'user', 'user_name',
            'rating', 'comment', 'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AgentRatingCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рейтингов агентов."""
    
    class Meta:
        model = AgentRating
        fields = ['agent', 'rating', 'comment', 'is_public']
    
    def create(self, validated_data):
        """Создание рейтинга агента."""
        validated_data['user'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class ServiceRatingSerializer(serializers.ModelSerializer):
    """Сериализатор для рейтингов сервиса."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = ServiceRating
        fields = [
            'id', 'user', 'user_name', 'rating', 'comment', 'is_public',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceRatingCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рейтингов сервиса."""
    
    class Meta:
        model = ServiceRating
        fields = ['rating', 'comment', 'is_public']
    
    def create(self, validated_data):
        """Создание рейтинга сервиса."""
        validated_data['user'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class RatingSurveyQuestionSerializer(serializers.ModelSerializer):
    """Сериализатор для вопросов опросов рейтингов."""
    
    class Meta:
        model = RatingSurveyQuestion
        fields = [
            'id', 'survey', 'question_text', 'question_type', 'is_required',
            'options', 'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RatingSurveyQuestionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания вопросов опросов рейтингов."""
    
    class Meta:
        model = RatingSurveyQuestion
        fields = ['question_text', 'question_type', 'is_required', 'options', 'order']
    
    def create(self, validated_data):
        """Создание вопроса опроса."""
        validated_data['survey'] = self.context['survey']
        return super().create(validated_data)


class RatingSurveySerializer(serializers.ModelSerializer):
    """Сериализатор для опросов рейтингов."""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    questions = RatingSurveyQuestionSerializer(many=True, read_only=True)
    responses_count = serializers.SerializerMethodField()
    
    class Meta:
        model = RatingSurvey
        fields = [
            'id', 'title', 'description', 'author', 'author_name',
            'is_active', 'start_date', 'end_date', 'questions',
            'responses_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_responses_count(self, obj):
        """Количество ответов на опрос."""
        return obj.responses.count()


class RatingSurveyCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания опросов рейтингов."""
    
    questions = RatingSurveyQuestionCreateSerializer(many=True, write_only=True)
    
    class Meta:
        model = RatingSurvey
        fields = [
            'title', 'description', 'is_active', 'start_date', 'end_date', 'questions'
        ]
    
    def create(self, validated_data):
        """Создание опроса с вопросами."""
        questions_data = validated_data.pop('questions')
        validated_data['author'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].user.tenant
        survey = super().create(validated_data)
        
        for question_data in questions_data:
            RatingSurveyQuestion.objects.create(survey=survey, **question_data)
        
        return survey


class RatingSurveyResponseSerializer(serializers.ModelSerializer):
    """Сериализатор для ответов на опросы рейтингов."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    survey_title = serializers.CharField(source='survey.title', read_only=True)
    
    class Meta:
        model = RatingSurveyResponse
        fields = [
            'id', 'survey', 'survey_title', 'user', 'user_name',
            'answers', 'submitted_at'
        ]
        read_only_fields = ['id', 'submitted_at']


class RatingSurveyResponseCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ответов на опросы рейтингов."""
    
    class Meta:
        model = RatingSurveyResponse
        fields = ['answers']
    
    def create(self, validated_data):
        """Создание ответа на опрос."""
        validated_data['user'] = self.context['request'].user
        validated_data['survey'] = self.context['survey']
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)


class RatingStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики рейтингов."""
    
    total_ratings = serializers.IntegerField()
    average_rating = serializers.FloatField()
    
    ratings_by_score = serializers.DictField()
    ratings_by_category = serializers.DictField()
    
    top_rated_agents = serializers.ListField()
    recent_ratings = serializers.ListField()
    
    rating_trends = serializers.DictField()


class RatingReportSerializer(serializers.Serializer):
    """Сериализатор для отчета по рейтингам."""
    
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    
    total_ratings = serializers.IntegerField()
    average_rating = serializers.FloatField()
    
    ratings_by_agent = serializers.DictField()
    ratings_by_ticket = serializers.DictField()
    
    satisfaction_score = serializers.FloatField()
    recommendations = serializers.ListField()


class RatingSearchSerializer(serializers.Serializer):
    """Сериализатор для поиска рейтингов."""
    
    query = serializers.CharField(max_length=255)
    rating_type = serializers.ChoiceField(
        choices=['ticket', 'agent', 'service'],
        required=False
    )
    min_rating = serializers.FloatField(required=False, min_value=1, max_value=5)
    max_rating = serializers.FloatField(required=False, min_value=1, max_value=5)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    
    def validate(self, attrs):
        """Валидация параметров поиска."""
        min_rating = attrs.get('min_rating')
        max_rating = attrs.get('max_rating')
        
        if min_rating and max_rating and min_rating > max_rating:
            raise serializers.ValidationError(
                "Минимальный рейтинг не может быть больше максимального"
            )
        
        if attrs.get('date_from') and attrs.get('date_to'):
            if attrs['date_from'] > attrs['date_to']:
                raise serializers.ValidationError(
                    "Дата начала не может быть больше даты окончания"
                )
        
        return attrs
