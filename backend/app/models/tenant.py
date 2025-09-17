"""
Tenant models for multitenancy support.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class Tenant(models.Model):
    """Tenant model for multitenancy."""
    
    name = models.CharField(max_length=255, verbose_name=_("Tenant Name"))
    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    domain = models.CharField(max_length=255, unique=True, verbose_name=_("Domain"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    # Configuration
    config = models.JSONField(default=dict, verbose_name=_("Configuration"))
    
    # Branding
    logo = models.ImageField(upload_to='tenants/logos/', null=True, blank=True, verbose_name=_("Logo"))
    primary_color = models.CharField(max_length=7, default='#1976d2', verbose_name=_("Primary Color"))
    secondary_color = models.CharField(max_length=7, default='#dc004e', verbose_name=_("Secondary Color"))
    
    # Features
    features = models.JSONField(default=dict, verbose_name=_("Features"))
    
    class Meta:
        verbose_name = _("Tenant")
        verbose_name_plural = _("Tenants")
        db_table = 'tenants'
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    """Extended User model with tenant support."""
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name=_("Tenant")
    )
    
    # Profile
    avatar = models.ImageField(upload_to='users/avatars/', null=True, blank=True, verbose_name=_("Avatar"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Phone"))
    department = models.CharField(max_length=100, blank=True, verbose_name=_("Department"))
    position = models.CharField(max_length=100, blank=True, verbose_name=_("Position"))
    
    # Preferences
    preferences = models.JSONField(default=dict, verbose_name=_("Preferences"))
    
    # Status
    is_verified = models.BooleanField(default=False, verbose_name=_("Is Verified"))
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("Last Login IP"))
    
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        db_table = 'users'
        unique_together = ['username', 'tenant']
    
    def __str__(self):
        return f"{self.username} ({self.tenant.name})"


class TenantConfiguration(models.Model):
    """Tenant-specific configuration."""
    
    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name='configuration',
        verbose_name=_("Tenant")
    )
    
    # General settings
    timezone = models.CharField(max_length=50, default='UTC', verbose_name=_("Timezone"))
    language = models.CharField(max_length=10, default='en', verbose_name=_("Language"))
    date_format = models.CharField(max_length=20, default='%Y-%m-%d', verbose_name=_("Date Format"))
    time_format = models.CharField(max_length=10, default='24', verbose_name=_("Time Format"))
    
    # Ticket settings
    auto_assign_tickets = models.BooleanField(default=True, verbose_name=_("Auto Assign Tickets"))
    ticket_priority_levels = models.JSONField(default=list, verbose_name=_("Ticket Priority Levels"))
    ticket_categories = models.JSONField(default=list, verbose_name=_("Ticket Categories"))
    
    # SLA settings
    default_sla_hours = models.IntegerField(default=24, verbose_name=_("Default SLA Hours"))
    escalation_rules = models.JSONField(default=dict, verbose_name=_("Escalation Rules"))
    
    # Notification settings
    email_notifications = models.BooleanField(default=True, verbose_name=_("Email Notifications"))
    sms_notifications = models.BooleanField(default=False, verbose_name=_("SMS Notifications"))
    push_notifications = models.BooleanField(default=True, verbose_name=_("Push Notifications"))
    
    # Security settings
    password_policy = models.JSONField(default=dict, verbose_name=_("Password Policy"))
    session_timeout = models.IntegerField(default=3600, verbose_name=_("Session Timeout (seconds)"))
    two_factor_required = models.BooleanField(default=False, verbose_name=_("Two Factor Required"))
    
    # Integration settings
    ldap_enabled = models.BooleanField(default=False, verbose_name=_("LDAP Enabled"))
    ldap_config = models.JSONField(default=dict, verbose_name=_("LDAP Configuration"))
    sso_enabled = models.BooleanField(default=False, verbose_name=_("SSO Enabled"))
    sso_config = models.JSONField(default=dict, verbose_name=_("SSO Configuration"))
    
    # Custom fields
    custom_fields = models.JSONField(default=dict, verbose_name=_("Custom Fields"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    class Meta:
        verbose_name = _("Tenant Configuration")
        verbose_name_plural = _("Tenant Configurations")
        db_table = 'tenant_configurations'
    
    def __str__(self):
        return f"Configuration for {self.tenant.name}"
