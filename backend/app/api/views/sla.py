"""
Представления для системы SLA.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, F, Case, When, IntegerField
from django.utils import timezone
from django.shortcuts import get_object_or_404

from app.models import SLA, TicketSLA, Ticket
from app.api.serializers.sla import (
    SLASerializer, SLACreateSerializer, TicketSLASerializer,
    TicketSLACreateSerializer, SLAStatsSerializer,
    SLAViolationSerializer, SLAReportSerializer
)


class SLAViewSet(viewsets.ModelViewSet):
    """Управление SLA."""
    
    queryset = SLA.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['priority', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'priority', 'response_time_hours', 'resolution_time_hours']
    ordering = ['priority', 'name']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return SLACreateSerializer
        else:
            return SLASerializer
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика SLA."""
        tenant = request.user.tenant
        
        # Общая статистика
        total_sla = SLA.objects.filter(tenant=tenant).count()
        active_sla = SLA.objects.filter(tenant=tenant, is_active=True).count()
        
        # Статистика по времени ответа
        response_time_met = TicketSLA.objects.filter(
            tenant=tenant,
            is_response_met=True
        ).count()
        
        response_time_missed = TicketSLA.objects.filter(
            tenant=tenant,
            is_response_met=False
        ).count()
        
        total_response = response_time_met + response_time_missed
        response_time_percentage = (response_time_met / total_response * 100) if total_response > 0 else 0
        
        # Статистика по времени решения
        resolution_time_met = TicketSLA.objects.filter(
            tenant=tenant,
            is_resolution_met=True
        ).count()
        
        resolution_time_missed = TicketSLA.objects.filter(
            tenant=tenant,
            is_resolution_met=False
        ).count()
        
        total_resolution = resolution_time_met + resolution_time_missed
        resolution_time_percentage = (resolution_time_met / total_resolution * 100) if total_resolution > 0 else 0
        
        # Средние времена
        average_response_time = TicketSLA.objects.filter(
            tenant=tenant,
            response_time_actual__isnull=False
        ).aggregate(avg=Avg('response_time_actual'))['avg'] or 0
        
        average_resolution_time = TicketSLA.objects.filter(
            tenant=tenant,
            resolution_time_actual__isnull=False
        ).aggregate(avg=Avg('resolution_time_actual'))['avg'] or 0
        
        # Производительность по SLA
        sla_performance = SLA.objects.filter(tenant=tenant).annotate(
            total_tickets=Count('ticket_sla'),
            met_response=Count('ticket_sla', filter=Q(ticket_sla__is_response_met=True)),
            met_resolution=Count('ticket_sla', filter=Q(ticket_sla__is_resolution_met=True))
        ).values('name', 'total_tickets', 'met_response', 'met_resolution')
        
        stats_data = {
            'total_sla': total_sla,
            'active_sla': active_sla,
            'response_time_met': response_time_met,
            'response_time_missed': response_time_missed,
            'response_time_percentage': round(response_time_percentage, 2),
            'resolution_time_met': resolution_time_met,
            'resolution_time_missed': resolution_time_missed,
            'resolution_time_percentage': round(resolution_time_percentage, 2),
            'average_response_time': round(average_response_time, 2),
            'average_resolution_time': round(average_resolution_time, 2),
            'sla_performance': list(sla_performance),
        }
        
        serializer = SLAStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def violations(self, request):
        """Нарушения SLA."""
        tenant = request.user.tenant
        
        # Нарушения времени ответа
        response_violations = TicketSLA.objects.filter(
            tenant=tenant,
            is_response_met=False,
            response_time_actual__isnull=False
        ).select_related('ticket', 'sla')
        
        # Нарушения времени решения
        resolution_violations = TicketSLA.objects.filter(
            tenant=tenant,
            is_resolution_met=False,
            resolution_time_actual__isnull=False
        ).select_related('ticket', 'sla')
        
        violations = []
        
        for violation in response_violations:
            delay_hours = (violation.response_time_actual - violation.response_deadline).total_seconds() / 3600
            violations.append({
                'ticket_id': violation.ticket.id,
                'ticket_title': violation.ticket.title,
                'sla_name': violation.sla.name,
                'violation_type': 'response_time',
                'expected_time': violation.response_deadline,
                'actual_time': violation.response_time_actual,
                'delay_hours': round(delay_hours, 2),
                'severity': 'high' if delay_hours > 24 else 'medium' if delay_hours > 4 else 'low'
            })
        
        for violation in resolution_violations:
            delay_hours = (violation.resolution_time_actual - violation.resolution_deadline).total_seconds() / 3600
            violations.append({
                'ticket_id': violation.ticket.id,
                'ticket_title': violation.ticket.title,
                'sla_name': violation.sla.name,
                'violation_type': 'resolution_time',
                'expected_time': violation.resolution_deadline,
                'actual_time': violation.resolution_time_actual,
                'delay_hours': round(delay_hours, 2),
                'severity': 'high' if delay_hours > 24 else 'medium' if delay_hours > 4 else 'low'
            })
        
        # Сортируем по времени задержки
        violations.sort(key=lambda x: x['delay_hours'], reverse=True)
        
        serializer = SLAViolationSerializer(violations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """Отчет по SLA."""
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
        total_tickets = Ticket.objects.filter(
            tenant=tenant,
            created_at__date__range=[period_start, period_end]
        ).count()
        
        tickets_with_sla = TicketSLA.objects.filter(
            tenant=tenant,
            created_at__date__range=[period_start, period_end]
        ).count()
        
        # Статистика времени ответа
        response_stats = TicketSLA.objects.filter(
            tenant=tenant,
            created_at__date__range=[period_start, period_end]
        ).aggregate(
            total=Count('id'),
            met=Count('id', filter=Q(is_response_met=True)),
            missed=Count('id', filter=Q(is_response_met=False)),
            avg_time=Avg('response_time_actual')
        )
        
        # Статистика времени решения
        resolution_stats = TicketSLA.objects.filter(
            tenant=tenant,
            created_at__date__range=[period_start, period_end]
        ).aggregate(
            total=Count('id'),
            met=Count('id', filter=Q(is_resolution_met=True)),
            missed=Count('id', filter=Q(is_resolution_met=False)),
            avg_time=Avg('resolution_time_actual')
        )
        
        # Топ нарушений
        top_violations = TicketSLA.objects.filter(
            tenant=tenant,
            created_at__date__range=[period_start, period_end],
            is_response_met=False
        ).values('sla__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Рекомендации
        recommendations = []
        
        if response_stats['missed'] > response_stats['met']:
            recommendations.append("Увеличьте время ответа в SLA или улучшите процессы")
        
        if resolution_stats['missed'] > resolution_stats['met']:
            recommendations.append("Увеличьте время решения в SLA или добавьте ресурсы")
        
        if not recommendations:
            recommendations.append("SLA выполняется хорошо, продолжайте в том же духе")
        
        report_data = {
            'period_start': period_start,
            'period_end': period_end,
            'total_tickets': total_tickets,
            'tickets_with_sla': tickets_with_sla,
            'response_time_stats': response_stats,
            'resolution_time_stats': resolution_stats,
            'violations': [],  # Здесь можно добавить детальные нарушения
            'top_violations': list(top_violations),
            'recommendations': recommendations,
        }
        
        serializer = SLAReportSerializer(report_data)
        return Response(serializer.data)


class TicketSLAViewSet(viewsets.ModelViewSet):
    """Управление связями тикетов и SLA."""
    
    queryset = TicketSLA.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['ticket', 'sla', 'is_response_met', 'is_resolution_met']
    ordering_fields = ['assigned_at', 'response_deadline', 'resolution_deadline']
    ordering = ['-assigned_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return TicketSLACreateSerializer
        else:
            return TicketSLASerializer
    
    @action(detail=True, methods=['post'])
    def update_times(self, request, pk=None):
        """Обновление фактических времен выполнения."""
        ticket_sla = self.get_object()
        
        response_time_actual = request.data.get('response_time_actual')
        resolution_time_actual = request.data.get('resolution_time_actual')
        
        if response_time_actual:
            ticket_sla.response_time_actual = response_time_actual
            ticket_sla.is_response_met = response_time_actual <= ticket_sla.response_deadline
        
        if resolution_time_actual:
            ticket_sla.resolution_time_actual = resolution_time_actual
            ticket_sla.is_resolution_met = resolution_time_actual <= ticket_sla.resolution_deadline
        
        ticket_sla.save()
        
        return Response({
            'message': 'Времена выполнения обновлены',
            'data': TicketSLASerializer(ticket_sla).data
        })
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Просроченные SLA."""
        now = timezone.now()
        
        overdue_response = self.get_queryset().filter(
            response_deadline__lt=now,
            is_response_met=False,
            response_time_actual__isnull=True
        )
        
        overdue_resolution = self.get_queryset().filter(
            resolution_deadline__lt=now,
            is_resolution_met=False,
            resolution_time_actual__isnull=True
        )
        
        overdue = list(overdue_response) + list(overdue_resolution)
        
        serializer = TicketSLASerializer(overdue, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming_deadlines(self, request):
        """Предстоящие дедлайны."""
        now = timezone.now()
        hours_ahead = int(request.query_params.get('hours', 24))
        deadline = now + timezone.timedelta(hours=hours_ahead)
        
        upcoming = self.get_queryset().filter(
            Q(response_deadline__lte=deadline, response_deadline__gt=now) |
            Q(resolution_deadline__lte=deadline, resolution_deadline__gt=now)
        ).order_by('response_deadline', 'resolution_deadline')
        
        serializer = TicketSLASerializer(upcoming, many=True)
        return Response(serializer.data)
