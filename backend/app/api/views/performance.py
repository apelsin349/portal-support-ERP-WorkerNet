"""
Представления для системы мониторинга производительности.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, F, Max, Min
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from app.models import (
    PerformanceMetric, PerformanceAlert, PerformanceTrace,
    PerformanceDashboard, PerformanceReport, PerformanceThreshold
)
from app.api.serializers.performance import (
    PerformanceMetricSerializer, PerformanceMetricCreateSerializer,
    PerformanceAlertSerializer, PerformanceAlertCreateSerializer,
    PerformanceTraceSerializer, PerformanceTraceCreateSerializer,
    PerformanceDashboardSerializer, PerformanceDashboardCreateSerializer,
    PerformanceReportSerializer, PerformanceThresholdSerializer,
    PerformanceStatsSerializer, PerformanceReportDataSerializer,
    PerformanceSearchSerializer, PerformanceWidgetSerializer,
    PerformanceDashboardWidgetSerializer
)

User = get_user_model()


class PerformanceMetricViewSet(viewsets.ModelViewSet):
    """Управление метриками производительности."""
    
    queryset = PerformanceMetric.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'unit']
    search_fields = ['name', 'tags']
    ordering_fields = ['timestamp', 'value', 'created_at']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return PerformanceMetricCreateSerializer
        else:
            return PerformanceMetricSerializer
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Метрики по категории."""
        category = request.query_params.get('category')
        
        if not category:
            return Response(
                {'error': 'category обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        metrics = self.get_queryset().filter(category=category)
        serializer = PerformanceMetricSerializer(metrics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Последние метрики."""
        limit = int(request.query_params.get('limit', 100))
        metrics = self.get_queryset().order_by('-timestamp')[:limit]
        serializer = PerformanceMetricSerializer(metrics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def aggregated(self, request):
        """Агрегированные метрики."""
        metric_name = request.query_params.get('metric_name')
        period = request.query_params.get('period', 'hour')  # hour, day, week
        
        if not metric_name:
            return Response(
                {'error': 'metric_name обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Базовый запрос
        metrics = self.get_queryset().filter(name=metric_name)
        
        # Период
        now = timezone.now()
        if period == 'hour':
            start_time = now - timezone.timedelta(hours=1)
        elif period == 'day':
            start_time = now - timezone.timedelta(days=1)
        elif period == 'week':
            start_time = now - timezone.timedelta(weeks=1)
        else:
            start_time = now - timezone.timedelta(hours=1)
        
        metrics = metrics.filter(timestamp__gte=start_time)
        
        # Агрегация
        aggregated = metrics.aggregate(
            avg=Avg('value'),
            max=Max('value'),
            min=Min('value'),
            count=Count('id')
        )
        
        return Response({
            'metric_name': metric_name,
            'period': period,
            'aggregated': aggregated,
            'data_points': metrics.count()
        })
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Поиск метрик."""
        serializer = PerformanceSearchSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        query = data['query']
        
        # Базовый запрос
        metrics = self.get_queryset()
        
        # Поиск по тексту
        if query:
            metrics = metrics.filter(
                Q(name__icontains=query) | Q(tags__icontains=query)
            )
        
        # Фильтры
        if data.get('category'):
            metrics = metrics.filter(category=data['category'])
        
        if data.get('metric_name'):
            metrics = metrics.filter(name=data['metric_name'])
        
        if data.get('date_from'):
            metrics = metrics.filter(timestamp__gte=data['date_from'])
        
        if data.get('date_to'):
            metrics = metrics.filter(timestamp__lte=data['date_to'])
        
        # Сортировка
        metrics = metrics.order_by('-timestamp')
        
        # Пагинация
        paginator = PageNumberPagination()
        paginated_metrics = paginator.paginate_queryset(metrics, request)
        
        serializer = PerformanceMetricSerializer(paginated_metrics, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика метрик."""
        tenant = request.user.tenant
        
        # Общая статистика
        total_metrics = PerformanceMetric.objects.filter(tenant=tenant).count()
        active_alerts = PerformanceAlert.objects.filter(
            tenant=tenant, is_resolved=False
        ).count()
        resolved_alerts = PerformanceAlert.objects.filter(
            tenant=tenant, is_resolved=True
        ).count()
        
        # Метрики по категориям
        metrics_by_category = PerformanceMetric.objects.filter(tenant=tenant).values(
            'category'
        ).annotate(count=Count('id')).order_by('-count')
        
        # Алерты по серьезности
        alerts_by_severity = PerformanceAlert.objects.filter(tenant=tenant).values(
            'severity'
        ).annotate(count=Count('id')).order_by('-count')
        
        # Среднее время ответа
        response_time_metrics = PerformanceMetric.objects.filter(
            tenant=tenant, name='response_time'
        )
        average_response_time = response_time_metrics.aggregate(avg=Avg('value'))['avg'] or 0
        
        # Процент uptime
        uptime_metrics = PerformanceMetric.objects.filter(
            tenant=tenant, name='uptime'
        )
        uptime_percentage = uptime_metrics.aggregate(avg=Avg('value'))['avg'] or 0
        
        # Топ операции
        top_operations = PerformanceTrace.objects.filter(tenant=tenant).values(
            'operation'
        ).annotate(
            count=Count('id'),
            avg_duration=Avg('duration')
        ).order_by('-count')[:10]
        
        # Недавние метрики
        recent_metrics = PerformanceMetric.objects.filter(tenant=tenant).order_by('-timestamp')[:10]
        
        stats_data = {
            'total_metrics': total_metrics,
            'active_alerts': active_alerts,
            'resolved_alerts': resolved_alerts,
            'metrics_by_category': dict(metrics_by_category),
            'alerts_by_severity': dict(alerts_by_severity),
            'average_response_time': round(average_response_time, 2),
            'uptime_percentage': round(uptime_percentage, 2),
            'top_operations': list(top_operations),
            'recent_metrics': PerformanceMetricSerializer(recent_metrics, many=True).data,
        }
        
        serializer = PerformanceStatsSerializer(stats_data)
        return Response(serializer.data)


class PerformanceAlertViewSet(viewsets.ModelViewSet):
    """Управление алертами производительности."""
    
    queryset = PerformanceAlert.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['metric', 'severity', 'is_resolved']
    search_fields = ['message']
    ordering_fields = ['created_at', 'severity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return PerformanceAlertCreateSerializer
        else:
            return PerformanceAlertSerializer
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Решение алерта."""
        alert = self.get_object()
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save(update_fields=['is_resolved', 'resolved_at'])
        
        return Response({'message': 'Алерт решен'})
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Активные алерты."""
        alerts = self.get_queryset().filter(is_resolved=False)
        serializer = PerformanceAlertSerializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_severity(self, request):
        """Алерты по серьезности."""
        severity = request.query_params.get('severity')
        
        if not severity:
            return Response(
                {'error': 'severity обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        alerts = self.get_queryset().filter(severity=severity)
        serializer = PerformanceAlertSerializer(alerts, many=True)
        return Response(serializer.data)


class PerformanceTraceViewSet(viewsets.ModelViewSet):
    """Управление трейсами производительности."""
    
    queryset = PerformanceTrace.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['operation', 'status']
    search_fields = ['trace_id', 'operation']
    ordering_fields = ['start_time', 'duration', 'created_at']
    ordering = ['-start_time']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return PerformanceTraceCreateSerializer
        else:
            return PerformanceTraceSerializer
    
    @action(detail=False, methods=['get'])
    def by_operation(self, request):
        """Трейсы по операции."""
        operation = request.query_params.get('operation')
        
        if not operation:
            return Response(
                {'error': 'operation обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        traces = self.get_queryset().filter(operation=operation)
        serializer = PerformanceTraceSerializer(traces, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def slow_operations(self, request):
        """Медленные операции."""
        threshold = float(request.query_params.get('threshold', 1.0))  # секунды
        
        traces = self.get_queryset().filter(
            duration__gt=threshold
        ).order_by('-duration')
        
        serializer = PerformanceTraceSerializer(traces, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def failed_operations(self, request):
        """Неудачные операции."""
        traces = self.get_queryset().filter(status='failed')
        serializer = PerformanceTraceSerializer(traces, many=True)
        return Response(serializer.data)


class PerformanceDashboardViewSet(viewsets.ModelViewSet):
    """Управление дашбордами производительности."""
    
    queryset = PerformanceDashboard.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_public', 'author']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return PerformanceDashboardCreateSerializer
        else:
            return PerformanceDashboardSerializer
    
    @action(detail=True, methods=['post'])
    def add_widget(self, request, pk=None):
        """Добавление виджета к дашборду."""
        dashboard = self.get_object()
        serializer = PerformanceWidgetSerializer(data=request.data)
        
        if serializer.is_valid():
            widget_data = serializer.validated_data
            
            # Добавляем виджет к дашборду
            if not dashboard.widgets:
                dashboard.widgets = []
            
            dashboard.widgets.append(widget_data)
            dashboard.save(update_fields=['widgets'])
            
            return Response({
                'message': 'Виджет добавлен',
                'widgets_count': len(dashboard.widgets)
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def remove_widget(self, request, pk=None):
        """Удаление виджета из дашборда."""
        dashboard = self.get_object()
        widget_index = request.data.get('widget_index')
        
        if widget_index is None:
            return Response(
                {'error': 'widget_index обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not dashboard.widgets or widget_index >= len(dashboard.widgets):
            return Response(
                {'error': 'Неверный индекс виджета'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Удаляем виджет
        dashboard.widgets.pop(widget_index)
        dashboard.save(update_fields=['widgets'])
        
        return Response({
            'message': 'Виджет удален',
            'widgets_count': len(dashboard.widgets)
        })
    
    @action(detail=True, methods=['post'])
    def update_widgets(self, request, pk=None):
        """Обновление виджетов дашборда."""
        dashboard = self.get_object()
        serializer = PerformanceDashboardWidgetSerializer(data=request.data)
        
        if serializer.is_valid():
            dashboard.widgets = serializer.validated_data['widgets']
            dashboard.save(update_fields=['widgets'])
            
            return Response({
                'message': 'Виджеты обновлены',
                'widgets_count': len(dashboard.widgets)
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def public_dashboards(self, request):
        """Публичные дашборды."""
        dashboards = self.get_queryset().filter(is_public=True)
        serializer = PerformanceDashboardSerializer(dashboards, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_dashboards(self, request):
        """Дашборды текущего пользователя."""
        user = request.user
        dashboards = self.get_queryset().filter(author=user)
        serializer = PerformanceDashboardSerializer(dashboards, many=True)
        return Response(serializer.data)


class PerformanceReportViewSet(viewsets.ModelViewSet):
    """Управление отчетами производительности."""
    
    queryset = PerformanceReport.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'is_public', 'author']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return PerformanceReportSerializer
        else:
            return PerformanceReportSerializer
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Генерация отчета."""
        report = self.get_object()
        
        # Здесь можно добавить логику генерации отчета
        # Пока возвращаем базовую информацию
        return Response({
            'message': 'Отчет сгенерирован',
            'report_id': report.id,
            'data': report.data
        })
    
    @action(detail=False, methods=['get'])
    def my_reports(self, request):
        """Отчеты текущего пользователя."""
        user = request.user
        reports = self.get_queryset().filter(author=user)
        serializer = PerformanceReportSerializer(reports, many=True)
        return Response(serializer.data)


class PerformanceThresholdViewSet(viewsets.ModelViewSet):
    """Управление пороговыми значениями производительности."""
    
    queryset = PerformanceThreshold.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['metric_name', 'severity', 'is_active']
    search_fields = ['metric_name']
    ordering_fields = ['metric_name', 'threshold_value', 'created_at']
    ordering = ['metric_name']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return PerformanceThresholdSerializer
        else:
            return PerformanceThresholdSerializer
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Переключение активности порогового значения."""
        threshold = self.get_object()
        threshold.is_active = not threshold.is_active
        threshold.save(update_fields=['is_active'])
        
        return Response({
            'message': f'Пороговое значение {"активировано" if threshold.is_active else "деактивировано"}',
            'is_active': threshold.is_active
        })
    
    @action(detail=False, methods=['get'])
    def active_thresholds(self, request):
        """Активные пороговые значения."""
        thresholds = self.get_queryset().filter(is_active=True)
        serializer = PerformanceThresholdSerializer(thresholds, many=True)
        return Response(serializer.data)
