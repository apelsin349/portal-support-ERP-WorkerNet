"""
Модели для управления инцидентами.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()
from .tenant import Tenant


class Incident(models.Model):
    """Модель инцидента."""
    
    SEVERITY_CHOICES = [
        ('P1', _('Критический')),
        ('P2', _('Высокий')),
        ('P3', _('Средний')),
        ('P4', _('Низкий')),
    ]
    
    STATUS_CHOICES = [
        ('open', _('Открыт')),
        ('investigating', _('Расследование')),
        ('identified', _('Выявлена причина')),
        ('monitoring', _('Мониторинг')),
        ('resolved', _('Решен')),
        ('closed', _('Закрыт')),
    ]
    
    CATEGORY_CHOICES = [
        ('infrastructure', _('Инфраструктура')),
        ('application', _('Приложение')),
        ('security', _('Безопасность')),
        ('data', _('Данные')),
        ('integration', _('Интеграция')),
        ('user_experience', _('Пользовательский опыт')),
    ]
    
    # Базовая информация
    incident_id = models.CharField(max_length=20, unique=True, verbose_name=_("ID инцидента"))
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    description = models.TextField(verbose_name=_("Описание"))
    
    # Классификация
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, verbose_name=_("Критичность"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name=_("Статус"))
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name=_("Категория"))
    
    # Назначение
    reported_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reported_incidents',
        verbose_name=_("Сообщил")
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_incidents',
        verbose_name=_("Назначен")
    )
    
    # Арендатор
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='incidents',
        verbose_name=_("Арендатор")
    )
    
    # Влияние
    affected_services = models.JSONField(default=list, verbose_name=_("Затронутые сервисы"))
    business_impact = models.TextField(blank=True, verbose_name=_("Бизнес-влияние"))
    user_impact = models.TextField(blank=True, verbose_name=_("Влияние на пользователей"))
    
    # Временные рамки
    detected_at = models.DateTimeField(verbose_name=_("Обнаружен"))
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Решен"))
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Закрыт"))
    
    # SLA
    response_time_minutes = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Время ответа (мин)"))
    resolution_time_minutes = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Время решения (мин)"))
    sla_breached = models.BooleanField(default=False, verbose_name=_("SLA нарушен"))
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    # Пользовательские поля
    custom_fields = models.JSONField(default=dict, verbose_name=_("Пользовательские поля"))
    
    # Теги
    tags = models.ManyToManyField('ticket.Tag', blank=True, verbose_name=_("Теги"))
    
    class Meta:
        verbose_name = _("Инцидент")
        verbose_name_plural = _("Инциденты")
        db_table = 'incidents'
        ordering = ['-detected_at']
    
    def __str__(self):
        return f"{self.incident_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.incident_id:
            self.incident_id = self.generate_incident_id()
        super().save(*args, **kwargs)
    
    def generate_incident_id(self):
        """Сгенерировать уникальный ID инцидента."""
        import uuid
        return f"INC-{uuid.uuid4().hex[:8].upper()}"


class IncidentUpdate(models.Model):
    """Обновление статуса инцидента."""
    
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='updates',
        verbose_name=_("Инцидент")
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='incident_updates',
        verbose_name=_("Автор")
    )
    
    # Содержимое
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    content = models.TextField(verbose_name=_("Содержимое"))
    
    # Тип обновления
    update_type = models.CharField(
        max_length=20,
        choices=[
            ('status_change', _('Изменение статуса')),
            ('investigation', _('Расследование')),
            ('resolution', _('Решение')),
            ('communication', _('Коммуникация')),
            ('escalation', _('Эскалация')),
        ],
        verbose_name=_("Тип обновления")
    )
    
    # Видимость
    is_public = models.BooleanField(default=True, verbose_name=_("Публичное"))
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    
    class Meta:
        verbose_name = _("Обновление инцидента")
        verbose_name_plural = _("Обновления инцидентов")
        db_table = 'incident_updates'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.incident.incident_id} - {self.title}"


class IncidentAttachment(models.Model):
    """Вложение к инциденту."""
    
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_("Инцидент")
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='incident_attachments',
        verbose_name=_("Загрузил")
    )
    
    file = models.FileField(upload_to='incidents/attachments/', verbose_name=_("Файл"))
    filename = models.CharField(max_length=255, verbose_name=_("Имя файла"))
    file_size = models.BigIntegerField(verbose_name=_("Размер файла"))
    mime_type = models.CharField(max_length=100, verbose_name=_("MIME-тип"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    
    class Meta:
        verbose_name = _("Вложение инцидента")
        verbose_name_plural = _("Вложения инцидентов")
        db_table = 'incident_attachments'
    
    def __str__(self):
        return f"{self.filename} - {self.incident.incident_id}"


class IncidentTimeline(models.Model):
    """Временная линия инцидента."""
    
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='timeline',
        verbose_name=_("Инцидент")
    )
    
    # Событие
    event_type = models.CharField(
        max_length=30,
        choices=[
            ('created', _('Создан')),
            ('assigned', _('Назначен')),
            ('status_changed', _('Статус изменен')),
            ('escalated', _('Эскалирован')),
            ('resolved', _('Решен')),
            ('closed', _('Закрыт')),
            ('comment_added', _('Добавлен комментарий')),
            ('attachment_added', _('Добавлено вложение')),
        ],
        verbose_name=_("Тип события")
    )
    
    # Описание события
    description = models.TextField(verbose_name=_("Описание"))
    
    # Автор события
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incident_timeline_events',
        verbose_name=_("Автор")
    )
    
    # Дополнительные данные
    metadata = models.JSONField(default=dict, verbose_name=_("Метаданные"))
    
    # Время события
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Время"))
    
    class Meta:
        verbose_name = _("Событие временной линии")
        verbose_name_plural = _("События временной линии")
        db_table = 'incident_timeline'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.incident.incident_id} - {self.get_event_type_display()}"


class IncidentEscalation(models.Model):
    """Эскалация инцидента."""
    
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='escalations',
        verbose_name=_("Инцидент")
    )
    
    # Уровень эскалации
    level = models.PositiveIntegerField(verbose_name=_("Уровень"))
    
    # Причина эскалации
    reason = models.TextField(verbose_name=_("Причина"))
    
    # Кому эскалирован
    escalated_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='escalated_incidents',
        verbose_name=_("Эскалирован")
    )
    
    # Кто эскалировал
    escalated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='incident_escalations',
        verbose_name=_("Эскалировал")
    )
    
    # Время эскалации
    escalated_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Время эскалации"))
    
    # Статус эскалации
    is_acknowledged = models.BooleanField(default=False, verbose_name=_("Подтверждена"))
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Время подтверждения"))
    
    class Meta:
        verbose_name = _("Эскалация инцидента")
        verbose_name_plural = _("Эскалации инцидентов")
        db_table = 'incident_escalations'
        ordering = ['-escalated_at']
    
    def __str__(self):
        return f"{self.incident.incident_id} - Level {self.level} escalation"


class IncidentSLA(models.Model):
    """SLA правила для инцидентов."""
    
    name = models.CharField(max_length=100, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    
    # Критичность
    severity = models.CharField(max_length=10, choices=Incident.SEVERITY_CHOICES, verbose_name=_("Критичность"))
    
    # Временные рамки (в минутах)
    response_time_minutes = models.PositiveIntegerField(verbose_name=_("Время ответа (мин)"))
    resolution_time_minutes = models.PositiveIntegerField(verbose_name=_("Время решения (мин)"))
    
    # Арендатор
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='incident_slas',
        verbose_name=_("Арендатор")
    )
    
    # Статус
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("SLA инцидента")
        verbose_name_plural = _("SLA инцидентов")
        db_table = 'incident_slas'
        unique_together = ['tenant', 'severity']
    
    def __str__(self):
        return f"{self.name} - {self.severity}"
