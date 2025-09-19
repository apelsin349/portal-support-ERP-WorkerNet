"""
Модели базы знаний.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

# Импортируем Tenant для использования в ForeignKey
from .tenant import Tenant


class KnowledgeCategory(models.Model):
    """Knowledge base category model."""
    
    name = models.CharField(max_length=100, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_("Родительская категория")
    )
    
    # Tenant
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='knowledge_categories',
        verbose_name=_("Арендатор")
    )
    
    # Ordering
    order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок"))
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name=_("Активно"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Категория базы знаний")
        verbose_name_plural = _("Категории базы знаний")
        db_table = 'knowledge_categories'
        ordering = ['order', 'name']
        unique_together = ['name', 'tenant']
    
    def __str__(self):
        return self.name


class KnowledgeArticle(models.Model):
    """Knowledge base article model."""
    
    STATUS_CHOICES = [
        ('draft', _('Черновик')),
        ('published', _('Опубликовано')),
        ('archived', _('Архивировано')),
    ]
    
    # Basic information
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    slug = models.SlugField(verbose_name=_("Слаг"))
    content = models.TextField(verbose_name=_("Содержание"))
    excerpt = models.TextField(blank=True, verbose_name=_("Выдержка"))
    
    # Classification
    category = models.ForeignKey(
        KnowledgeCategory,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name=_("Категория")
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_("Статус"))
    
    # Authorship
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='knowledge_articles',
        verbose_name=_("Автор")
    )
    
    # Tenant
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='knowledge_articles',
        verbose_name=_("Арендатор")
    )
    
    # SEO
    meta_title = models.CharField(max_length=255, blank=True, verbose_name=_("Мета заголовок"))
    meta_description = models.TextField(blank=True, verbose_name=_("Мета описание"))
    keywords = models.CharField(max_length=500, blank=True, verbose_name=_("Ключевые слова"))
    
    # Statistics
    view_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество просмотров"))
    helpful_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество полезных оценок"))
    not_helpful_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество негативных оценок"))
    
    # Timestamps
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата публикации"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    # Custom fields
    custom_fields = models.JSONField(default=dict, verbose_name=_("Пользовательские поля"))
    
    # Tags
    tags = models.ManyToManyField('Tag', blank=True, verbose_name=_("Теги"))
    
    class Meta:
        verbose_name = _("Статья базы знаний")
        verbose_name_plural = _("Статьи базы знаний")
        db_table = 'knowledge_articles'
        ordering = ['-published_at', '-created_at']
        unique_together = ['slug', 'tenant']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class KnowledgeArticleAttachment(models.Model):
    """Knowledge article attachment model."""
    
    article = models.ForeignKey(
        KnowledgeArticle,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_("Статья")
    )
    file = models.FileField(upload_to='knowledge/attachments/', verbose_name=_("Файл"))
    filename = models.CharField(max_length=255, verbose_name=_("Имя файла"))
    file_size = models.BigIntegerField(verbose_name=_("Размер файла"))
    mime_type = models.CharField(max_length=100, verbose_name=_("MIME тип"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    
    class Meta:
        verbose_name = _("Вложение статьи базы знаний")
        verbose_name_plural = _("Вложения статей базы знаний")
        db_table = 'knowledge_article_attachments'
    
    def __str__(self):
        return f"{self.filename} - {self.article.title}"


class KnowledgeArticleRating(models.Model):
    """Knowledge article rating model."""
    
    RATING_CHOICES = [
        (1, _('Очень плохо')),
        (2, _('Плохо')),
        (3, _('Удовлетворительно')),
        (4, _('Хорошо')),
        (5, _('Отлично')),
    ]
    
    article = models.ForeignKey(
        KnowledgeArticle,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name=_("Статья")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='knowledge_ratings',
        verbose_name=_("Пользователь")
    )
    rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Оценка")
    )
    comment = models.TextField(blank=True, verbose_name=_("Комментарий"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Оценка статьи базы знаний")
        verbose_name_plural = _("Оценки статей базы знаний")
        db_table = 'knowledge_article_ratings'
        unique_together = ['article', 'user']
    
    def __str__(self):
        return f"Rating {self.rating} for {self.article.title} by {self.user.username}"


class KnowledgeArticleView(models.Model):
    """Knowledge article view tracking model."""
    
    article = models.ForeignKey(
        KnowledgeArticle,
        on_delete=models.CASCADE,
        related_name='views',
        verbose_name=_("Статья")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='knowledge_views',
        verbose_name=_("Пользователь")
    )
    ip_address = models.GenericIPAddressField(verbose_name=_("IP адрес"))
    user_agent = models.TextField(blank=True, verbose_name=_("Пользовательский агент"))
    viewed_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Время просмотра"))
    
    class Meta:
        verbose_name = _("Просмотр статьи базы знаний")
        verbose_name_plural = _("Просмотры статей базы знаний")
        db_table = 'knowledge_article_views'
        ordering = ['-viewed_at']
    
    def __str__(self):
        return f"View of {self.article.title} at {self.viewed_at}"


class KnowledgeSearch(models.Model):
    """Knowledge base search tracking model."""
    
    query = models.CharField(max_length=255, verbose_name=_("Запрос"))
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='knowledge_searches',
        verbose_name=_("Пользователь")
    )
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='knowledge_searches',
        verbose_name=_("Арендатор")
    )
    results_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество результатов"))
    searched_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Время поиска"))
    
    class Meta:
        verbose_name = _("Поиск в базе знаний")
        verbose_name_plural = _("Поиски в базе знаний")
        db_table = 'knowledge_searches'
        ordering = ['-searched_at']
    
    def __str__(self):
        return f"Search: {self.query} at {self.searched_at}"
