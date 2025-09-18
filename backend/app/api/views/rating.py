"""
Представления для системы рейтингов.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from app.models import (
    TicketRating, AgentRating, ServiceRating, RatingCategory,
    RatingSurvey, RatingSurveyQuestion, RatingSurveyResponse
)
from app.api.serializers.rating import (
    TicketRatingSerializer, TicketRatingCreateSerializer,
    AgentRatingSerializer, AgentRatingCreateSerializer,
    ServiceRatingSerializer, ServiceRatingCreateSerializer,
    RatingSurveySerializer, RatingSurveyCreateSerializer,
    RatingSurveyQuestionSerializer, RatingSurveyQuestionCreateSerializer,
    RatingSurveyResponseSerializer, RatingSurveyResponseCreateSerializer,
    RatingCategorySerializer, RatingStatsSerializer, RatingReportSerializer,
    RatingSearchSerializer
)

User = get_user_model()


class TicketRatingViewSet(viewsets.ModelViewSet):
    """Управление рейтингами тикетов."""
    
    queryset = TicketRating.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['ticket', 'agent', 'rating', 'is_public']
    search_fields = ['comment']
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return TicketRatingCreateSerializer
        else:
            return TicketRatingSerializer
    
    @action(detail=False, methods=['get'])
    def by_ticket(self, request):
        """Рейтинги по тикету."""
        ticket_id = request.query_params.get('ticket_id')
        
        if not ticket_id:
            return Response(
                {'error': 'ticket_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ratings = self.get_queryset().filter(ticket_id=ticket_id)
        serializer = TicketRatingSerializer(ratings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_agent(self, request):
        """Рейтинги по агенту."""
        agent_id = request.query_params.get('agent_id')
        
        if not agent_id:
            return Response(
                {'error': 'agent_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ratings = self.get_queryset().filter(agent_id=agent_id)
        serializer = TicketRatingSerializer(ratings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_ratings(self, request):
        """Рейтинги текущего пользователя."""
        user = request.user
        ratings = self.get_queryset().filter(user=user)
        serializer = TicketRatingSerializer(ratings, many=True)
        return Response(serializer.data)


class AgentRatingViewSet(viewsets.ModelViewSet):
    """Управление рейтингами агентов."""
    
    queryset = AgentRating.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['agent', 'rating', 'is_public']
    search_fields = ['comment']
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return AgentRatingCreateSerializer
        else:
            return AgentRatingSerializer
    
    @action(detail=False, methods=['get'])
    def by_agent(self, request):
        """Рейтинги по агенту."""
        agent_id = request.query_params.get('agent_id')
        
        if not agent_id:
            return Response(
                {'error': 'agent_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ratings = self.get_queryset().filter(agent_id=agent_id)
        serializer = AgentRatingSerializer(ratings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_ratings(self, request):
        """Рейтинги текущего пользователя."""
        user = request.user
        ratings = self.get_queryset().filter(user=user)
        serializer = AgentRatingSerializer(ratings, many=True)
        return Response(serializer.data)


class ServiceRatingViewSet(viewsets.ModelViewSet):
    """Управление рейтингами сервиса."""
    
    queryset = ServiceRating.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rating', 'is_public']
    search_fields = ['comment']
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return ServiceRatingCreateSerializer
        else:
            return ServiceRatingSerializer
    
    @action(detail=False, methods=['get'])
    def my_ratings(self, request):
        """Рейтинги текущего пользователя."""
        user = request.user
        ratings = self.get_queryset().filter(user=user)
        serializer = ServiceRatingSerializer(ratings, many=True)
        return Response(serializer.data)


class RatingSurveyViewSet(viewsets.ModelViewSet):
    """Управление опросами рейтингов."""
    
    queryset = RatingSurvey.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'author']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'start_date', 'end_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return RatingSurveyCreateSerializer
        else:
            return RatingSurveySerializer
    
    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """Ответ на опрос."""
        survey = self.get_object()
        serializer = RatingSurveyResponseCreateSerializer(
            data=request.data,
            context={'request': request, 'survey': survey}
        )
        
        if serializer.is_valid():
            response = serializer.save()
            return Response({
                'message': 'Ответ на опрос сохранен',
                'response_id': response.id
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def responses(self, request, pk=None):
        """Ответы на опрос."""
        survey = self.get_object()
        responses = survey.responses.all().order_by('-submitted_at')
        
        # Пагинация
        paginator = PageNumberPagination()
        paginated_responses = paginator.paginate_queryset(responses, request)
        
        serializer = RatingSurveyResponseSerializer(paginated_responses, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active_surveys(self, request):
        """Активные опросы."""
        now = timezone.now()
        surveys = self.get_queryset().filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )
        
        serializer = RatingSurveySerializer(surveys, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_surveys(self, request):
        """Опросы текущего пользователя."""
        user = request.user
        surveys = self.get_queryset().filter(author=user)
        serializer = RatingSurveySerializer(surveys, many=True)
        return Response(serializer.data)


class RatingSurveyQuestionViewSet(viewsets.ModelViewSet):
    """Управление вопросами опросов рейтингов."""
    
    queryset = RatingSurveyQuestion.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['survey', 'question_type', 'is_required']
    ordering_fields = ['order', 'created_at']
    ordering = ['order']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(survey__tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return RatingSurveyQuestionCreateSerializer
        else:
            return RatingSurveyQuestionSerializer


class RatingSurveyResponseViewSet(viewsets.ModelViewSet):
    """Управление ответами на опросы рейтингов."""
    
    queryset = RatingSurveyResponse.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['survey', 'user']
    ordering_fields = ['submitted_at']
    ordering = ['-submitted_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return RatingSurveyResponseCreateSerializer
        else:
            return RatingSurveyResponseSerializer
    
    @action(detail=False, methods=['get'])
    def my_responses(self, request):
        """Ответы текущего пользователя."""
        user = request.user
        responses = self.get_queryset().filter(user=user)
        serializer = RatingSurveyResponseSerializer(responses, many=True)
        return Response(serializer.data)


class RatingCategoryViewSet(viewsets.ModelViewSet):
    """Управление категориями рейтингов."""
    
    queryset = RatingCategory.objects.all()
    serializer_class = RatingCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'order', 'created_at']
    ordering = ['order', 'name']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика рейтингов."""
        tenant = request.user.tenant
        
        # Общая статистика
        total_ratings = TicketRating.objects.filter(tenant=tenant).count()
        average_rating = TicketRating.objects.filter(tenant=tenant).aggregate(
            avg=Avg('rating')
        )['avg'] or 0
        
        # Рейтинги по баллам
        ratings_by_score = TicketRating.objects.filter(tenant=tenant).values(
            'rating'
        ).annotate(count=Count('id')).order_by('rating')
        
        # Рейтинги по категориям (если есть)
        ratings_by_category = {}
        
        # Топ рейтинговые агенты
        top_rated_agents = TicketRating.objects.filter(tenant=tenant).values(
            'agent__first_name', 'agent__last_name'
        ).annotate(
            avg_rating=Avg('rating'),
            count=Count('id')
        ).filter(count__gte=5).order_by('-avg_rating')[:10]
        
        # Недавние рейтинги
        recent_ratings = TicketRating.objects.filter(tenant=tenant).order_by('-created_at')[:10]
        
        # Тренды рейтингов (по месяцам)
        rating_trends = {}
        for i in range(6):  # Последние 6 месяцев
            month_start = timezone.now() - timezone.timedelta(days=30*i)
            month_end = month_start + timezone.timedelta(days=30)
            
            month_ratings = TicketRating.objects.filter(
                tenant=tenant,
                created_at__range=[month_start, month_end]
            ).aggregate(avg=Avg('rating'))['avg'] or 0
            
            month_name = month_start.strftime('%Y-%m')
            rating_trends[month_name] = round(month_ratings, 2)
        
        stats_data = {
            'total_ratings': total_ratings,
            'average_rating': round(average_rating, 2),
            'ratings_by_score': dict(ratings_by_score),
            'ratings_by_category': ratings_by_category,
            'top_rated_agents': list(top_rated_agents),
            'recent_ratings': TicketRatingSerializer(recent_ratings, many=True).data,
            'rating_trends': rating_trends,
        }
        
        serializer = RatingStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """Отчет по рейтингам."""
        tenant = request.user.tenant
        
        # Период отчета
        period_start = request.query_params.get('start')
        period_end = request.query_params.get('end')
        
        if not period_start or not period_end:
            return Response(
                {'error': 'Параметры start и end обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from datetime import datetime
            period_start = datetime.strptime(period_start, '%Y-%m-%d').date()
            period_end = datetime.strptime(period_end, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Неверный формат даты. Используйте YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Фильтруем рейтинги по периоду
        ratings = TicketRating.objects.filter(
            tenant=tenant,
            created_at__date__range=[period_start, period_end]
        )
        
        # Общая статистика
        total_ratings = ratings.count()
        average_rating = ratings.aggregate(avg=Avg('rating'))['avg'] or 0
        
        # Рейтинги по агентам
        ratings_by_agent = ratings.values(
            'agent__first_name', 'agent__last_name'
        ).annotate(
            avg_rating=Avg('rating'),
            count=Count('id')
        ).order_by('-avg_rating')
        
        # Рейтинги по тикетам
        ratings_by_ticket = ratings.values('ticket__title').annotate(
            avg_rating=Avg('rating'),
            count=Count('id')
        ).order_by('-avg_rating')
        
        # Общий балл удовлетворенности
        satisfaction_score = average_rating
        
        # Рекомендации
        recommendations = []
        
        if average_rating < 3.0:
            recommendations.append("Низкий средний рейтинг. Рассмотрите улучшение качества обслуживания")
        elif average_rating > 4.5:
            recommendations.append("Отличные рейтинги! Продолжайте в том же духе")
        
        if total_ratings < 10:
            recommendations.append("Мало рейтингов. Рассмотрите стимулирование пользователей к оценке")
        
        report_data = {
            'period_start': period_start,
            'period_end': period_end,
            'total_ratings': total_ratings,
            'average_rating': round(average_rating, 2),
            'ratings_by_agent': dict(ratings_by_agent),
            'ratings_by_ticket': dict(ratings_by_ticket),
            'satisfaction_score': round(satisfaction_score, 2),
            'recommendations': recommendations,
        }
        
        serializer = RatingReportSerializer(report_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Поиск рейтингов."""
        serializer = RatingSearchSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        query = data['query']
        
        # Базовый запрос
        ratings = TicketRating.objects.filter(tenant=request.user.tenant)
        
        # Поиск по тексту
        if query:
            ratings = ratings.filter(comment__icontains=query)
        
        # Фильтры
        if data.get('rating_type') == 'ticket':
            ratings = TicketRating.objects.filter(tenant=request.user.tenant)
        elif data.get('rating_type') == 'agent':
            ratings = AgentRating.objects.filter(tenant=request.user.tenant)
        elif data.get('rating_type') == 'service':
            ratings = ServiceRating.objects.filter(tenant=request.user.tenant)
        
        if data.get('min_rating'):
            ratings = ratings.filter(rating__gte=data['min_rating'])
        
        if data.get('max_rating'):
            ratings = ratings.filter(rating__lte=data['max_rating'])
        
        if data.get('date_from'):
            ratings = ratings.filter(created_at__gte=data['date_from'])
        
        if data.get('date_to'):
            ratings = ratings.filter(created_at__lte=data['date_to'])
        
        # Сортировка
        ratings = ratings.order_by('-created_at')
        
        # Пагинация
        paginator = PageNumberPagination()
        paginated_ratings = paginator.paginate_queryset(ratings, request)
        
        # Выбираем сериализатор в зависимости от типа
        if data.get('rating_type') == 'agent':
            serializer = AgentRatingSerializer(paginated_ratings, many=True)
        elif data.get('rating_type') == 'service':
            serializer = ServiceRatingSerializer(paginated_ratings, many=True)
        else:
            serializer = TicketRatingSerializer(paginated_ratings, many=True)
        
        return paginator.get_paginated_response(serializer.data)
