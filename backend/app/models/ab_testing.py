"""
Модели для A/B тестирования и feature flags.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()
from .tenant import Tenant


class FeatureFlag(models.Model):
    """Feature flag для управления функциональностью."""
    
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    is_enabled = models.BooleanField(default=False, verbose_name=_("Включен"))
    
    # Настройки
    rollout_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Процент пользователей")
    )
    
    # Целевые группы
    target_tenants = models.ManyToManyField(
        Tenant,
        blank=True,
        related_name='feature_flags',
        verbose_name=_("Целевые арендаторы")
    )
    
    # Временные рамки
    start_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата начала"))
    end_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата окончания"))
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Feature Flag")
        verbose_name_plural = _("Feature Flags")
        db_table = 'feature_flags'
    
    def __str__(self):
        return f"{self.name} ({'ON' if self.is_enabled else 'OFF'})"


class ABTest(models.Model):
    """A/B тест для экспериментов."""
    
    STATUS_CHOICES = [
        ('draft', _('Черновик')),
        ('active', _('Активен')),
        ('paused', _('Приостановлен')),
        ('completed', _('Завершен')),
        ('cancelled', _('Отменен')),
    ]
    
    name = models.CharField(max_length=200, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_("Статус"))
    
    # Настройки теста
    traffic_allocation = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name=_("Распределение трафика (%)")
    )
    
    # Временные рамки
    start_date = models.DateTimeField(verbose_name=_("Дата начала"))
    end_date = models.DateTimeField(verbose_name=_("Дата окончания"))
    
    # Целевые группы
    target_tenants = models.ManyToManyField(
        Tenant,
        blank=True,
        related_name='ab_tests',
        verbose_name=_("Целевые арендаторы")
    )
    
    # Метаданные
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_ab_tests',
        verbose_name=_("Создатель")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("A/B Тест")
        verbose_name_plural = _("A/B Тесты")
        db_table = 'ab_tests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class ABTestVariant(models.Model):
    """Вариант A/B теста."""
    
    ab_test = models.ForeignKey(
        ABTest,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name=_("A/B Тест")
    )
    
    name = models.CharField(max_length=100, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    
    # Конфигурация варианта
    weight = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name=_("Вес (%)")
    )
    
    # Настройки варианта
    config = models.JSONField(default=dict, verbose_name=_("Конфигурация"))
    
    # Статистика
    participants_count = models.PositiveIntegerField(default=0, verbose_name=_("Участников"))
    conversions_count = models.PositiveIntegerField(default=0, verbose_name=_("Конверсий"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Вариант A/B Теста")
        verbose_name_plural = _("Варианты A/B Тестов")
        db_table = 'ab_test_variants'
        unique_together = ['ab_test', 'name']
    
    def __str__(self):
        return f"{self.ab_test.name} - {self.name}"
    
    @property
    def conversion_rate(self):
        """Конверсия варианта."""
        if self.participants_count == 0:
            return 0
        return (self.conversions_count / self.participants_count) * 100


class ABTestParticipant(models.Model):
    """Участник A/B теста."""
    
    ab_test = models.ForeignKey(
        ABTest,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name=_("A/B Тест")
    )
    variant = models.ForeignKey(
        ABTestVariant,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name=_("Вариант")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ab_test_participations',
        verbose_name=_("Пользователь")
    )
    
    # Статус участия
    is_converted = models.BooleanField(default=False, verbose_name=_("Конвертирован"))
    converted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Время конверсии"))
    
    # Метаданные
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Назначен"))
    
    class Meta:
        verbose_name = _("Участник A/B Теста")
        verbose_name_plural = _("Участники A/B Тестов")
        db_table = 'ab_test_participants'
        unique_together = ['ab_test', 'user']
    
    def __str__(self):
        return f"{self.user.username} in {self.ab_test.name}"


class ABTestEvent(models.Model):
    """Событие в A/B тесте."""
    
    EVENT_TYPES = [
        ('view', _('Просмотр')),
        ('click', _('Клик')),
        ('conversion', _('Конверсия')),
        ('custom', _('Пользовательское')),
    ]
    
    participant = models.ForeignKey(
        ABTestParticipant,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name=_("Участник")
    )
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, verbose_name=_("Тип события"))
    event_name = models.CharField(max_length=100, verbose_name=_("Название события"))
    
    # Данные события
    properties = models.JSONField(default=dict, verbose_name=_("Свойства"))
    
    # Метаданные
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Время"))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("IP адрес"))
    user_agent = models.TextField(blank=True, verbose_name=_("User Agent"))
    
    class Meta:
        verbose_name = _("Событие A/B Теста")
        verbose_name_plural = _("События A/B Тестов")
        db_table = 'ab_test_events'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.participant.user.username} - {self.event_name} at {self.timestamp}"


class ABTestMetric(models.Model):
    """Метрика A/B теста."""
    
    METRIC_TYPES = [
        ('conversion_rate', _('Конверсия')),
        ('click_through_rate', _('CTR')),
        ('bounce_rate', _('Отказы')),
        ('time_on_page', _('Время на странице')),
        ('custom', _('Пользовательская')),
    ]
    
    ab_test = models.ForeignKey(
        ABTest,
        on_delete=models.CASCADE,
        related_name='metrics',
        verbose_name=_("A/B Тест")
    )
    
    name = models.CharField(max_length=100, verbose_name=_("Название"))
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES, verbose_name=_("Тип метрики"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    
    # Настройки метрики
    target_value = models.FloatField(null=True, blank=True, verbose_name=_("Целевое значение"))
    is_primary = models.BooleanField(default=False, verbose_name=_("Основная метрика"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Метрика A/B Теста")
        verbose_name_plural = _("Метрики A/B Тестов")
        db_table = 'ab_test_metrics'
        unique_together = ['ab_test', 'name']
    
    def __str__(self):
        return f"{self.ab_test.name} - {self.name}"
