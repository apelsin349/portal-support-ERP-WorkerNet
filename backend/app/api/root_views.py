"""
API-представления (views) портала WorkerNet.
Содержит ViewSet'ы для тикетов, базы знаний, пользователей и арендаторов.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from django.utils import timezone
from django.conf import settings

from app.models.ticket import Ticket, TicketComment, TicketAttachment
from app.models.tenant import User, Tenant
from .serializers import (
    TicketSerializer,
    TicketCommentSerializer,
    TicketAttachmentSerializer,
    UserSerializer,
    TenantSerializer,
    # Добавляем, т.к. используются ниже
    KnowledgeArticleSerializer,
    KnowledgeCategorySerializer,
)


class TicketViewSet(viewsets.ModelViewSet):
    """Управление тикетами службы поддержки."""
    
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'priority', 'category', 'assigned_to']
    search_fields = ['title', 'description', 'ticket_id']
    ordering_fields = ['created_at', 'updated_at', 'priority', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фильтрация тикетов по текущему арендатору пользователя."""
        return Ticket.objects.filter(tenant=self.request.user.tenant)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Добавить комментарий к тикету."""
        ticket = self.get_object()
        serializer = TicketCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ticket=ticket, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_attachment(self, request, pk=None):
        """Добавить вложение к тикету."""
        ticket = self.get_object()
        serializer = TicketAttachmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ticket=ticket, uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Назначить тикет пользователю."""
        ticket = self.get_object()
        user_id = request.data.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id, tenant=request.user.tenant)
                ticket.assigned_to = user
                ticket.save()
                return Response({'message': 'Ticket assigned successfully'})
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Закрыть тикет."""
        ticket = self.get_object()
        ticket.status = 'closed'
        ticket.save()
        return Response({'message': 'Ticket closed successfully'})
    
    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """Переоткрыть тикет."""
        ticket = self.get_object()
        ticket.status = 'open'
        ticket.save()
        return Response({'message': 'Ticket reopened successfully'})


class KnowledgeArticleViewSet(viewsets.ModelViewSet):
    """Управление статьями базы знаний."""
    
    serializer_class = KnowledgeArticleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'category', 'author']
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['created_at', 'updated_at', 'view_count', 'helpful_count']
    ordering = ['-published_at', '-created_at']
    
    def get_queryset(self):
        """Фильтрация статей по арендатору и статусу публикации."""
        queryset = KnowledgeArticle.objects.filter(tenant=self.request.user.tenant)
        if self.action == 'list':
            # Only show published articles in list view
            queryset = queryset.filter(status='published')
        return queryset
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Оценить статью базы знаний."""
        article = self.get_object()
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        
        if not rating or not 1 <= int(rating) <= 5:
            return Response({'error': 'Rating must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update or create rating
        from app.models.knowledge import KnowledgeArticleRating
        rating_obj, created = KnowledgeArticleRating.objects.get_or_create(
            article=article,
            user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )
        
        if not created:
            rating_obj.rating = rating
            rating_obj.comment = comment
            rating_obj.save()
        
        # Update article helpful count
        article.helpful_count = article.ratings.filter(rating__gte=4).count()
        article.not_helpful_count = article.ratings.filter(rating__lte=2).count()
        article.save()
        
        return Response({'message': 'Rating saved successfully'})
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Отметить просмотр статьи."""
        article = self.get_object()
        
        # Create view record
        from app.models.knowledge import KnowledgeArticleView
        KnowledgeArticleView.objects.create(
            article=article,
            user=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Update view count
        article.view_count += 1
        article.save()
        
        return Response({'message': 'View tracked successfully'})


class KnowledgeCategoryViewSet(viewsets.ModelViewSet):
    """Управление категориями базы знаний."""
    
    serializer_class = KnowledgeCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'order', 'created_at']
    ordering = ['order', 'name']
    
    def get_queryset(self):
        """Фильтрация категорий по арендатору."""
        return KnowledgeCategory.objects.filter(tenant=self.request.user.tenant)


class UserViewSet(viewsets.ModelViewSet):
    """Управление пользователями арендатора."""
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'department', 'position']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'first_name', 'last_name', 'date_joined']
    ordering = ['username']
    
    def get_queryset(self):
        """Фильтрация пользователей по арендатору."""
        return User.objects.filter(tenant=self.request.user.tenant)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получить профиль текущего пользователя."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put'])
    def update_me(self, request):
        """Обновить профиль текущего пользователя."""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TenantViewSet(viewsets.ModelViewSet):
    """Управление арендаторами (тенантами)."""
    
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'domain']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Ограничить список до арендатора текущего пользователя."""
        return Tenant.objects.filter(id=self.request.user.tenant.id)
    
    @action(detail=True, methods=['get'])
    def configuration(self, request, pk=None):
        """Получить конфигурацию арендатора (настройки)."""
        tenant = self.get_object()
        config = tenant.configuration
        return Response({
            'timezone': config.timezone,
            'language': config.language,
            'date_format': config.date_format,
            'time_format': config.time_format,
            'ticket_settings': {
                'auto_assign_tickets': config.auto_assign_tickets,
                'priority_levels': config.ticket_priority_levels,
                'categories': config.ticket_categories,
            },
            'sla_settings': {
                'default_sla_hours': config.default_sla_hours,
                'escalation_rules': config.escalation_rules,
            },
            'notification_settings': {
                'email_notifications': config.email_notifications,
                'sms_notifications': config.sms_notifications,
                'push_notifications': config.push_notifications,
            },
            'security_settings': {
                'password_policy': config.password_policy,
                'session_timeout': config.session_timeout,
                'two_factor_required': config.two_factor_required,
            },
            'integration_settings': {
                'ldap_enabled': config.ldap_enabled,
                'ldap_config': config.ldap_config,
                'sso_enabled': config.sso_enabled,
                'sso_config': config.sso_config,
            },
            'custom_fields': config.custom_fields,
        })


class HealthView(APIView):
    """Проверка состояния сервисов (health check)."""
    
    def get(self, request):
        """Вернуть сводку состояния сервисов системы."""
        from django.db import connection
        from django.core.cache import cache
        import redis
        
        health_data = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'services': {}
        }
        
        # Check database
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_data['services']['database'] = {'status': 'healthy'}
        except Exception as e:
            health_data['services']['database'] = {'status': 'unhealthy', 'error': str(e)}
            health_data['status'] = 'unhealthy'
        
        # Check cache
        try:
            cache.set('health_check', 'ok', 10)
            cache.get('health_check')
            health_data['services']['cache'] = {'status': 'healthy'}
        except Exception as e:
            health_data['services']['cache'] = {'status': 'unhealthy', 'error': str(e)}
            health_data['status'] = 'unhealthy'
        
        # Check Redis
        try:
            r = redis.Redis.from_url(settings.REDIS_URL)
            r.ping()
            health_data['services']['redis'] = {'status': 'healthy'}
        except Exception as e:
            health_data['services']['redis'] = {'status': 'unhealthy', 'error': str(e)}
            health_data['status'] = 'unhealthy'
        
        return Response(health_data)


