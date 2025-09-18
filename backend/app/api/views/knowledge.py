"""
Представления для базы знаний.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from django.shortcuts import get_object_or_404

from app.models import (
    KnowledgeCategory, KnowledgeArticle, KnowledgeArticleAttachment,
    KnowledgeArticleRating, KnowledgeArticleView, KnowledgeSearch
)
from app.api.serializers.knowledge import (
    KnowledgeCategorySerializer, KnowledgeArticleListSerializer,
    KnowledgeArticleDetailSerializer, KnowledgeArticleCreateSerializer,
    KnowledgeArticleUpdateSerializer, KnowledgeArticleRatingSerializer,
    KnowledgeArticleRatingCreateSerializer, KnowledgeSearchSerializer,
    KnowledgeSearchRequestSerializer, KnowledgeStatsSerializer,
    KnowledgeCategoryTreeSerializer
)


class KnowledgeCategoryViewSet(viewsets.ModelViewSet):
    """Управление категориями базы знаний."""
    
    queryset = KnowledgeCategory.objects.all()
    serializer_class = KnowledgeCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'order', 'created_at']
    ordering = ['order', 'name']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Получение дерева категорий."""
        root_categories = self.get_queryset().filter(parent=None, is_active=True)
        serializer = KnowledgeCategoryTreeSerializer(root_categories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def articles(self, request, pk=None):
        """Получение статей в категории."""
        category = self.get_object()
        articles = category.articles.filter(status='published')
        
        # Фильтрация
        search = request.query_params.get('search')
        if search:
            articles = articles.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search) |
                Q(excerpt__icontains=search)
            )
        
        # Сортировка
        sort_by = request.query_params.get('sort', 'created_at')
        if sort_by == 'rating':
            articles = articles.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')
        elif sort_by == 'views':
            articles = articles.order_by('-view_count')
        elif sort_by == 'helpful':
            articles = articles.annotate(
                helpful_percentage=F('helpful_count') * 100.0 / (F('helpful_count') + F('not_helpful_count'))
            ).order_by('-helpful_percentage')
        else:
            articles = articles.order_by('-created_at')
        
        # Пагинация
        paginator = PageNumberPagination()
        paginated_articles = paginator.paginate_queryset(articles, request)
        
        serializer = KnowledgeArticleListSerializer(paginated_articles, many=True)
        return paginator.get_paginated_response(serializer.data)


