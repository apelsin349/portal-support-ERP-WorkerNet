"""
Модели для системы оценки качества.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()
from .tenant import Tenant


class TicketRating(models.Model):
    """Оценка тикета клиентом."""
    
    RATING_CHOICES = [
        (1, _('Очень плохо')),
        (2, _('Плохо')),
        (3, _('Удовлетворительно')),
        (4, _('Хорошо')),
        (5, _('Отлично')),
    ]
    
    # Связи
    ticket = models.OneToOneField(
        'app.Ticket',
        on_delete=models.CASCADE,
        related_name='rating',
        verbose_name=_("Тикет")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ticket_ratings',
        verbose_name=_("Пользователь")
    )
    
    # Оценки
    overall_rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Общая оценка")
    )
    
    # Детальные оценки
    response_time_rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        verbose_name=_("Оценка времени ответа")
    )
    resolution_quality_rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        verbose_name=_("Оценка качества решения")
    )
    communication_rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        verbose_name=_("Оценка коммуникации")
    )
    
    # Комментарии
    comment = models.TextField(blank=True, verbose_name=_("Комментарий"))
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Оценка тикета")
        verbose_name_plural = _("Оценки тикетов")
        db_table = 'ticket_ratings'
        unique_together = ['ticket', 'user']
    
    def __str__(self):
        return f"Rating {self.overall_rating} for {self.ticket.ticket_id}"


class AgentRating(models.Model):
    """Оценка агента поддержки."""
    
    # Связи
    agent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='agent_ratings',
        verbose_name=_("Агент")
    )
    rated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='given_agent_ratings',
        verbose_name=_("Оценил")
    )
    ticket = models.ForeignKey(
        'app.Ticket',
        on_delete=models.CASCADE,
        related_name='agent_ratings',
        verbose_name=_("Тикет")
    )
    
    # Оценки
    professionalism_rating = models.PositiveIntegerField(
        choices=TicketRating.RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Профессионализм")
    )
    knowledge_rating = models.PositiveIntegerField(
        choices=TicketRating.RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Знания")
    )
    communication_rating = models.PositiveIntegerField(
        choices=TicketRating.RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Коммуникация")
    )
    problem_solving_rating = models.PositiveIntegerField(
        choices=TicketRating.RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Решение проблем")
    )
    
    # Общая оценка
    overall_rating = models.PositiveIntegerField(
        choices=TicketRating.RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Общая оценка")
    )
    
    # Комментарии
    comment = models.TextField(blank=True, verbose_name=_("Комментарий"))
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Оценка агента")
        verbose_name_plural = _("Оценки агентов")
        db_table = 'agent_ratings'
        unique_together = ['agent', 'rated_by', 'ticket']
    
    def __str__(self):
        return f"Rating {self.overall_rating} for {self.agent.username}"


class ServiceRating(models.Model):
    """Оценка качества сервиса."""
    
    # Связи
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='service_ratings',
        verbose_name=_("Пользователь")
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='service_ratings',
        verbose_name=_("Арендатор")
    )
    
    # Оценки
    overall_satisfaction = models.PositiveIntegerField(
        choices=TicketRating.RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Общая удовлетворенность")
    )
    
    # Детальные оценки
    response_time_satisfaction = models.PositiveIntegerField(
        choices=TicketRating.RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        verbose_name=_("Удовлетворенность временем ответа")
    )
    resolution_quality_satisfaction = models.PositiveIntegerField(
        choices=TicketRating.RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        verbose_name=_("Удовлетворенность качеством решения")
    )
    communication_satisfaction = models.PositiveIntegerField(
        choices=TicketRating.RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        verbose_name=_("Удовлетворенность коммуникацией")
    )
    system_usability_satisfaction = models.PositiveIntegerField(
        choices=TicketRating.RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        verbose_name=_("Удовлетворенность удобством системы")
    )
    
    # Комментарии
    comment = models.TextField(blank=True, verbose_name=_("Комментарий"))
    suggestions = models.TextField(blank=True, verbose_name=_("Предложения"))
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Оценка сервиса")
        verbose_name_plural = _("Оценки сервиса")
        db_table = 'service_ratings'
        unique_together = ['user', 'tenant']
    
    def __str__(self):
        return f"Service rating {self.overall_satisfaction} by {self.user.username}"


class RatingCategory(models.Model):
    """Категория для оценки."""
    
    name = models.CharField(max_length=100, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    
    # Настройки
    is_required = models.BooleanField(default=False, verbose_name=_("Обязательная"))
    weight = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name=_("Вес")
    )
    
    # Арендатор
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='rating_categories',
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
        verbose_name = _("Категория оценки")
        verbose_name_plural = _("Категории оценок")
        db_table = 'rating_categories'
        ordering = ['order', 'name']
        unique_together = ['name', 'tenant']
    
    def __str__(self):
        return self.name


class RatingSurvey(models.Model):
    """Опрос для оценки."""
    
    name = models.CharField(max_length=200, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    
    # Настройки
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    is_required = models.BooleanField(default=False, verbose_name=_("Обязательный"))
    
    # Триггеры
    trigger_on_ticket_close = models.BooleanField(default=True, verbose_name=_("При закрытии тикета"))
    trigger_on_rating = models.BooleanField(default=False, verbose_name=_("При оценке"))
    
    # Арендатор
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='rating_surveys',
        verbose_name=_("Арендатор")
    )
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Опрос оценки")
        verbose_name_plural = _("Опросы оценок")
        db_table = 'rating_surveys'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class RatingSurveyQuestion(models.Model):
    """Вопрос в опросе оценки."""
    
    QUESTION_TYPES = [
        ('rating', _('Оценка')),
        ('text', _('Текст')),
        ('choice', _('Выбор')),
        ('multiple_choice', _('Множественный выбор')),
    ]
    
    survey = models.ForeignKey(
        RatingSurvey,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name=_("Опрос")
    )
    
    # Вопрос
    question_text = models.TextField(verbose_name=_("Текст вопроса"))
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, verbose_name=_("Тип вопроса"))
    
    # Настройки
    is_required = models.BooleanField(default=False, verbose_name=_("Обязательный"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок"))
    
    # Варианты ответов (для choice типов)
    choices = models.JSONField(default=list, blank=True, verbose_name=_("Варианты ответов"))
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Вопрос опроса")
        verbose_name_plural = _("Вопросы опросов")
        db_table = 'rating_survey_questions'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.survey.name} - {self.question_text[:50]}"


class RatingSurveyResponse(models.Model):
    """Ответ на опрос оценки."""
    
    survey = models.ForeignKey(
        RatingSurvey,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name=_("Опрос")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rating_survey_responses',
        verbose_name=_("Пользователь")
    )
    ticket = models.ForeignKey(
        'app.Ticket',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='rating_survey_responses',
        verbose_name=_("Тикет")
    )
    
    # Ответы
    responses = models.JSONField(default=dict, verbose_name=_("Ответы"))
    
    # Метаданные
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Завершен"))
    
    class Meta:
        verbose_name = _("Ответ на опрос")
        verbose_name_plural = _("Ответы на опросы")
        db_table = 'rating_survey_responses'
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"Response to {self.survey.name} by {self.user.username}"
