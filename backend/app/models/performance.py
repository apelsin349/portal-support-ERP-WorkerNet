"""
Модели для системы мониторинга производительности.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()
from .tenant import Tenant


class PerformanceMetric(models.Model):
    """Метрика производительности."""
    
    METRIC_TYPES = [
        ('response_time', _('Время ответа')),
        ('throughput', _('Пропускная способность')),
        ('error_rate', _('Частота ошибок')),
        ('cpu_usage', _('Использование CPU')),
        ('memory_usage', _('Использование памяти')),
        ('disk_usage', _('Использование диска')),
        ('database_query_time', _('Время запроса к БД')),
        ('cache_hit_rate', _('Частота попаданий в кэш')),
        ('custom', _('Пользовательская')),
    ]
    
    # Базовая информация
    name = models.CharField(max_length=100, verbose_name=_("Название"))
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES, verbose_name=_("Тип метрики"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    
    # Значение
    value = models.FloatField(verbose_name=_("Значение"))
    unit = models.CharField(max_length=20, default='ms', verbose_name=_("Единица измерения"))
    
    # Контекст
    service = models.CharField(max_length=100, blank=True, verbose_name=_("Сервис"))
    endpoint = models.CharField(max_length=200, blank=True, verbose_name=_("Эндпоинт"))
    method = models.CharField(max_length=10, blank=True, verbose_name=_("HTTP метод"))
    
    # Метаданные
    tags = models.JSONField(default=dict, verbose_name=_("Теги"))
    metadata = models.JSONField(default=dict, verbose_name=_("Метаданные"))
    
    # Арендатор
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='performance_metrics',
        verbose_name=_("Арендатор")
    )
    
    # Время измерения
    timestamp = models.DateTimeField(verbose_name=_("Время измерения"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    
    class Meta:
        verbose_name = _("Метрика производительности")
        verbose_name_plural = _("Метрики производительности")
        db_table = 'performance_metrics'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_type', 'timestamp']),
            models.Index(fields=['service', 'timestamp']),
            models.Index(fields=['tenant', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.name}: {self.value}{self.unit}"


class PerformanceAlert(models.Model):
    """Алерт производительности."""
    
    SEVERITY_CHOICES = [
        ('low', _('Низкий')),
        ('medium', _('Средний')),
        ('high', _('Высокий')),
        ('critical', _('Критический')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('Активен')),
        ('acknowledged', _('Подтвержден')),
        ('resolved', _('Решен')),
        ('suppressed', _('Подавлен')),
    ]
    
    # Базовая информация
    name = models.CharField(max_length=200, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    
    # Условие алерта
    metric_type = models.CharField(max_length=30, verbose_name=_("Тип метрики"))
    threshold_value = models.FloatField(verbose_name=_("Пороговое значение"))
    comparison_operator = models.CharField(
        max_length=10,
        choices=[
            ('gt', _('Больше')),
            ('gte', _('Больше или равно')),
            ('lt', _('Меньше')),
            ('lte', _('Меньше или равно')),
            ('eq', _('Равно')),
            ('ne', _('Не равно')),
        ],
        verbose_name=_("Оператор сравнения")
    )
    
    # Настройки алерта
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, verbose_name=_("Критичность"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name=_("Статус"))
    
    # Условия
    conditions = models.JSONField(default=dict, verbose_name=_("Условия"))
    
    # Действия
    actions = models.JSONField(default=dict, verbose_name=_("Действия"))
    
    # Арендатор
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='performance_alerts',
        verbose_name=_("Арендатор")
    )
    
    # Временные рамки
    triggered_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Сработал"))
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Решен"))
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Алерт производительности")
        verbose_name_plural = _("Алерты производительности")
        db_table = 'performance_alerts'
        ordering = ['-triggered_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_severity_display()})"


class PerformanceTrace(models.Model):
    """Трассировка запроса."""
    
    # Базовая информация
    trace_id = models.CharField(max_length=100, unique=True, verbose_name=_("ID трассировки"))
    span_id = models.CharField(max_length=100, verbose_name=_("ID span"))
    parent_span_id = models.CharField(max_length=100, blank=True, verbose_name=_("ID родительского span"))
    
    # Операция
    operation_name = models.CharField(max_length=200, verbose_name=_("Название операции"))
    service_name = models.CharField(max_length=100, verbose_name=_("Название сервиса"))
    
    # Время выполнения
    start_time = models.DateTimeField(verbose_name=_("Время начала"))
    end_time = models.DateTimeField(verbose_name=_("Время окончания"))
    duration_ms = models.PositiveIntegerField(verbose_name=_("Длительность (мс)"))
    
    # Статус
    status_code = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Код статуса"))
    is_error = models.BooleanField(default=False, verbose_name=_("Ошибка"))
    error_message = models.TextField(blank=True, verbose_name=_("Сообщение об ошибке"))
    
    # Метаданные
    tags = models.JSONField(default=dict, verbose_name=_("Теги"))
    logs = models.JSONField(default=list, verbose_name=_("Логи"))
    
    # Арендатор
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='performance_traces',
        verbose_name=_("Арендатор")
    )
    
    # Пользователь
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performance_traces',
        verbose_name=_("Пользователь")
    )
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    
    class Meta:
        verbose_name = _("Трассировка производительности")
        verbose_name_plural = _("Трассировки производительности")
        db_table = 'performance_traces'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['trace_id']),
            models.Index(fields=['service_name', 'start_time']),
            models.Index(fields=['operation_name', 'start_time']),
        ]
    
    def __str__(self):
        return f"{self.operation_name} ({self.duration_ms}ms)"


class PerformanceDashboard(models.Model):
    """Дашборд производительности."""
    
    name = models.CharField(max_length=200, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    
    # Конфигурация дашборда
    config = models.JSONField(default=dict, verbose_name=_("Конфигурация"))
    
    # Настройки
    is_public = models.BooleanField(default=False, verbose_name=_("Публичный"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    
    # Арендатор
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='performance_dashboards',
        verbose_name=_("Арендатор")
    )
    
    # Автор
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='performance_dashboards',
        verbose_name=_("Создатель")
    )
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Дашборд производительности")
        verbose_name_plural = _("Дашборды производительности")
        db_table = 'performance_dashboards'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class PerformanceReport(models.Model):
    """Отчет производительности."""
    
    REPORT_TYPES = [
        ('daily', _('Ежедневный')),
        ('weekly', _('Еженедельный')),
        ('monthly', _('Ежемесячный')),
        ('custom', _('Пользовательский')),
    ]
    
    # Базовая информация
    name = models.CharField(max_length=200, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name=_("Тип отчета"))
    
    # Период отчета
    start_date = models.DateTimeField(verbose_name=_("Дата начала"))
    end_date = models.DateTimeField(verbose_name=_("Дата окончания"))
    
    # Конфигурация отчета
    config = models.JSONField(default=dict, verbose_name=_("Конфигурация"))
    
    # Результаты отчета
    results = models.JSONField(default=dict, verbose_name=_("Результаты"))
    
    # Арендатор
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='performance_reports',
        verbose_name=_("Арендатор")
    )
    
    # Автор
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='performance_reports',
        verbose_name=_("Создатель")
    )
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Отчет производительности")
        verbose_name_plural = _("Отчеты производительности")
        db_table = 'performance_reports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


class PerformanceThreshold(models.Model):
    """Пороговое значение для метрики."""
    
    # Базовая информация
    name = models.CharField(max_length=200, verbose_name=_("Название"))
    metric_type = models.CharField(max_length=30, verbose_name=_("Тип метрики"))
    
    # Пороговые значения
    warning_threshold = models.FloatField(verbose_name=_("Порог предупреждения"))
    critical_threshold = models.FloatField(verbose_name=_("Критический порог"))
    
    # Условия
    conditions = models.JSONField(default=dict, verbose_name=_("Условия"))
    
    # Настройки
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    
    # Арендатор
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='performance_thresholds',
        verbose_name=_("Арендатор")
    )
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Пороговое значение")
        verbose_name_plural = _("Пороговые значения")
        db_table = 'performance_thresholds'
        ordering = ['metric_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.metric_type})"
