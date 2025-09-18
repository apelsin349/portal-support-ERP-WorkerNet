"""
Представления для A/B тестирования.
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
import random

from app.models import (
    FeatureFlag, ABTest, ABTestVariant, ABTestParticipant,
    ABTestEvent, ABTestMetric
)
from app.api.serializers.ab_testing import (
    FeatureFlagSerializer, FeatureFlagCreateSerializer,
    ABTestSerializer, ABTestCreateSerializer, ABTestVariantSerializer,
    ABTestParticipantSerializer, ABTestEventSerializer,
    ABTestEventCreateSerializer, ABTestMetricSerializer,
    ABTestStatsSerializer, ABTestReportSerializer,
    FeatureFlagUsageSerializer, ABTestAssignmentSerializer
)

User = get_user_model()


class FeatureFlagViewSet(viewsets.ModelViewSet):
    """Управление флагами функций."""
    
    queryset = FeatureFlag.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_enabled']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return FeatureFlagCreateSerializer
        else:
            return FeatureFlagSerializer
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Переключение флага функции."""
        flag = self.get_object()
        flag.is_enabled = not flag.is_enabled
        flag.save(update_fields=['is_enabled'])
        
        return Response({
            'message': f'Флаг {flag.name} {"включен" if flag.is_enabled else "выключен"}',
            'is_enabled': flag.is_enabled
        })
    
    @action(detail=False, methods=['get'])
    def check(self, request):
        """Проверка состояния флагов для пользователя."""
        user = request.user
        flags = self.get_queryset().filter(is_enabled=True)
        
        result = {}
        for flag in flags:
            # Простая логика проверки условий
            is_enabled = self._check_flag_conditions(flag, user)
            result[flag.name] = is_enabled
        
        return Response(result)
    
    def _check_flag_conditions(self, flag, user):
        """Проверка условий флага для пользователя."""
        # Простая реализация - можно расширить
        if flag.rollout_percentage < 100:
            # Простое хеширование по ID пользователя
            hash_value = hash(str(user.id)) % 100
            if hash_value >= flag.rollout_percentage:
                return False
        
        return True
    
    @action(detail=False, methods=['get'])
    def usage_stats(self, request):
        """Статистика использования флагов."""
        tenant = request.user.tenant
        
        # Здесь можно добавить логику сбора статистики
        # Пока возвращаем базовую информацию
        flags = self.get_queryset()
        stats = []
        
        for flag in flags:
            stats.append({
                'flag_name': flag.name,
                'is_enabled': flag.is_enabled,
                'rollout_percentage': flag.rollout_percentage,
                'created_at': flag.created_at
            })
        
        return Response(stats)


