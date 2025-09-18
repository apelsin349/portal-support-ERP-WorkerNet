"""
Представления для системы тикетов.
"""
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Case, When, IntegerField, DurationField
from django.utils import timezone
from datetime import timedelta

from app.models import Ticket, TicketComment, TicketAttachment, Tag, SLA, TicketSLA
from app.api.serializers.ticket import (
    TicketListSerializer, TicketDetailSerializer, TicketCreateSerializer,
    TicketUpdateSerializer, TicketCommentSerializer, TicketCommentCreateSerializer,
    TicketAttachmentSerializer, TagSerializer, SLASerializer,
    TicketAssignSerializer, TicketStatusUpdateSerializer, TicketPriorityUpdateSerializer,
    TicketSearchSerializer, TicketStatsSerializer
)


class TicketViewSet(viewsets.ModelViewSet):
    """ViewSet для тикетов."""
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category', 'assigned_to', 'created_by']
    search_fields = ['title', 'description', 'ticket_id']
    ordering_fields = ['created_at', 'updated_at', 'priority', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Получение queryset тикетов для текущего тенанта."""
        return Ticket.objects.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'list':
            return TicketListSerializer
        elif self.action == 'create':
            return TicketCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TicketUpdateSerializer
        return TicketDetailSerializer
    
    def perform_create(self, serializer):
        """Создание тикета."""
        serializer.save(
            created_by=self.request.user,
            tenant=self.request.user.tenant
        )
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Назначение тикета пользователю."""
        ticket = self.get_object()
        serializer = TicketAssignSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        ticket.assigned_to = serializer.validated_data['assigned_to']
        ticket.save()
        
        # Добавляем комментарий о назначении
        TicketComment.objects.create(
            ticket=ticket,
            author=request.user,
            content=f"Тикет назначен пользователю {ticket.assigned_to.get_full_name()}",
            is_internal=True
        )
        
        return Response({
            'message': 'Тикет успешно назначен',
            'assigned_to': ticket.assigned_to.get_full_name()
        })
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Обновление статуса тикета."""
        ticket = self.get_object()
        serializer = TicketStatusUpdateSerializer(
            data=request.data,
            context={'ticket': ticket}
        )
        serializer.is_valid(raise_exception=True)
        
        old_status = ticket.status
        ticket.status = serializer.validated_data['status']
        
        # Обновляем время решения
        if ticket.status in ['resolved', 'closed'] and not ticket.resolved_at:
            ticket.resolved_at = timezone.now()
        elif ticket.status not in ['resolved', 'closed']:
            ticket.resolved_at = None
        
        ticket.save()
        
        # Добавляем комментарий об изменении статуса
        comment_text = f"Статус изменен с '{old_status}' на '{ticket.get_status_display()}'"
        if serializer.validated_data.get('comment'):
            comment_text += f"\n\n{serializer.validated_data['comment']}"
        
        TicketComment.objects.create(
            ticket=ticket,
            author=request.user,
            content=comment_text,
            is_internal=True
        )
        
        return Response({
            'message': 'Статус тикета обновлен',
            'status': ticket.get_status_display()
        })
    
    @action(detail=True, methods=['post'])
    def update_priority(self, request, pk=None):
        """Обновление приоритета тикета."""
        ticket = self.get_object()
        serializer = TicketPriorityUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_priority = ticket.priority
        ticket.priority = serializer.validated_data['priority']
        ticket.save()
        
        # Добавляем комментарий об изменении приоритета
        comment_text = f"Приоритет изменен с '{old_priority}' на '{ticket.get_priority_display()}'"
        if serializer.validated_data.get('comment'):
            comment_text += f"\n\n{serializer.validated_data['comment']}"
        
        TicketComment.objects.create(
            ticket=ticket,
            author=request.user,
            content=comment_text,
            is_internal=True
        )
        
        return Response({
            'message': 'Приоритет тикета обновлен',
            'priority': ticket.get_priority_display()
        })
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Добавление комментария к тикету."""
        ticket = self.get_object()
        serializer = TicketCommentCreateSerializer(
            data=request.data,
            context={'request': request, 'ticket': ticket}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Комментарий добавлен',
            'comment': TicketCommentSerializer(serializer.instance).data
        })
    
    @action(detail=True, methods=['post'])
    def add_attachment(self, request, pk=None):
        """Добавление вложения к тикету."""
        ticket = self.get_object()
        
        if 'file' not in request.FILES:
            return Response(
                {'error': 'Файл не найден'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        
        # Проверяем размер файла (50MB)
        if file.size > 50 * 1024 * 1024:
            return Response(
                {'error': 'Размер файла превышает 50MB'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attachment = TicketAttachment.objects.create(
            ticket=ticket,
            uploaded_by=request.user,
            file=file,
            filename=file.name,
            file_size=file.size,
            mime_type=file.content_type
        )
        
        return Response({
            'message': 'Вложение добавлено',
            'attachment': TicketAttachmentSerializer(attachment).data
        })
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Поиск тикетов."""
        serializer = TicketSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        queryset = self.get_queryset()
        params = serializer.validated_data
        
        # Фильтрация по параметрам
        if params.get('query'):
            queryset = queryset.filter(
                Q(title__icontains=params['query']) |
                Q(description__icontains=params['query']) |
                Q(ticket_id__icontains=params['query'])
            )
        
        if params.get('status'):
            queryset = queryset.filter(status=params['status'])
        
        if params.get('priority'):
            queryset = queryset.filter(priority=params['priority'])
        
        if params.get('category'):
            queryset = queryset.filter(category=params['category'])
        
        if params.get('assigned_to'):
            queryset = queryset.filter(assigned_to=params['assigned_to'])
        
        if params.get('created_by'):
            queryset = queryset.filter(created_by=params['created_by'])
        
        if params.get('tags'):
            tag_names = [tag.strip() for tag in params['tags'].split(',')]
            queryset = queryset.filter(tags__name__in=tag_names).distinct()
        
        if params.get('date_from'):
            queryset = queryset.filter(created_at__gte=params['date_from'])
        
        if params.get('date_to'):
            queryset = queryset.filter(created_at__lte=params['date_to'])
        
        if params.get('sla_breached') is not None:
            if params['sla_breached']:
                queryset = queryset.filter(sla_tracking__is_breached=True)
            else:
                queryset = queryset.filter(sla_tracking__is_breached=False)
        
        # Применяем пагинацию
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TicketListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TicketListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика тикетов."""
        queryset = self.get_queryset()
        
        # Общая статистика по статусам
        status_stats = queryset.aggregate(
            total=Count('id'),
            open=Count('id', filter=Q(status='open')),
            in_progress=Count('id', filter=Q(status='in_progress')),
            pending=Count('id', filter=Q(status='pending')),
            resolved=Count('id', filter=Q(status='resolved')),
            closed=Count('id', filter=Q(status='closed')),
            cancelled=Count('id', filter=Q(status='cancelled')),
        )
        
        # Статистика по приоритетам
        priority_stats = queryset.aggregate(
            critical=Count('id', filter=Q(priority='critical')),
            urgent=Count('id', filter=Q(priority='urgent')),
            high=Count('id', filter=Q(priority='high')),
            medium=Count('id', filter=Q(priority='medium')),
            low=Count('id', filter=Q(priority='low')),
        )
        
        # SLA статистика
        sla_stats = queryset.aggregate(
            sla_breached=Count('id', filter=Q(sla_tracking__is_breached=True)),
            sla_at_risk=Count('id', filter=Q(
                sla_tracking__is_breached=False,
                due_date__lte=timezone.now() + timedelta(hours=2)
            )),
            sla_ok=Count('id', filter=Q(
                sla_tracking__is_breached=False,
                due_date__gt=timezone.now() + timedelta(hours=2)
            )),
        )
        
        # Временные метрики
        time_stats = queryset.aggregate(
            avg_response_time=Avg('sla_tracking__first_response_at'),
            avg_resolution_time=Avg('sla_tracking__resolution_at'),
        )
        
        # Расчет процентов
        total = status_stats['total']
        first_response_rate = 0
        resolution_rate = 0
        
        if total > 0:
            first_response_rate = (status_stats['in_progress'] + status_stats['resolved'] + status_stats['closed']) / total * 100
            resolution_rate = (status_stats['resolved'] + status_stats['closed']) / total * 100
        
        stats_data = {
            **status_stats,
            **priority_stats,
            **sla_stats,
            'avg_response_time': time_stats['avg_response_time'],
            'avg_resolution_time': time_stats['avg_resolution_time'],
            'first_response_rate': first_response_rate,
            'resolution_rate': resolution_rate,
        }
        
        serializer = TicketStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_tickets(self, request):
        """Тикеты текущего пользователя."""
        queryset = self.get_queryset().filter(
            Q(created_by=request.user) | Q(assigned_to=request.user)
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TicketListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TicketListSerializer(queryset, many=True)
        return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet для тегов."""
    
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class SLAViewSet(viewsets.ModelViewSet):
    """ViewSet для SLA."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Получение SLA для текущего тенанта."""
        return SLA.objects.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        return SLASerializer
    
    def perform_create(self, serializer):
        """Создание SLA."""
        serializer.save(tenant=self.request.user.tenant)
