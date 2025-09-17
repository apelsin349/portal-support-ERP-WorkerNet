"""
Ticket models for support system.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Ticket(models.Model):
    """Support ticket model."""
    
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
        ('critical', _('Critical')),
    ]
    
    STATUS_CHOICES = [
        ('open', _('Open')),
        ('in_progress', _('In Progress')),
        ('pending', _('Pending')),
        ('resolved', _('Resolved')),
        ('closed', _('Closed')),
        ('cancelled', _('Cancelled')),
    ]
    
    CATEGORY_CHOICES = [
        ('technical', _('Technical')),
        ('billing', _('Billing')),
        ('general', _('General')),
        ('bug_report', _('Bug Report')),
        ('feature_request', _('Feature Request')),
        ('other', _('Other')),
    ]
    
    # Basic information
    ticket_id = models.CharField(max_length=20, unique=True, verbose_name=_("Ticket ID"))
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"))
    
    # Classification
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name=_("Priority"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name=_("Status"))
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general', verbose_name=_("Category"))
    
    # Assignment
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tickets',
        verbose_name=_("Created By")
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name=_("Assigned To")
    )
    
    # Tenant
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name=_("Tenant")
    )
    
    # SLA
    sla_hours = models.IntegerField(default=24, verbose_name=_("SLA Hours"))
    due_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Due Date"))
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Resolved At"))
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    # Custom fields
    custom_fields = models.JSONField(default=dict, verbose_name=_("Custom Fields"))
    
    # Tags
    tags = models.ManyToManyField('Tag', blank=True, verbose_name=_("Tags"))
    
    class Meta:
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")
        db_table = 'tickets'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.ticket_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_id = self.generate_ticket_id()
        super().save(*args, **kwargs)
    
    def generate_ticket_id(self):
        """Generate unique ticket ID."""
        import uuid
        return f"TK-{uuid.uuid4().hex[:8].upper()}"


class TicketComment(models.Model):
    """Ticket comment model."""
    
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_("Ticket")
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ticket_comments',
        verbose_name=_("Author")
    )
    content = models.TextField(verbose_name=_("Content"))
    is_internal = models.BooleanField(default=False, verbose_name=_("Is Internal"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    class Meta:
        verbose_name = _("Ticket Comment")
        verbose_name_plural = _("Ticket Comments")
        db_table = 'ticket_comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on {self.ticket.ticket_id} by {self.author.username}"


class TicketAttachment(models.Model):
    """Ticket attachment model."""
    
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_("Ticket")
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ticket_attachments',
        verbose_name=_("Uploaded By")
    )
    file = models.FileField(upload_to='tickets/attachments/', verbose_name=_("File"))
    filename = models.CharField(max_length=255, verbose_name=_("Filename"))
    file_size = models.BigIntegerField(verbose_name=_("File Size"))
    mime_type = models.CharField(max_length=100, verbose_name=_("MIME Type"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    
    class Meta:
        verbose_name = _("Ticket Attachment")
        verbose_name_plural = _("Ticket Attachments")
        db_table = 'ticket_attachments'
    
    def __str__(self):
        return f"{self.filename} - {self.ticket.ticket_id}"


class Tag(models.Model):
    """Tag model for tickets."""
    
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Name"))
    color = models.CharField(max_length=7, default='#1976d2', verbose_name=_("Color"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        db_table = 'tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class SLA(models.Model):
    """Service Level Agreement model."""
    
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    # Response time (in hours)
    response_time = models.IntegerField(verbose_name=_("Response Time (hours)"))
    
    # Resolution time (in hours)
    resolution_time = models.IntegerField(verbose_name=_("Resolution Time (hours)"))
    
    # Priority mapping
    priority = models.CharField(max_length=20, choices=Ticket.PRIORITY_CHOICES, verbose_name=_("Priority"))
    
    # Tenant
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='slas',
        verbose_name=_("Tenant")
    )
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    class Meta:
        verbose_name = _("SLA")
        verbose_name_plural = _("SLAs")
        db_table = 'slas'
        unique_together = ['tenant', 'priority']
    
    def __str__(self):
        return f"{self.name} - {self.priority}"


class TicketSLA(models.Model):
    """Ticket SLA tracking model."""
    
    ticket = models.OneToOneField(
        Ticket,
        on_delete=models.CASCADE,
        related_name='sla_tracking',
        verbose_name=_("Ticket")
    )
    sla = models.ForeignKey(
        SLA,
        on_delete=models.CASCADE,
        related_name='ticket_slas',
        verbose_name=_("SLA")
    )
    
    # Timestamps
    first_response_at = models.DateTimeField(null=True, blank=True, verbose_name=_("First Response At"))
    resolution_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Resolution At"))
    
    # Status
    is_breached = models.BooleanField(default=False, verbose_name=_("Is Breached"))
    breach_reason = models.TextField(blank=True, verbose_name=_("Breach Reason"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    class Meta:
        verbose_name = _("Ticket SLA")
        verbose_name_plural = _("Ticket SLAs")
        db_table = 'ticket_slas'
    
    def __str__(self):
        return f"SLA for {self.ticket.ticket_id}"
