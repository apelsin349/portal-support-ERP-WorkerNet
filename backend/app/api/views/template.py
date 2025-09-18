"""
Представления для шаблонов ответов.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Max
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
import re

from app.models import (
    ResponseTemplate, TemplateVariable, TemplateUsage, TemplateCategory,
    TemplateVersion
)
from app.api.serializers.template import (
    ResponseTemplateListSerializer, ResponseTemplateDetailSerializer,
    ResponseTemplateCreateSerializer, ResponseTemplateUpdateSerializer,
    TemplateVariableSerializer, TemplateCategorySerializer,
    TemplateVersionSerializer, TemplateUsageSerializer,
    TemplateUsageCreateSerializer, TemplateSearchSerializer,
    TemplateStatsSerializer, TemplateReportSerializer,
    TemplatePreviewSerializer
)

User = get_user_model()


class ResponseTemplateViewSet(viewsets.ModelViewSet):
    """Управление шаблонами ответов."""
    
    queryset = ResponseTemplate.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'author', 'is_active']
    search_fields = ['name', 'description', 'content', 'tags']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'list':
            return ResponseTemplateListSerializer
        elif self.action == 'create':
            return ResponseTemplateCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ResponseTemplateUpdateSerializer
        else:
            return ResponseTemplateDetailSerializer
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Использование шаблона."""
        template = self.get_object()
        serializer = TemplateUsageCreateSerializer(
            data=request.data,
            context={'request': request, 'template': template}
        )
        
        if serializer.is_valid():
            usage = serializer.save()
            return Response({
                'message': 'Шаблон использован',
                'usage_id': usage.id
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def preview(self, request, pk=None):
        """Предварительный просмотр шаблона с переменными."""
        template = self.get_object()
        variables = request.data.get('variables', {})
        
        # Заменяем переменные в контенте
        content = template.content
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            content = content.replace(placeholder, str(var_value))
        
        return Response({
            'template_id': template.id,
            'template_name': template.name,
            'preview_content': content,
            'variables_used': variables
        })
    
    @action(detail=True, methods=['post'])
    def create_version(self, request, pk=None):
        """Создание новой версии шаблона."""
        template = self.get_object()
        content = request.data.get('content')
        change_log = request.data.get('change_log', 'Новая версия')
        
        if not content:
            return Response(
                {'error': 'Содержимое шаблона обязательно'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Создаем новую версию
        version = TemplateVersion.objects.create(
            template=template,
            version_number=template.versions.count() + 1,
            content=content,
            author=request.user,
            change_log=change_log,
            tenant=request.user.tenant
        )
        
        # Обновляем основной контент шаблона
        template.content = content
        template.save(update_fields=['content'])
        
        return Response({
            'message': 'Новая версия создана',
            'version_id': version.id,
            'version_number': version.version_number
        })
    
    @action(detail=True, methods=['get'])
    def variables(self, request, pk=None):
        """Получение переменных шаблона."""
        template = self.get_object()
        variables = template.variables.all()
        serializer = TemplateVariableSerializer(variables, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Получение версий шаблона."""
        template = self.get_object()
        versions = template.versions.all().order_by('-version_number')
        serializer = TemplateVersionSerializer(versions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def usage_history(self, request, pk=None):
        """История использования шаблона."""
        template = self.get_object()
        usage = template.usage.all().order_by('-used_at')
        
        # Пагинация
        paginator = PageNumberPagination()
        paginated_usage = paginator.paginate_queryset(usage, request)
        
        serializer = TemplateUsageSerializer(paginated_usage, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Поиск шаблонов."""
        serializer = TemplateSearchSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        query = data['query']
        
        # Базовый запрос
        templates = self.get_queryset()
        
        # Поиск по тексту
        if query:
            templates = templates.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__icontains=query)
            )
        
        # Фильтры
        if data.get('category'):
            templates = templates.filter(category=data['category'])
        
        if data.get('author'):
            templates = templates.filter(author=data['author'])
        
        if data.get('tags'):
            tags = [tag.strip() for tag in data['tags'].split(',')]
            for tag in tags:
                templates = templates.filter(tags__icontains=tag)
        
        if data.get('is_active') is not None:
            templates = templates.filter(is_active=data['is_active'])
        
        # Сортировка
        templates = templates.order_by('-created_at')
        
        # Пагинация
        paginator = PageNumberPagination()
        paginated_templates = paginator.paginate_queryset(templates, request)
        
        serializer = ResponseTemplateListSerializer(paginated_templates, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика шаблонов."""
        tenant = request.user.tenant
        
        # Общая статистика
        total_templates = ResponseTemplate.objects.filter(tenant=tenant).count()
        active_templates = ResponseTemplate.objects.filter(tenant=tenant, is_active=True).count()
        inactive_templates = total_templates - active_templates
        
        # Статистика по категориям
        templates_by_category = ResponseTemplate.objects.filter(tenant=tenant).values(
            'category__name'
        ).annotate(count=Count('id')).order_by('-count')
        
        # Статистика по авторам
        templates_by_author = ResponseTemplate.objects.filter(tenant=tenant).values(
            'author__first_name', 'author__last_name'
        ).annotate(count=Count('id')).order_by('-count')
        
        # Самые используемые шаблоны
        most_used_templates = ResponseTemplate.objects.filter(tenant=tenant).annotate(
            usage_count=Count('usage')
        ).order_by('-usage_count')[:10]
        
        # Недавние шаблоны
        recent_templates = ResponseTemplate.objects.filter(tenant=tenant).order_by('-created_at')[:10]
        
        # Статистика использования
        usage_stats = {
            'total_usage': TemplateUsage.objects.filter(template__tenant=tenant).count(),
            'usage_today': TemplateUsage.objects.filter(
                template__tenant=tenant,
                used_at__date=timezone.now().date()
            ).count(),
            'usage_this_week': TemplateUsage.objects.filter(
                template__tenant=tenant,
                used_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
        }
        
        stats_data = {
            'total_templates': total_templates,
            'active_templates': active_templates,
            'inactive_templates': inactive_templates,
            'templates_by_category': dict(templates_by_category),
            'templates_by_author': dict(templates_by_author),
            'most_used_templates': ResponseTemplateListSerializer(most_used_templates, many=True).data,
            'recent_templates': ResponseTemplateListSerializer(recent_templates, many=True).data,
            'usage_stats': usage_stats,
        }
        
        serializer = TemplateStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """Отчет по шаблонам."""
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
        
        # Общая статистика
        total_templates = ResponseTemplate.objects.filter(tenant=tenant).count()
        
        # Шаблоны, созданные в периоде
        templates_created = ResponseTemplate.objects.filter(
            tenant=tenant,
            created_at__date__range=[period_start, period_end]
        ).count()
        
        # Шаблоны, обновленные в периоде
        templates_updated = ResponseTemplate.objects.filter(
            tenant=tenant,
            updated_at__date__range=[period_start, period_end]
        ).count()
        
        # Использование в периоде
        usage_count = TemplateUsage.objects.filter(
            template__tenant=tenant,
            used_at__date__range=[period_start, period_end]
        ).count()
        
        # Использование по шаблонам
        usage_by_template = TemplateUsage.objects.filter(
            template__tenant=tenant,
            used_at__date__range=[period_start, period_end]
        ).values('template__name').annotate(count=Count('id')).order_by('-count')
        
        # Использование по пользователям
        usage_by_user = TemplateUsage.objects.filter(
            template__tenant=tenant,
            used_at__date__range=[period_start, period_end]
        ).values('user__first_name', 'user__last_name').annotate(count=Count('id')).order_by('-count')
        
        # Топ шаблоны
        top_templates = ResponseTemplate.objects.filter(tenant=tenant).annotate(
            usage_count=Count('usage', filter=Q(
                usage__used_at__date__range=[period_start, period_end]
            ))
        ).order_by('-usage_count')[:10]
        
        # Рекомендации
        recommendations = []
        
        if usage_count == 0:
            recommendations.append("Нет использования шаблонов в периоде. Рассмотрите обучение пользователей")
        
        if templates_created > templates_updated:
            recommendations.append("Создается больше шаблонов, чем обновляется. Рассмотрите улучшение существующих")
        
        if not recommendations:
            recommendations.append("Показатели в норме. Продолжайте текущую работу")
        
        report_data = {
            'period_start': period_start,
            'period_end': period_end,
            'total_templates': total_templates,
            'templates_created': templates_created,
            'templates_updated': templates_updated,
            'usage_count': usage_count,
            'usage_by_template': dict(usage_by_template),
            'usage_by_user': dict(usage_by_user),
            'top_templates': ResponseTemplateListSerializer(top_templates, many=True).data,
            'recommendations': recommendations,
        }
        
        serializer = TemplateReportSerializer(report_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_templates(self, request):
        """Шаблоны текущего пользователя."""
        user = request.user
        templates = self.get_queryset().filter(author=user)
        serializer = ResponseTemplateListSerializer(templates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Популярные шаблоны."""
        templates = self.get_queryset().annotate(
            usage_count=Count('usage')
        ).order_by('-usage_count')[:10]
        
        serializer = ResponseTemplateListSerializer(templates, many=True)
        return Response(serializer.data)


class TemplateCategoryViewSet(viewsets.ModelViewSet):
    """Управление категориями шаблонов."""
    
    queryset = TemplateCategory.objects.all()
    serializer_class = TemplateCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    @action(detail=True, methods=['get'])
    def templates(self, request, pk=None):
        """Шаблоны в категории."""
        category = self.get_object()
        templates = category.templates.filter(is_active=True)
        
        # Пагинация
        paginator = PageNumberPagination()
        paginated_templates = paginator.paginate_queryset(templates, request)
        
        serializer = ResponseTemplateListSerializer(paginated_templates, many=True)
        return paginator.get_paginated_response(serializer.data)


class TemplateVariableViewSet(viewsets.ModelViewSet):
    """Управление переменными шаблонов."""
    
    queryset = TemplateVariable.objects.all()
    serializer_class = TemplateVariableSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['variable_type', 'is_required']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