class ABTestViewSet(viewsets.ModelViewSet):
    """Управление A/B тестами."""
    
    queryset = ABTest.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'start_date', 'end_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return ABTestCreateSerializer
        else:
            return ABTestSerializer
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Запуск A/B теста."""
        test = self.get_object()
        
        if test.status != 'draft':
            return Response(
                {'error': 'Тест можно запустить только из статуса draft'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        test.status = 'running'
        test.start_date = timezone.now()
        test.save(update_fields=['status', 'start_date'])
        
        return Response({'message': 'A/B тест запущен'})
    
    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """Остановка A/B теста."""
        test = self.get_object()
        
        if test.status != 'running':
            return Response(
                {'error': 'Тест можно остановить только из статуса running'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        test.status = 'completed'
        test.end_date = timezone.now()
        test.save(update_fields=['status', 'end_date'])
        
        return Response({'message': 'A/B тест остановлен'})
    
    @action(detail=True, methods=['post'])
    def assign_user(self, request, pk=None):
        """Назначение пользователя в A/B тест."""
        test = self.get_object()
        serializer = ABTestAssignmentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user_id = data['user_id']
        
        try:
            user = User.objects.get(id=user_id, tenant=request.user.tenant)
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Проверяем, не участвует ли уже пользователь
        existing_participant = ABTestParticipant.objects.filter(
            test=test, user=user
        ).first()
        
        if existing_participant:
            return Response({
                'message': 'Пользователь уже участвует в тесте',
                'variant': existing_participant.variant.name
            })
        
        # Выбираем вариант
        if data.get('force_variant') and data.get('variant_id'):
            try:
                variant = ABTestVariant.objects.get(
                    id=data['variant_id'], test=test
                )
            except ABTestVariant.DoesNotExist:
                return Response(
                    {'error': 'Вариант не найден'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Случайное назначение на основе трафика
            variants = test.variants.all()
            if not variants.exists():
                return Response(
                    {'error': 'В тесте нет вариантов'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Простое случайное назначение
            variant = random.choice(list(variants))
        
        # Создаем участника
        participant = ABTestParticipant.objects.create(
            test=test,
            user=user,
            variant=variant,
            tenant=request.user.tenant
        )
        
        return Response({
            'message': 'Пользователь назначен в тест',
            'variant': variant.name,
            'participant_id': participant.id
        })
    
    @action(detail=True, methods=['post'])
    def track_event(self, request, pk=None):
        """Отслеживание события в A/B тесте."""
        test = self.get_object()
        user = request.user
        
        # Проверяем, участвует ли пользователь в тесте
        participant = ABTestParticipant.objects.filter(
            test=test, user=user
        ).first()
        
        if not participant:
            return Response(
                {'error': 'Пользователь не участвует в тесте'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ABTestEventCreateSerializer(
            data=request.data,
            context={'request': request, 'test': test, 'variant': participant.variant}
        )
        
        if serializer.is_valid():
            event = serializer.save()
            return Response({
                'message': 'Событие зафиксировано',
                'event_id': event.id
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Статистика A/B теста."""
        test = self.get_object()
        
        # Участники по вариантам
        participants_by_variant = {}
        conversion_rates = {}
        
        for variant in test.variants.all():
            participants = ABTestParticipant.objects.filter(
                test=test, variant=variant
            ).count()
            participants_by_variant[variant.name] = participants
            
            # Конверсия
            conversions = ABTestEvent.objects.filter(
                test=test, variant=variant, event_type='conversion'
            ).count()
            
            if participants > 0:
                conversion_rates[variant.name] = (conversions / participants) * 100
            else:
                conversion_rates[variant.name] = 0
        
        # Общее количество участников
        total_participants = sum(participants_by_variant.values())
        
        # Простая статистическая значимость (упрощенная)
        if len(conversion_rates) >= 2:
            rates = list(conversion_rates.values())
            max_rate = max(rates)
            min_rate = min(rates)
            statistical_significance = min(95.0, (max_rate - min_rate) * 2)
        else:
            statistical_significance = 0
        
        # Победитель
        winner_variant = None
        if statistical_significance > 80:
            winner_variant = max(conversion_rates, key=conversion_rates.get)
        
        stats_data = {
            'test_id': test.id,
            'test_name': test.name,
            'status': test.status,
            'total_participants': total_participants,
            'participants_by_variant': participants_by_variant,
            'conversion_rates': conversion_rates,
            'statistical_significance': round(statistical_significance, 2),
            'winner_variant': winner_variant,
            'confidence_level': statistical_significance,
            'recommendations': self._get_recommendations(test, conversion_rates, statistical_significance)
        }
        
        serializer = ABTestStatsSerializer(stats_data)
        return Response(serializer.data)
    
    def _get_recommendations(self, test, conversion_rates, significance):
        """Получение рекомендаций по A/B тесту."""
        recommendations = []
        
        if significance < 80:
            recommendations.append("Недостаточно данных для принятия решения. Продолжите тест.")
        elif significance >= 95:
            recommendations.append("Тест показывает статистически значимые результаты.")
        
        if test.status == 'running':
            recommendations.append("Рассмотрите возможность остановки теста и внедрения победителя.")
        
        return recommendations
    
    @action(detail=False, methods=['get'])
    def active_tests(self, request):
        """Активные A/B тесты."""
        active_tests = self.get_queryset().filter(status='running')
        serializer = ABTestSerializer(active_tests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def user_tests(self, request):
        """A/B тесты пользователя."""
        user = request.user
        user_tests = ABTestParticipant.objects.filter(
            user=user, test__tenant=user.tenant
        ).select_related('test', 'variant')
        
        result = []
        for participant in user_tests:
            result.append({
                'test_id': participant.test.id,
                'test_name': participant.test.name,
                'variant_name': participant.variant.name,
                'joined_at': participant.joined_at
            })
        
        return Response(result)


class ABTestVariantViewSet(viewsets.ModelViewSet):
    """Управление вариантами A/B тестов."""
    
    queryset = ABTestVariant.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['test', 'is_control']
    ordering_fields = ['name', 'traffic_percentage']
    ordering = ['name']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(test__tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return ABTestVariantCreateSerializer
        else:
            return ABTestVariantSerializer


class ABTestParticipantViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр участников A/B тестов."""
    
    queryset = ABTestParticipant.objects.all()
    serializer_class = ABTestParticipantSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['test', 'variant', 'is_active']
    ordering_fields = ['joined_at']
    ordering = ['-joined_at']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(tenant=self.request.user.tenant)


class ABTestEventViewSet(viewsets.ModelViewSet):
    """Управление событиями A/B тестов."""
    
    queryset = ABTestEvent.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['test', 'variant', 'event_type']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Фильтрация по арендатору."""
        return self.queryset.filter(test__tenant=self.request.user.tenant)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return ABTestEventCreateSerializer
        else:
            return ABTestEventSerializer
