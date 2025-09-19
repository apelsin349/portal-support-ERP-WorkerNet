"""
Модели тикетов для системы службы поддержки.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

# Импортируем Tenant для использования в ForeignKey
from .tenant import Tenant


class Ticket(models.Model):
    """Модель тикета службы поддержки."""
    
    PRIORITY_CHOICES = [
        ('low', _('Низкий')),
        ('medium', _('Средний')),
        ('high', _('Высокий')),
        ('urgent', _('Срочный')),
        ('critical', _('Критический')),
    ]
    
    STATUS_CHOICES = [
        ('open', _('Открыт')),
        ('in_progress', _('В работе')),
        ('pending', _('Ожидание')),
        ('resolved', _('Решён')),
        ('closed', _('Закрыт')),
        ('cancelled', _('Отменён')),
    ]
    
    CATEGORY_CHOICES = [
        ('technical', _('Техническая')),
        ('billing', _('Биллинг')),
        ('general', _('Общая')),
        ('bug_report', _('Баг')),
        ('feature_request', _('Запрос фичи')),
        ('other', _('Другое')),
    ]
    
    # Базовая информация
    ticket_id = models.CharField(max_length=20, unique=True, verbose_name=_("ID тикета"))
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    description = models.TextField(verbose_name=_("Описание"))
    
    # Классификация
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name=_("Приоритет"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name=_("Статус"))
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general', verbose_name=_("Категория"))
    
    # Назначение
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tickets',
        verbose_name=_("Автор")
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name=_("Назначен")
    )
    
    # Арендатор
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name=_("Арендатор")
    )
    
    # SLA
    sla_hours = models.IntegerField(default=24, verbose_name=_("SLA (часы)"))
    due_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Крайний срок"))
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Время решения"))
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    # Пользовательские поля
    custom_fields = models.JSONField(default=dict, verbose_name=_("Пользовательские поля"))
    
    # Теги
    tags = models.ManyToManyField('Tag', blank=True, verbose_name=_("Теги"))
    
    class Meta:
        verbose_name = _("Тикет")
        verbose_name_plural = _("Тикеты")
        db_table = 'tickets'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.ticket_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_id = self.generate_ticket_id()
        super().save(*args, **kwargs)
    
    def generate_ticket_id(self):
        """Сгенерировать уникальный ID тикета."""
        import uuid
        return f"TK-{uuid.uuid4().hex[:8].upper()}"


class TicketComment(models.Model):
    """Модель комментария к тикету."""
    
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_("Тикет")
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ticket_comments',
        verbose_name=_("Автор")
    )
    content = models.TextField(verbose_name=_("Содержимое"))
    is_internal = models.BooleanField(default=False, verbose_name=_("Внутренний"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Комментарий к тикету")
        verbose_name_plural = _("Комментарии к тикету")
        db_table = 'ticket_comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on {self.ticket.ticket_id} by {self.author.username}"


class TicketAttachment(models.Model):
    """Модель вложения тикета."""
    
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_("Тикет")
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ticket_attachments',
        verbose_name=_("Загрузил")
    )
    file = models.FileField(upload_to='tickets/attachments/', verbose_name=_("Файл"))
    filename = models.CharField(max_length=255, verbose_name=_("Имя файла"))
    file_size = models.BigIntegerField(verbose_name=_("Размер файла"))
    mime_type = models.CharField(max_length=100, verbose_name=_("MIME-тип"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    
    class Meta:
        verbose_name = _("Вложение тикета")
        verbose_name_plural = _("Вложения тикетов")
        db_table = 'ticket_attachments'
    
    def __str__(self):
        return f"{self.filename} - {self.ticket.ticket_id}"


class Tag(models.Model):
    """Модель тега для тикетов."""
    
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Название"))
    color = models.CharField(max_length=7, default='#1976d2', verbose_name=_("Цвет"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    
    class Meta:
        verbose_name = _("Тег")
        verbose_name_plural = _("Теги")
        db_table = 'tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class SLA(models.Model):
    """Модель SLA (уровни сервиса)."""
    
    name = models.CharField(max_length=100, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    
    # Время ответа (в часах)
    response_time = models.IntegerField(verbose_name=_("Время ответа (часы)"))
    
    # Время решения (в часах)
    resolution_time = models.IntegerField(verbose_name=_("Время решения (часы)"))
    
    # Приоритет
    priority = models.CharField(max_length=20, choices=Ticket.PRIORITY_CHOICES, verbose_name=_("Приоритет"))
    
    # Арендатор
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='slas',
        verbose_name=_("Арендатор")
    )
    
    # Статус
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("SLA")
        verbose_name_plural = _("SLA")
        db_table = 'slas'
        unique_together = ['tenant', 'priority']
    
    def __str__(self):
        return f"{self.name} - {self.priority}"


class TicketSLA(models.Model):
    """Модель отслеживания SLA для конкретного тикета."""
    
    ticket = models.OneToOneField(
        Ticket,
        on_delete=models.CASCADE,
        related_name='sla_tracking',
        verbose_name=_("Тикет")
    )
    sla = models.ForeignKey(
        SLA,
        on_delete=models.CASCADE,
        related_name='ticket_slas',
        verbose_name=_("SLA")
    )
    
    # Метки времени
    first_response_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Время первого ответа"))
    resolution_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Время решения"))
    
    # Статус SLA
    is_breached = models.BooleanField(default=False, verbose_name=_("SLA нарушен"))
    breach_reason = models.TextField(blank=True, verbose_name=_("Причина нарушения"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("SLA тикета")
        verbose_name_plural = _("SLA тикетов")
        db_table = 'ticket_slas'
    
    def __str__(self):
        return f"SLA for {self.ticket.ticket_id}"
