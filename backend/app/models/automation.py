"""
Модели для системы автоматических правил.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()
from .tenant import Tenant


class AutomationRule(models.Model):
    """Автоматическое правило для обработки тикетов."""
    
    RULE_TYPES = [
        ('assignment', _('Назначение')),
        ('escalation', _('Эскалация')),
        ('notification', _('Уведомление')),
        ('status_change', _('Изменение статуса')),
        ('response', _('Автоответ')),
        ('tagging', _('Тегирование')),
        ('routing', _('Маршрутизация')),
    ]
    
    TRIGGER_TYPES = [
        ('ticket_created', _('Тикет создан')),
        ('ticket_updated', _('Тикет обновлен')),
        ('comment_added', _('Добавлен комментарий')),
        ('status_changed', _('Статус изменен')),
        ('priority_changed', _('Приоритет изменен')),
        ('sla_breach', _('Нарушение SLA')),
        ('time_based', _('По времени')),
    ]
    
    # Базовая информация
    name = models.CharField(max_length=200, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES, verbose_name=_("Тип правила"))
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPES, verbose_name=_("Тип триггера"))
    
    # Условия
    conditions = models.JSONField(default=dict, verbose_name=_("Условия"))
    
    # Действия
    actions = models.JSONField(default=dict, verbose_name=_("Действия"))
    
    # Настройки
    is_active = models.BooleanField(default=True, verbose_name=_("Активно"))
    priority = models.PositiveIntegerField(default=0, verbose_name=_("Приоритет"))
    
    # Арендатор
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='automation_rules',
        verbose_name=_("Арендатор")
    )
    
    # Автор
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_automation_rules',
        verbose_name=_("Создатель")
    )
    
    # Статистика
    execution_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество выполнений"))
    last_executed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Последнее выполнение"))
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Правило автоматизации")
        verbose_name_plural = _("Правила автоматизации")
        db_table = 'automation_rules'
        ordering = ['priority', '-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"


class AutomationExecution(models.Model):
    """Выполнение правила автоматизации."""
    
    STATUS_CHOICES = [
        ('pending', _('Ожидает')),
        ('running', _('Выполняется')),
        ('completed', _('Завершено')),
        ('failed', _('Ошибка')),
        ('skipped', _('Пропущено')),
    ]
    
    rule = models.ForeignKey(
        AutomationRule,
        on_delete=models.CASCADE,
        related_name='executions',
        verbose_name=_("Правило")
    )
    
    # Контекст выполнения
    ticket = models.ForeignKey(
        'ticket.Ticket',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='automation_executions',
        verbose_name=_("Тикет")
    )
    
    # Статус
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Статус"))
    
    # Результат
    result = models.JSONField(default=dict, verbose_name=_("Результат"))
    error_message = models.TextField(blank=True, verbose_name=_("Сообщение об ошибке"))
    
    # Время выполнения
    started_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Начато"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Завершено"))
    
    class Meta:
        verbose_name = _("Выполнение правила")
        verbose_name_plural = _("Выполнения правил")
        db_table = 'automation_executions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.rule.name} - {self.get_status_display()}"


class AutomationCondition(models.Model):
    """Условие для правила автоматизации."""
    
    CONDITION_TYPES = [
        ('field_equals', _('Поле равно')),
        ('field_contains', _('Поле содержит')),
        ('field_greater_than', _('Поле больше')),
        ('field_less_than', _('Поле меньше')),
        ('field_in', _('Поле в списке')),
        ('field_not_in', _('Поле не в списке')),
        ('field_is_empty', _('Поле пустое')),
        ('field_is_not_empty', _('Поле не пустое')),
        ('time_based', _('По времени')),
        ('user_based', _('По пользователю')),
        ('custom', _('Пользовательское')),
    ]
    
    rule = models.ForeignKey(
        AutomationRule,
        on_delete=models.CASCADE,
        related_name='conditions',
        verbose_name=_("Правило")
    )
    
    # Условие
    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPES, verbose_name=_("Тип условия"))
    field_name = models.CharField(max_length=100, blank=True, verbose_name=_("Название поля"))
    operator = models.CharField(max_length=20, blank=True, verbose_name=_("Оператор"))
    value = models.TextField(blank=True, verbose_name=_("Значение"))
    
    # Логические операторы
    logical_operator = models.CharField(
        max_length=10,
        choices=[
            ('AND', _('И')),
            ('OR', _('ИЛИ')),
        ],
        default='AND',
        verbose_name=_("Логический оператор")
    )
    
    # Порядок
    order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок"))
    
    class Meta:
        verbose_name = _("Условие правила")
        verbose_name_plural = _("Условия правил")
        db_table = 'automation_conditions'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.rule.name} - {self.get_condition_type_display()}"


class AutomationAction(models.Model):
    """Действие для правила автоматизации."""
    
    ACTION_TYPES = [
        ('assign_ticket', _('Назначить тикет')),
        ('change_status', _('Изменить статус')),
        ('change_priority', _('Изменить приоритет')),
        ('add_tag', _('Добавить тег')),
        ('remove_tag', _('Удалить тег')),
        ('send_notification', _('Отправить уведомление')),
        ('send_email', _('Отправить email')),
        ('add_comment', _('Добавить комментарий')),
        ('escalate', _('Эскалировать')),
        ('close_ticket', _('Закрыть тикет')),
        ('custom', _('Пользовательское')),
    ]
    
    rule = models.ForeignKey(
        AutomationRule,
        on_delete=models.CASCADE,
        related_name='actions',
        verbose_name=_("Правило")
    )
    
    # Действие
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, verbose_name=_("Тип действия"))
    parameters = models.JSONField(default=dict, verbose_name=_("Параметры"))
    
    # Порядок
    order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок"))
    
    class Meta:
        verbose_name = _("Действие правила")
        verbose_name_plural = _("Действия правил")
        db_table = 'automation_actions'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.rule.name} - {self.get_action_type_display()}"


class AutomationTemplate(models.Model):
    """Шаблон правила автоматизации."""
    
    name = models.CharField(max_length=200, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    
    # Шаблон
    template_data = models.JSONField(default=dict, verbose_name=_("Данные шаблона"))
    
    # Категория
    category = models.CharField(max_length=100, blank=True, verbose_name=_("Категория"))
    
    # Настройки
    is_public = models.BooleanField(default=True, verbose_name=_("Публичный"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    
    # Автор
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='automation_templates',
        verbose_name=_("Создатель")
    )
    
    # Статистика использования
    usage_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество использований"))
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Шаблон правила")
        verbose_name_plural = _("Шаблоны правил")
        db_table = 'automation_templates'
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return self.name


class AutomationSchedule(models.Model):
    """Расписание для правил автоматизации."""
    
    FREQUENCY_CHOICES = [
        ('once', _('Один раз')),
        ('daily', _('Ежедневно')),
        ('weekly', _('Еженедельно')),
        ('monthly', _('Ежемесячно')),
        ('custom', _('Пользовательское')),
    ]
    
    rule = models.OneToOneField(
        AutomationRule,
        on_delete=models.CASCADE,
        related_name='schedule',
        verbose_name=_("Правило")
    )
    
    # Расписание
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name=_("Частота"))
    cron_expression = models.CharField(max_length=100, blank=True, verbose_name=_("Cron выражение"))
    
    # Время выполнения
    start_time = models.TimeField(verbose_name=_("Время начала"))
    end_time = models.TimeField(null=True, blank=True, verbose_name=_("Время окончания"))
    
    # Дни недели (для weekly)
    weekdays = models.JSONField(default=list, blank=True, verbose_name=_("Дни недели"))
    
    # Дни месяца (для monthly)
    month_days = models.JSONField(default=list, blank=True, verbose_name=_("Дни месяца"))
    
    # Настройки
    is_active = models.BooleanField(default=True, verbose_name=_("Активно"))
    timezone = models.CharField(max_length=50, default='UTC', verbose_name=_("Часовой пояс"))
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Расписание правила")
        verbose_name_plural = _("Расписания правил")
        db_table = 'automation_schedules'
    
    def __str__(self):
        return f"Schedule for {self.rule.name}"