class KnowledgeArticleViewSet(viewsets.ModelViewSet):
    """Управление статьями базы знаний."""
    
    queryset = KnowledgeArticle.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'author', 'status', 'tags']
    search_fields = ['title', 'content', 'excerpt', 'keywords']
    ordering_fields = ['title', 'created_at', 'updated_at', 'published_at', 'view_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'list':
            return KnowledgeArticleListSerializer
        elif self.action == 'create':
            return KnowledgeArticleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return KnowledgeArticleUpdateSerializer
        else:
            return KnowledgeArticleDetailSerializer
    
    def get_permissions(self):
        """Права доступа в зависимости от действия."""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def retrieve(self, request, *args, **kwargs):
        """Детальный просмотр статьи с увеличением счетчика просмотров."""
        instance = self.get_object()
        
        # Увеличиваем счетчик просмотров
        instance.view_count = F('view_count') + 1
        instance.save(update_fields=['view_count'])
        
        # Записываем просмотр
        if request.user.is_authenticated:
            KnowledgeArticleView.objects.create(
                article=instance,
                user=request.user,
                ip_address=request.META.get('REMOTE_ADDR')
            )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Оценка статьи."""
        article = self.get_object()
        
        # Проверяем, не оценивал ли уже пользователь
        existing_rating = article.ratings.filter(user=request.user).first()
        if existing_rating:
            return Response(
                {'error': 'Вы уже оценили эту статью'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = KnowledgeArticleRatingCreateSerializer(
            data=request.data,
            context={'request': request, 'article': article}
        )
        
        if serializer.is_valid():
            rating = serializer.save()
            
            # Обновляем счетчики статьи
            if rating.rating >= 4:
                article.helpful_count = F('helpful_count') + 1
            else:
                article.not_helpful_count = F('not_helpful_count') + 1
            article.save(update_fields=['helpful_count', 'not_helpful_count'])
            
            return Response(
                KnowledgeArticleRatingSerializer(rating).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def helpful(self, request, pk=None):
        """Отметка статьи как полезной."""
        article = self.get_object()
        is_helpful = request.data.get('helpful', True)
        
        if is_helpful:
            article.helpful_count = F('helpful_count') + 1
        else:
            article.not_helpful_count = F('not_helpful_count') + 1
        
        article.save(update_fields=['helpful_count', 'not_helpful_count'])
        
        return Response({'message': 'Спасибо за обратную связь!'})
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Рекомендуемые статьи."""
        articles = self.get_queryset().filter(
            status='published',
            featured=True
        ).order_by('-created_at')[:10]
        
        serializer = KnowledgeArticleListSerializer(articles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Популярные статьи."""
        articles = self.get_queryset().filter(
            status='published'
        ).annotate(
            helpful_percentage=F('helpful_count') * 100.0 / (F('helpful_count') + F('not_helpful_count'))
        ).order_by('-view_count', '-helpful_percentage')[:10]
        
        serializer = KnowledgeArticleListSerializer(articles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Недавние статьи."""
        articles = self.get_queryset().filter(
            status='published'
        ).order_by('-published_at')[:10]
        
        serializer = KnowledgeArticleListSerializer(articles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Поиск в базе знаний."""
        serializer = KnowledgeSearchRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        query = data['query']
        
        # Базовый запрос
        articles = self.get_queryset().filter(status='published')
        
        # Поиск по тексту
        if query:
            articles = articles.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(keywords__icontains=query)
            )
        
        # Фильтры
        if data.get('category'):
            articles = articles.filter(category=data['category'])
        
        if data.get('author'):
            articles = articles.filter(author=data['author'])
        
        if data.get('date_from'):
            articles = articles.filter(created_at__gte=data['date_from'])
        
        if data.get('date_to'):
            articles = articles.filter(created_at__lte=data['date_to'])
        
        if data.get('min_rating'):
            articles = articles.annotate(
                avg_rating=Avg('ratings__rating')
            ).filter(avg_rating__gte=data['min_rating'])
        
        # Сортировка
        sort_by = data.get('sort_by', 'relevance')
        if sort_by == 'date':
            articles = articles.order_by('-created_at')
        elif sort_by == 'rating':
            articles = articles.annotate(
                avg_rating=Avg('ratings__rating')
            ).order_by('-avg_rating')
        elif sort_by == 'views':
            articles = articles.order_by('-view_count')
        elif sort_by == 'helpful':
            articles = articles.annotate(
                helpful_percentage=F('helpful_count') * 100.0 / (F('helpful_count') + F('not_helpful_count'))
            ).order_by('-helpful_percentage')
        else:  # relevance
            articles = articles.order_by('-view_count', '-created_at')
        
        # Пагинация
        paginator = PageNumberPagination()
        paginated_articles = paginator.paginate_queryset(articles, request)
        
        # Сохраняем поисковый запрос
        if request.user.is_authenticated:
            KnowledgeSearch.objects.create(
                user=request.user,
                query=query,
                results_count=articles.count(),
                tenant=request.user.tenant
            )
        
        serializer = KnowledgeArticleListSerializer(paginated_articles, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика базы знаний."""
        tenant = request.user.tenant
        
        # Общая статистика
        total_articles = KnowledgeArticle.objects.filter(tenant=tenant).count()
        published_articles = KnowledgeArticle.objects.filter(tenant=tenant, status='published').count()
        draft_articles = KnowledgeArticle.objects.filter(tenant=tenant, status='draft').count()
        archived_articles = KnowledgeArticle.objects.filter(tenant=tenant, status='archived').count()
        
        total_categories = KnowledgeCategory.objects.filter(tenant=tenant).count()
        active_categories = KnowledgeCategory.objects.filter(tenant=tenant, is_active=True).count()
        
        # Статистика просмотров и оценок
        total_views = KnowledgeArticle.objects.filter(tenant=tenant).aggregate(
            total=Count('view_count')
        )['total'] or 0
        
        total_ratings = KnowledgeArticleRating.objects.filter(
            article__tenant=tenant
        ).count()
        
        average_rating = KnowledgeArticleRating.objects.filter(
            article__tenant=tenant
        ).aggregate(avg=Avg('rating'))['avg'] or 0
        
        # Топ статьи
        most_viewed = KnowledgeArticle.objects.filter(
            tenant=tenant, status='published'
        ).order_by('-view_count')[:5]
        
        most_rated = KnowledgeArticle.objects.filter(
            tenant=tenant, status='published'
        ).annotate(
            avg_rating=Avg('ratings__rating'),
            ratings_count=Count('ratings')
        ).filter(ratings_count__gt=0).order_by('-avg_rating')[:5]
        
        most_helpful = KnowledgeArticle.objects.filter(
            tenant=tenant, status='published'
        ).annotate(
            helpful_percentage=F('helpful_count') * 100.0 / (F('helpful_count') + F('not_helpful_count'))
        ).order_by('-helpful_percentage')[:5]
        
        # Недавние статьи и поиски
        recent_articles = KnowledgeArticle.objects.filter(
            tenant=tenant, status='published'
        ).order_by('-created_at')[:5]
        
        recent_searches = KnowledgeSearch.objects.filter(
            tenant=tenant
        ).order_by('-searched_at')[:10]
        
        stats_data = {
            'total_articles': total_articles,
            'published_articles': published_articles,
            'draft_articles': draft_articles,
            'archived_articles': archived_articles,
            'total_categories': total_categories,
            'active_categories': active_categories,
            'total_views': total_views,
            'total_ratings': total_ratings,
            'average_rating': round(average_rating, 2),
            'most_viewed_articles': KnowledgeArticleListSerializer(most_viewed, many=True).data,
            'most_rated_articles': KnowledgeArticleListSerializer(most_rated, many=True).data,
            'most_helpful_articles': KnowledgeArticleListSerializer(most_helpful, many=True).data,
            'recent_articles': KnowledgeArticleListSerializer(recent_articles, many=True).data,
            'recent_searches': KnowledgeSearchSerializer(recent_searches, many=True).data,
        }
        
        serializer = KnowledgeStatsSerializer(stats_data)
        return Response(serializer.data)


class KnowledgeArticleRatingViewSet(viewsets.ModelViewSet):
    """Управление оценками статей."""
    
    queryset = KnowledgeArticleRating.objects.all()
    serializer_class = KnowledgeArticleRatingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['article', 'rating']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(article__tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return KnowledgeArticleRatingCreateSerializer
        return KnowledgeArticleRatingSerializer
    
    def perform_create(self, serializer):
        """Создание оценки."""
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """Обновление оценки."""
        serializer.save(user=self.request.user)
