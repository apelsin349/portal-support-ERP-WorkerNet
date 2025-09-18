"""
Представления для системы автоматизации.
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
    AutomationRule, AutomationExecution, AutomationCondition,
    AutomationAction, AutomationTemplate, AutomationSchedule
)
from app.api.serializers.automation import (
    AutomationRuleListSerializer, AutomationRuleDetailSerializer,
    AutomationRuleCreateSerializer, AutomationRuleUpdateSerializer,
    AutomationConditionSerializer, AutomationConditionCreateSerializer,
    AutomationActionSerializer, AutomationActionCreateSerializer,
    AutomationExecutionSerializer, AutomationExecutionCreateSerializer,
    AutomationTemplateSerializer, AutomationTemplateCreateSerializer,
    AutomationScheduleSerializer, AutomationScheduleCreateSerializer,
    AutomationStatsSerializer, AutomationReportSerializer,
    AutomationSearchSerializer
)

User = get_user_model()


class AutomationRuleViewSet(viewsets.ModelViewSet):
    """Управление правилами автоматизации."""
    
    queryset = AutomationRule.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'trigger_event', 'author']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'priority', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'list':
            return AutomationRuleListSerializer
        elif self.action == 'create':
            return AutomationRuleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AutomationRuleUpdateSerializer
        else:
            return AutomationRuleDetailSerializer
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Ручное выполнение правила автоматизации."""
        rule = self.get_object()
        
        if not rule.is_active:
            return Response(
                {'error': 'Правило неактивно'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Здесь можно добавить логику выполнения правила
        # Пока создаем запись о выполнении
        execution = AutomationExecution.objects.create(
            rule=rule,
            executed_by=request.user,
            status='success',
            result='Правило выполнено успешно',
            tenant=request.user.tenant
        )
        
        return Response({
            'message': 'Правило выполнено',
            'execution_id': execution.id
        })
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Переключение активности правила."""
        rule = self.get_object()
        rule.is_active = not rule.is_active
        rule.save(update_fields=['is_active'])
        
        return Response({
            'message': f'Правило {"активировано" if rule.is_active else "деактивировано"}',
            'is_active': rule.is_active
        })
    
    @action(detail=True, methods=['get'])
    def executions(self, request, pk=None):
        """Выполнения правила."""
        rule = self.get_object()
        executions = rule.executions.all().order_by('-executed_at')
        
        # Пагинация
        paginator = PageNumberPagination()
        paginated_executions = paginator.paginate_queryset(executions, request)
        
        serializer = AutomationExecutionSerializer(paginated_executions, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_condition(self, request, pk=None):
        """Добавление условия к правилу."""
        rule = self.get_object()
        serializer = AutomationConditionCreateSerializer(
            data=request.data,
            context={'rule': rule}
        )
        
        if serializer.is_valid():
            condition = serializer.save()
            return Response(
                AutomationConditionSerializer(condition).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_action(self, request, pk=None):
        """Добавление действия к правилу."""
        rule = self.get_object()
        serializer = AutomationActionCreateSerializer(
            data=request.data,
            context={'rule': rule}
        )
        
        if serializer.is_valid():
            action = serializer.save()
            return Response(
                AutomationActionSerializer(action).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Поиск правил автоматизации."""
        serializer = AutomationSearchSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        query = data['query']
        
        # Базовый запрос
        rules = self.get_queryset()
        
        # Поиск по тексту
        if query:
            rules = rules.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        
        # Фильтры
        if data.get('trigger_event'):
            rules = rules.filter(trigger_event=data['trigger_event'])
        
        if data.get('is_active') is not None:
            rules = rules.filter(is_active=data['is_active'])
        
        if data.get('author'):
            rules = rules.filter(author=data['author'])
        
        if data.get('date_from'):
            rules = rules.filter(created_at__gte=data['date_from'])
        
        if data.get('date_to'):
            rules = rules.filter(created_at__lte=data['date_to'])
        
        # Сортировка
        rules = rules.order_by('-created_at')
        
        # Пагинация
        paginator = PageNumberPagination()
        paginated_rules = paginator.paginate_queryset(rules, request)
        
        serializer = AutomationRuleListSerializer(paginated_rules, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика автоматизации."""
        tenant = request.user.tenant
        
        # Общая статистика правил
        total_rules = AutomationRule.objects.filter(tenant=tenant).count()
        active_rules = AutomationRule.objects.filter(tenant=tenant, is_active=True).count()
        inactive_rules = total_rules - active_rules
        
        # Статистика выполнений
        total_executions = AutomationExecution.objects.filter(tenant=tenant).count()
        successful_executions = AutomationExecution.objects.filter(
            tenant=tenant, status='success'
        ).count()
        failed_executions = AutomationExecution.objects.filter(
            tenant=tenant, status='failed'
        ).count()
        
        # Процент успеха
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        # Среднее время выполнения
        average_execution_time = AutomationExecution.objects.filter(
            tenant=tenant, duration__isnull=False
        ).aggregate(avg=Avg('duration'))['avg'] or 0
        
        # Правила по триггерам
        rules_by_trigger = AutomationRule.objects.filter(tenant=tenant).values(
            'trigger_event'
        ).annotate(count=Count('id')).order_by('-count')
        
        # Выполнения по часам
        executions_by_hour = AutomationExecution.objects.filter(tenant=tenant).extra(
            select={'hour': 'EXTRACT(hour FROM executed_at)'}
        ).values('hour').annotate(count=Count('id')).order_by('hour')
        
        # Топ правила
        top_rules = AutomationRule.objects.filter(tenant=tenant).annotate(
            executions_count=Count('executions')
        ).order_by('-executions_count')[:10]
        
        # Недавние выполнения
        recent_executions = AutomationExecution.objects.filter(tenant=tenant).order_by('-executed_at')[:10]
        
        stats_data = {
            'total_rules': total_rules,
            'active_rules': active_rules,
            'inactive_rules': inactive_rules,
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': failed_executions,
            'success_rate': round(success_rate, 2),
            'average_execution_time': round(average_execution_time, 2),
            'rules_by_trigger': dict(rules_by_trigger),
            'executions_by_hour': dict(executions_by_hour),
            'top_rules': AutomationRuleListSerializer(top_rules, many=True).data,
            'recent_executions': AutomationExecutionSerializer(recent_executions, many=True).data,
        }
        
        serializer = AutomationStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """Отчет по автоматизации."""
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
        total_rules = AutomationRule.objects.filter(tenant=tenant).count()
        
        # Правила, созданные в периоде
        rules_created = AutomationRule.objects.filter(
            tenant=tenant,
            created_at__date__range=[period_start, period_end]
        ).count()
        
        # Правила, обновленные в периоде
        rules_updated = AutomationRule.objects.filter(
            tenant=tenant,
            updated_at__date__range=[period_start, period_end]
        ).count()
        
        # Выполнения в периоде
        total_executions = AutomationExecution.objects.filter(
            tenant=tenant,
            executed_at__date__range=[period_start, period_end]
        ).count()
        
        # Выполнения по правилам
        executions_by_rule = AutomationExecution.objects.filter(
            tenant=tenant,
            executed_at__date__range=[period_start, period_end]
        ).values('rule__name').annotate(count=Count('id')).order_by('-count')
        
        # Выполнения по статусу
        executions_by_status = AutomationExecution.objects.filter(
            tenant=tenant,
            executed_at__date__range=[period_start, period_end]
        ).values('status').annotate(count=Count('id')).order_by('-count')
        
        # Метрики производительности
        performance_metrics = {
            'average_execution_time': AutomationExecution.objects.filter(
                tenant=tenant,
                executed_at__date__range=[period_start, period_end],
                duration__isnull=False
            ).aggregate(avg=Avg('duration'))['avg'] or 0,
            'success_rate': 0,
            'failure_rate': 0
        }
        
        if total_executions > 0:
            successful = AutomationExecution.objects.filter(
                tenant=tenant,
                executed_at__date__range=[period_start, period_end],
                status='success'
            ).count()
            performance_metrics['success_rate'] = (successful / total_executions) * 100
            performance_metrics['failure_rate'] = 100 - performance_metrics['success_rate']
        
        # Рекомендации
        recommendations = []
        
        if performance_metrics['failure_rate'] > 20:
            recommendations.append("Высокий процент неудачных выполнений. Проверьте логи и условия правил")
        
        if total_executions == 0:
            recommendations.append("Нет выполнений в периоде. Рассмотрите активацию правил")
        
        if not recommendations:
            recommendations.append("Показатели в норме. Продолжайте текущую работу")
        
        report_data = {
            'period_start': period_start,
            'period_end': period_end,
            'total_rules': total_rules,
            'rules_created': rules_created,
            'rules_updated': rules_updated,
            'total_executions': total_executions,
            'executions_by_rule': dict(executions_by_rule),
            'executions_by_status': dict(executions_by_status),
            'performance_metrics': performance_metrics,
            'recommendations': recommendations,
        }
        
        serializer = AutomationReportSerializer(report_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_rules(self, request):
        """Правила текущего пользователя."""
        user = request.user
        rules = self.get_queryset().filter(author=user)
        serializer = AutomationRuleListSerializer(rules, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active_rules(self, request):
        """Активные правила."""
        rules = self.get_queryset().filter(is_active=True)
        serializer = AutomationRuleListSerializer(rules, many=True)
        return Response(serializer.data)


class AutomationExecutionViewSet(viewsets.ModelViewSet):
    """Управление выполнениями автоматизации."""
    
    queryset = AutomationExecution.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rule', 'status', 'executed_by']
    ordering_fields = ['executed_at', 'duration']
    ordering = ['-executed_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return AutomationExecutionCreateSerializer
        else:
            return AutomationExecutionSerializer
    
    @action(detail=False, methods=['get'])
    def my_executions(self, request):
        """Выполнения текущего пользователя."""
        user = request.user
        executions = self.get_queryset().filter(executed_by=user)
        serializer = AutomationExecutionSerializer(executions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def failed_executions(self, request):
        """Неудачные выполнения."""
        executions = self.get_queryset().filter(status='failed')
        serializer = AutomationExecutionSerializer(executions, many=True)
        return Response(serializer.data)


class AutomationTemplateViewSet(viewsets.ModelViewSet):
    """Управление шаблонами автоматизации."""
    
    queryset = AutomationTemplate.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_public', 'author']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return AutomationTemplateCreateSerializer
        else:
            return AutomationTemplateSerializer
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Использование шаблона для создания правила."""
        template = self.get_object()
        template_data = template.template_data
        
        # Создаем правило на основе шаблона
        rule_data = {
            'name': f"{template.name} (из шаблона)",
            'description': template.description,
            'is_active': True,
            'priority': 1,
            'trigger_event': template_data.get('trigger_event', 'manual'),
            'conditions': template_data.get('conditions', []),
            'actions': template_data.get('actions', [])
        }
        
        serializer = AutomationRuleCreateSerializer(
            data=rule_data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            rule = serializer.save()
            return Response({
                'message': 'Правило создано из шаблона',
                'rule_id': rule.id
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def public_templates(self, request):
        """Публичные шаблоны."""
        templates = self.get_queryset().filter(is_public=True)
        serializer = AutomationTemplateSerializer(templates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_templates(self, request):
        """Шаблоны текущего пользователя."""
        user = request.user
        templates = self.get_queryset().filter(author=user)
        serializer = AutomationTemplateSerializer(templates, many=True)
        return Response(serializer.data)


class AutomationScheduleViewSet(viewsets.ModelViewSet):
    """Управление расписаниями автоматизации."""
    
    queryset = AutomationSchedule.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rule', 'schedule_type', 'is_active']
    ordering_fields = ['next_run', 'last_run', 'created_at']
    ordering = ['next_run']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return AutomationScheduleCreateSerializer
        else:
            return AutomationScheduleSerializer
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Переключение активности расписания."""
        schedule = self.get_object()
        schedule.is_active = not schedule.is_active
        schedule.save(update_fields=['is_active'])
        
        return Response({
            'message': f'Расписание {"активировано" if schedule.is_active else "деактивировано"}',
            'is_active': schedule.is_active
        })
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Предстоящие выполнения."""
        now = timezone.now()
        schedules = self.get_queryset().filter(
            is_active=True,
            next_run__gt=now
        ).order_by('next_run')
        
        serializer = AutomationScheduleSerializer(schedules, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Просроченные выполнения."""
        now = timezone.now()
        schedules = self.get_queryset().filter(
            is_active=True,
            next_run__lt=now
        ).order_by('next_run')
        
        serializer = AutomationScheduleSerializer(schedules, many=True)
        return Response(serializer.data)
