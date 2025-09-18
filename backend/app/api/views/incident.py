"""
Представления для управления инцидентами.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, F, Max
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from app.models import (
    Incident, IncidentUpdate, IncidentAttachment, IncidentTimeline,
    IncidentEscalation, IncidentSLA
)
from app.api.serializers.incident import (
    IncidentListSerializer, IncidentDetailSerializer, IncidentCreateSerializer,
    IncidentUpdateSerializer, IncidentUpdateCreateSerializer,
    IncidentAttachmentSerializer, IncidentTimelineSerializer,
    IncidentEscalationSerializer, IncidentEscalationCreateSerializer,
    IncidentSLASerializer, IncidentStatsSerializer, IncidentReportSerializer,
    IncidentSearchSerializer
)

User = get_user_model()


class IncidentViewSet(viewsets.ModelViewSet):
    """Управление инцидентами."""
    
    queryset = Incident.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['severity', 'status', 'category', 'reported_by', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['detected_at', 'resolved_at', 'created_at', 'severity']
    ordering = ['-detected_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'list':
            return IncidentListSerializer
        elif self.action == 'create':
            return IncidentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return IncidentUpdateSerializer
        else:
            return IncidentDetailSerializer
    
    def perform_create(self, serializer):
        """Создание инцидента."""
        incident = serializer.save()
        
        # Создаем запись в временной шкале
        IncidentTimeline.objects.create(
            incident=incident,
            author=self.request.user,
            event_type='created',
            description='Инцидент создан',
            metadata={},
        )
    
    def perform_update(self, serializer):
        """Обновление инцидента."""
        old_instance = self.get_object()
        incident = serializer.save()
        
        # Создаем запись в временной шкале для изменений
        changes = []
        for field in ['title', 'description', 'severity', 'status', 'category', 'assigned_to']:
            old_value = getattr(old_instance, field)
            new_value = getattr(incident, field)
            if old_value != new_value:
                changes.append(f"{field}: {old_value} → {new_value}")
        
        if changes:
            IncidentTimeline.objects.create(
                incident=incident,
                author=self.request.user,
                event_type='status_changed',
                description=f"Инцидент обновлен: {', '.join(changes)}",
                metadata={},
            )
    
    @action(detail=True, methods=['post'])
    def add_update(self, request, pk=None):
        """Добавление обновления к инциденту."""
        incident = self.get_object()
        serializer = IncidentUpdateCreateSerializer(
            data=request.data,
            context={'request': request, 'incident': incident}
        )
        
        if serializer.is_valid():
            update = serializer.save()
            
            # Создаем запись в временной шкале
            IncidentTimeline.objects.create(
                incident=incident,
                author=request.user,
                event_type='created',
                description=f"Добавлено обновление: {update.title}",
                metadata={},
            )
            
            return Response(
                IncidentUpdateSerializer(update).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        """Эскалация инцидента."""
        incident = self.get_object()
        serializer = IncidentEscalationCreateSerializer(
            data=request.data,
            context={'request': request, 'incident': incident}
        )
        
        if serializer.is_valid():
            escalation = serializer.save()
            
            # Создаем запись в временной шкале
            IncidentTimeline.objects.create(
                incident=incident,
                user=request.user,
                action='escalated',
                description=f"Инцидент эскалирован: {escalation.reason}",
                tenant=request.user.tenant
            )
            
            return Response(
                IncidentEscalationSerializer(escalation).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Назначение инцидента пользователю."""
        incident = self.get_object()
        assignee_id = request.data.get('assignee_id')
        
        if not assignee_id:
            return Response(
                {'error': 'assignee_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            assignee = User.objects.get(id=assignee_id, tenant=request.user.tenant)
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        old_assignee = incident.assigned_to
        incident.assigned_to = assignee
        incident.save(update_fields=['assigned_to'])
        
        # Создаем запись в временной шкале
        IncidentTimeline.objects.create(
            incident=incident,
            author=request.user,
            event_type='assigned',
            description=f"Инцидент назначен: {old_assignee} → {assignee}",
            metadata={},
        )
        
        return Response({'message': 'Инцидент назначен'})
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Решение инцидента."""
        incident = self.get_object()
        
        if incident.status == 'resolved':
            return Response(
                {'error': 'Инцидент уже решен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        incident.status = 'resolved'
        incident.resolved_at = timezone.now()
        incident.save(update_fields=['status', 'resolved_at'])
        
        # Создаем запись в временной шкале
        IncidentTimeline.objects.create(
            incident=incident,
            author=request.user,
            event_type='resolved',
            description='Инцидент решен',
            metadata={},
        )
        
        return Response({'message': 'Инцидент решен'})
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Закрытие инцидента."""
        incident = self.get_object()
        
        if incident.status == 'closed':
            return Response(
                {'error': 'Инцидент уже закрыт'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        incident.status = 'closed'
        incident.save(update_fields=['status'])
        
        # Создаем запись в временной шкале
        IncidentTimeline.objects.create(
            incident=incident,
            author=request.user,
            event_type='closed',
            description='Инцидент закрыт',
            metadata={},
        )
        
        return Response({'message': 'Инцидент закрыт'})
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Поиск инцидентов."""
        serializer = IncidentSearchSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        query = data['query']
        
        # Базовый запрос
        incidents = self.get_queryset()
        
        # Поиск по тексту
        if query:
            incidents = incidents.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        
        # Фильтры
        if data.get('severity'):
            incidents = incidents.filter(severity=data['severity'])
        
        if data.get('status'):
            incidents = incidents.filter(status=data['status'])
        
        if data.get('category'):
            incidents = incidents.filter(category=data['category'])
        
        if data.get('assignee'):
            incidents = incidents.filter(assigned_to=data['assignee'])
        
        if data.get('reporter'):
            incidents = incidents.filter(reported_by=data['reporter'])
        
        if data.get('date_from'):
            incidents = incidents.filter(detected_at__gte=data['date_from'])
        
        if data.get('date_to'):
            incidents = incidents.filter(detected_at__lte=data['date_to'])
        
        # Сортировка
        incidents = incidents.order_by('-detected_at')
        
        # Пагинация
        paginator = PageNumberPagination()
        paginated_incidents = paginator.paginate_queryset(incidents, request)
        
        serializer = IncidentListSerializer(paginated_incidents, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика инцидентов."""
        tenant = request.user.tenant
        
        # Общая статистика
        total_incidents = Incident.objects.filter(tenant=tenant).count()
        open_incidents = Incident.objects.filter(tenant=tenant, status='open').count()
        resolved_incidents = Incident.objects.filter(tenant=tenant, status='resolved').count()
        closed_incidents = Incident.objects.filter(tenant=tenant, status='closed').count()
        
        # Статистика по серьезности
        incidents_by_severity = Incident.objects.filter(tenant=tenant).values(
            'severity'
        ).annotate(count=Count('id')).order_by('-count')
        
        # Статистика по статусу
        incidents_by_status = Incident.objects.filter(tenant=tenant).values(
            'status'
        ).annotate(count=Count('id')).order_by('-count')
        
        # Статистика по приоритету
        incidents_by_category = Incident.objects.filter(tenant=tenant).values(
            'category'
        ).annotate(count=Count('id')).order_by('-count')
        
        # Среднее время решения
        resolved_incidents_with_time = Incident.objects.filter(
            tenant=tenant,
            status='resolved',
            resolved_at__isnull=False
        )
        
        average_resolution_time = 0
        if resolved_incidents_with_time.exists():
            total_time = 0
            for incident in resolved_incidents_with_time:
                time_diff = incident.resolved_at - incident.detected_at
                total_time += time_diff.total_seconds() / 3600  # в часах
            average_resolution_time = total_time / resolved_incidents_with_time.count()
        
        # Время решения по серьезности
        resolution_time_by_severity = {}
        for severity, _ in Incident.SEVERITY_CHOICES:
            incidents = resolved_incidents_with_time.filter(severity=severity)
            if incidents.exists():
                total_time = 0
                for incident in incidents:
                    time_diff = incident.resolved_at - incident.detected_at
                    total_time += time_diff.total_seconds() / 3600
                resolution_time_by_severity[severity] = total_time / incidents.count()
            else:
                resolution_time_by_severity[severity] = 0
        
        # Топ исполнителей
        top_assignees = Incident.objects.filter(
            tenant=tenant,
            assignee__isnull=False
        ).values('assignee__first_name', 'assignee__last_name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Недавние инциденты
        recent_incidents = Incident.objects.filter(
            tenant=tenant
        ).order_by('-detected_at')[:10]
        
        stats_data = {
            'total_incidents': total_incidents,
            'open_incidents': open_incidents,
            'resolved_incidents': resolved_incidents,
            'closed_incidents': closed_incidents,
            'incidents_by_severity': dict(incidents_by_severity),
            'incidents_by_status': dict(incidents_by_status),
            'incidents_by_category': dict(incidents_by_category),
            'average_resolution_time': round(average_resolution_time, 2),
            'resolution_time_by_severity': resolution_time_by_severity,
            'top_assignees': list(top_assignees),
            'recent_incidents': IncidentListSerializer(recent_incidents, many=True).data,
        }
        
        serializer = IncidentStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """Отчет по инцидентам."""
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
        
        # Фильтруем инциденты по периоду
        incidents = Incident.objects.filter(
            tenant=tenant,
            detected_at__date__range=[period_start, period_end]
        )
        
        # Общая статистика
        total_incidents = incidents.count()
        
        # Статистика по серьезности
        incidents_by_severity = incidents.values('severity').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Статистика по статусу
        incidents_by_status = incidents.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Время решения
        resolved_incidents = incidents.filter(
            status='resolved',
            resolved_at__isnull=False
        )
        
        resolution_times = {}
        if resolved_incidents.exists():
            total_time = 0
            for incident in resolved_incidents:
                time_diff = incident.resolved_at - incident.detected_at
                total_time += time_diff.total_seconds() / 3600
            resolution_times['average'] = total_time / resolved_incidents.count()
        else:
            resolution_times['average'] = 0
        
        # Количество эскалаций
        escalation_count = IncidentEscalation.objects.filter(
            incident__tenant=tenant,
            escalated_at__date__range=[period_start, period_end]
        ).count()
        
        # Топ инциденты
        top_incidents = incidents.order_by('-detected_at')[:10]
        
        # Рекомендации
        recommendations = []
        
        if escalation_count > total_incidents * 0.2:
            recommendations.append("Высокий уровень эскалаций. Рассмотрите улучшение процессов")
        
        if resolution_times['average'] > 24:
            recommendations.append("Длительное время решения. Увеличьте ресурсы или улучшите процессы")
        
        if not recommendations:
            recommendations.append("Показатели в норме. Продолжайте текущую работу")
        
        report_data = {
            'period_start': period_start,
            'period_end': period_end,
            'total_incidents': total_incidents,
            'incidents_by_severity': dict(incidents_by_severity),
            'incidents_by_status': dict(incidents_by_status),
            'resolution_times': resolution_times,
            'escalation_count': escalation_count,
            'top_incidents': IncidentListSerializer(top_incidents, many=True).data,
            'recommendations': recommendations,
        }
        
        serializer = IncidentReportSerializer(report_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_incidents(self, request):
        """Инциденты текущего пользователя."""
        user = request.user
        
        # Инциденты, где пользователь является репортером или исполнителем
        incidents = self.get_queryset().filter(
            Q(reported_by=user) | Q(assigned_to=user)
        ).order_by('-detected_at')
        
        serializer = IncidentListSerializer(incidents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def urgent(self, request):
        """Срочные инциденты."""
        incidents = self.get_queryset().filter(
            Q(severity__in=['P1', 'P2']) | Q(category='security'),
            status__in=['open', 'investigating']
        ).order_by('-detected_at')
        
        serializer = IncidentListSerializer(incidents, many=True)
        return Response(serializer.data)
