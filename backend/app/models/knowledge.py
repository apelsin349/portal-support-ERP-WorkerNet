"""
Knowledge base models.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class KnowledgeCategory(models.Model):
    """Knowledge base category model."""
    
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_("Parent Category")
    )
    
    # Tenant
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='knowledge_categories',
        verbose_name=_("Tenant")
    )
    
    # Ordering
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    class Meta:
        verbose_name = _("Knowledge Category")
        verbose_name_plural = _("Knowledge Categories")
        db_table = 'knowledge_categories'
        ordering = ['order', 'name']
        unique_together = ['name', 'tenant']
    
    def __str__(self):
        return self.name


class KnowledgeArticle(models.Model):
    """Knowledge base article model."""
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    ]
    
    # Basic information
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    slug = models.SlugField(verbose_name=_("Slug"))
    content = models.TextField(verbose_name=_("Content"))
    excerpt = models.TextField(blank=True, verbose_name=_("Excerpt"))
    
    # Classification
    category = models.ForeignKey(
        KnowledgeCategory,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name=_("Category")
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_("Status"))
    
    # Authorship
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='knowledge_articles',
        verbose_name=_("Author")
    )
    
    # Tenant
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='knowledge_articles',
        verbose_name=_("Tenant")
    )
    
    # SEO
    meta_title = models.CharField(max_length=255, blank=True, verbose_name=_("Meta Title"))
    meta_description = models.TextField(blank=True, verbose_name=_("Meta Description"))
    keywords = models.CharField(max_length=500, blank=True, verbose_name=_("Keywords"))
    
    # Statistics
    view_count = models.PositiveIntegerField(default=0, verbose_name=_("View Count"))
    helpful_count = models.PositiveIntegerField(default=0, verbose_name=_("Helpful Count"))
    not_helpful_count = models.PositiveIntegerField(default=0, verbose_name=_("Not Helpful Count"))
    
    # Timestamps
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Published At"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    # Custom fields
    custom_fields = models.JSONField(default=dict, verbose_name=_("Custom Fields"))
    
    # Tags
    tags = models.ManyToManyField('Tag', blank=True, verbose_name=_("Tags"))
    
    class Meta:
        verbose_name = _("Knowledge Article")
        verbose_name_plural = _("Knowledge Articles")
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
        verbose_name=_("Article")
    )
    file = models.FileField(upload_to='knowledge/attachments/', verbose_name=_("File"))
    filename = models.CharField(max_length=255, verbose_name=_("Filename"))
    file_size = models.BigIntegerField(verbose_name=_("File Size"))
    mime_type = models.CharField(max_length=100, verbose_name=_("MIME Type"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    
    class Meta:
        verbose_name = _("Knowledge Article Attachment")
        verbose_name_plural = _("Knowledge Article Attachments")
        db_table = 'knowledge_article_attachments'
    
    def __str__(self):
        return f"{self.filename} - {self.article.title}"


class KnowledgeArticleRating(models.Model):
    """Knowledge article rating model."""
    
    RATING_CHOICES = [
        (1, _('Very Poor')),
        (2, _('Poor')),
        (3, _('Fair')),
        (4, _('Good')),
        (5, _('Excellent')),
    ]
    
    article = models.ForeignKey(
        KnowledgeArticle,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name=_("Article")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='knowledge_ratings',
        verbose_name=_("User")
    )
    rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Rating")
    )
    comment = models.TextField(blank=True, verbose_name=_("Comment"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    class Meta:
        verbose_name = _("Knowledge Article Rating")
        verbose_name_plural = _("Knowledge Article Ratings")
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
        verbose_name=_("Article")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='knowledge_views',
        verbose_name=_("User")
    )
    ip_address = models.GenericIPAddressField(verbose_name=_("IP Address"))
    user_agent = models.TextField(blank=True, verbose_name=_("User Agent"))
    viewed_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Viewed At"))
    
    class Meta:
        verbose_name = _("Knowledge Article View")
        verbose_name_plural = _("Knowledge Article Views")
        db_table = 'knowledge_article_views'
        ordering = ['-viewed_at']
    
    def __str__(self):
        return f"View of {self.article.title} at {self.viewed_at}"


class KnowledgeSearch(models.Model):
    """Knowledge base search tracking model."""
    
    query = models.CharField(max_length=255, verbose_name=_("Query"))
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='knowledge_searches',
        verbose_name=_("User")
    )
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='knowledge_searches',
        verbose_name=_("Tenant")
    )
    results_count = models.PositiveIntegerField(default=0, verbose_name=_("Results Count"))
    searched_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Searched At"))
    
    class Meta:
        verbose_name = _("Knowledge Search")
        verbose_name_plural = _("Knowledge Searches")
        db_table = 'knowledge_searches'
        ordering = ['-searched_at']
    
    def __str__(self):
        return f"Search: {self.query} at {self.searched_at}"
