"""
Модели для системы шаблонов ответов.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()
from .tenant import Tenant


class ResponseTemplate(models.Model):
    """Шаблон ответа для тикетов."""
    
    CATEGORY_CHOICES = [
        ('greeting', _('Приветствие')),
        ('acknowledgment', _('Подтверждение')),
        ('resolution', _('Решение')),
        ('escalation', _('Эскалация')),
        ('closing', _('Закрытие')),
        ('follow_up', _('Дополнительный вопрос')),
        ('custom', _('Пользовательский')),
    ]
    
    # Базовая информация
    name = models.CharField(max_length=200, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name=_("Категория"))
    
    # Содержимое
    subject_template = models.CharField(max_length=255, blank=True, verbose_name=_("Шаблон темы"))
    content_template = models.TextField(verbose_name=_("Шаблон содержимого"))
    
    # Настройки
    is_public = models.BooleanField(default=True, verbose_name=_("Публичный"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    
    # Автор
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='response_templates',
        verbose_name=_("Автор")
    )
    
    # Арендатор
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='response_templates',
        verbose_name=_("Арендатор")
    )
    
    # Статистика использования
    usage_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество использований"))
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Последнее использование"))
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    # Теги
    tags = models.ManyToManyField('app.Tag', blank=True, verbose_name=_("Теги"))
    
    class Meta:
        verbose_name = _("Шаблон ответа")
        verbose_name_plural = _("Шаблоны ответов")
        db_table = 'response_templates'
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class TemplateVariable(models.Model):
    """Переменная для шаблонов."""
    
    VARIABLE_TYPES = [
        ('text', _('Текст')),
        ('number', _('Число')),
        ('date', _('Дата')),
        ('datetime', _('Дата и время')),
        ('user', _('Пользователь')),
        ('ticket', _('Тикет')),
        ('system', _('Система')),
    ]
    
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    variable_type = models.CharField(max_length=20, choices=VARIABLE_TYPES, verbose_name=_("Тип переменной"))
    
    # Шаблон для замены
    template_string = models.CharField(max_length=100, verbose_name=_("Строка шаблона"))
    
    # Значение по умолчанию
    default_value = models.TextField(blank=True, verbose_name=_("Значение по умолчанию"))
    
    # Настройки
    is_system = models.BooleanField(default=False, verbose_name=_("Системная"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активна"))
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Переменная шаблона")
        verbose_name_plural = _("Переменные шаблонов")
        db_table = 'template_variables'
        ordering = ['name']
    
    def __str__(self):
        return f"{{{self.template_string}}}"


class TemplateUsage(models.Model):
    """Использование шаблона."""
    
    template = models.ForeignKey(
        ResponseTemplate,
        on_delete=models.CASCADE,
        related_name='usages',
        verbose_name=_("Шаблон")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='template_usages',
        verbose_name=_("Пользователь")
    )
    
    # Контекст использования
    ticket = models.ForeignKey(
        'app.Ticket',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='template_usages',
        verbose_name=_("Тикет")
    )
    
    # Кастомизация
    custom_subject = models.CharField(max_length=255, blank=True, verbose_name=_("Кастомная тема"))
    custom_content = models.TextField(blank=True, verbose_name=_("Кастомное содержимое"))
    
    # Переменные
    variables_used = models.JSONField(default=dict, verbose_name=_("Использованные переменные"))
    
    # Время использования
    used_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Время использования"))
    
    class Meta:
        verbose_name = _("Использование шаблона")
        verbose_name_plural = _("Использования шаблонов")
        db_table = 'template_usages'
        ordering = ['-used_at']
    
    def __str__(self):
        return f"{self.template.name} used by {self.user.username}"


class TemplateCategory(models.Model):
    """Категория шаблонов."""
    
    name = models.CharField(max_length=100, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    color = models.CharField(max_length=7, default='#1976d2', verbose_name=_("Цвет"))
    
    # Арендатор
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='template_categories',
        verbose_name=_("Арендатор")
    )
    
    # Порядок
    order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок"))
    
    # Статус
    is_active = models.BooleanField(default=True, verbose_name=_("Активна"))
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Категория шаблонов")
        verbose_name_plural = _("Категории шаблонов")
        db_table = 'template_categories'
        ordering = ['order', 'name']
        unique_together = ['name', 'tenant']
    
    def __str__(self):
        return self.name


class TemplateVersion(models.Model):
    """Версия шаблона."""
    
    template = models.ForeignKey(
        ResponseTemplate,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name=_("Шаблон")
    )
    
    # Версия
    version_number = models.PositiveIntegerField(verbose_name=_("Номер версии"))
    
    # Содержимое версии
    subject_template = models.CharField(max_length=255, blank=True, verbose_name=_("Шаблон темы"))
    content_template = models.TextField(verbose_name=_("Шаблон содержимого"))
    
    # Изменения
    changes = models.TextField(blank=True, verbose_name=_("Изменения"))
    
    # Автор версии
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='template_versions',
        verbose_name=_("Автор")
    )
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    
    class Meta:
        verbose_name = _("Версия шаблона")
        verbose_name_plural = _("Версии шаблонов")
        db_table = 'template_versions'
        ordering = ['-version_number']
        unique_together = ['template', 'version_number']
    
    def __str__(self):
        return f"{self.template.name} v{self.version_number}"
