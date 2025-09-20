"""
Модели арендатора (мультитенантность) и пользователи.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Менеджер для модели пользователя."""
    
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)


class Tenant(models.Model):
    """Модель арендатора (тенанта) для мультитенантной архитектуры."""
    
    name = models.CharField(max_length=255, verbose_name=_("Название арендатора"))
    slug = models.SlugField(unique=True, verbose_name=_("Слаг"))
    domain = models.CharField(max_length=255, unique=True, verbose_name=_("Домен"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создан"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлён"))
    
    # Configuration
    config = models.JSONField(default=dict, verbose_name=_("Конфигурация"))
    
    # Branding
    logo = models.ImageField(upload_to='tenants/logos/', null=True, blank=True, verbose_name=_("Логотип"))
    primary_color = models.CharField(max_length=7, default='#1976d2', verbose_name=_("Основной цвет"))
    secondary_color = models.CharField(max_length=7, default='#dc004e', verbose_name=_("Дополнительный цвет"))
    
    # Features
    features = models.JSONField(default=dict, verbose_name=_("Фичи"))
    
    class Meta:
        verbose_name = _("Арендатор")
        verbose_name_plural = _("Арендаторы")
        db_table = 'tenants'
    
    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """Расширенная модель пользователя с привязкой к арендатору."""
    
    username = models.CharField(max_length=150, unique=True, verbose_name=_("Имя пользователя"))
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    first_name = models.CharField(max_length=150, blank=True, verbose_name=_("Имя"))
    last_name = models.CharField(max_length=150, blank=True, verbose_name=_("Фамилия"))
    is_staff = models.BooleanField(default=False, verbose_name=_("Сотрудник"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата регистрации"))
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name=_("Арендатор")
    )
    
    # Профиль
    avatar = models.ImageField(upload_to='users/avatars/', null=True, blank=True, verbose_name=_("Аватар"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Телефон"))
    department = models.CharField(max_length=100, blank=True, verbose_name=_("Отдел"))
    position = models.CharField(max_length=100, blank=True, verbose_name=_("Должность"))
    
    # Предпочтения
    preferences = models.JSONField(default=dict, verbose_name=_("Предпочтения"))
    
    # Статус
    is_verified = models.BooleanField(default=False, verbose_name=_("Верифицирован"))
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("IP последнего входа"))
    
    # JWT Reset tokens
    reset_token = models.CharField(max_length=32, null=True, blank=True, verbose_name=_("Токен сброса"))
    reset_token_expires = models.DateTimeField(null=True, blank=True, verbose_name=_("Истечение токена"))
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        db_table = 'users'
        unique_together = ['username', 'tenant']
    
    def __str__(self):
        return f"{self.username} ({self.tenant.name})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name


class TenantConfiguration(models.Model):
    """Настройки арендатора."""
    
    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name='configuration',
        verbose_name=_("Арендатор")
    )
    
    # Общие настройки
    timezone = models.CharField(max_length=50, default='UTC', verbose_name=_("Часовой пояс"))
    language = models.CharField(max_length=10, default='en', verbose_name=_("Язык"))
    date_format = models.CharField(max_length=20, default='%Y-%m-%d', verbose_name=_("Формат даты"))
    time_format = models.CharField(max_length=10, default='24', verbose_name=_("Формат времени"))
    
    # Настройки тикетов
    auto_assign_tickets = models.BooleanField(default=True, verbose_name=_("Автоназначение тикетов"))
    ticket_priority_levels = models.JSONField(default=list, verbose_name=_("Уровни приоритетов"))
    ticket_categories = models.JSONField(default=list, verbose_name=_("Категории тикетов"))
    
    # Настройки SLA
    default_sla_hours = models.IntegerField(default=24, verbose_name=_("Базовый SLA (часы)"))
    escalation_rules = models.JSONField(default=dict, verbose_name=_("Правила эскалации"))
    
    # Уведомления
    email_notifications = models.BooleanField(default=True, verbose_name=_("Уведомления по email"))
    sms_notifications = models.BooleanField(default=False, verbose_name=_("Уведомления по SMS"))
    push_notifications = models.BooleanField(default=True, verbose_name=_("Push-уведомления"))
    
    # Безопасность
    password_policy = models.JSONField(default=dict, verbose_name=_("Политика паролей"))
    session_timeout = models.IntegerField(default=3600, verbose_name=_("Таймаут сессии (сек)"))
    two_factor_required = models.BooleanField(default=False, verbose_name=_("Двухфакторная аутентификация"))
    
    # Интеграции
    ldap_enabled = models.BooleanField(default=False, verbose_name=_("LDAP включён"))
    ldap_config = models.JSONField(default=dict, verbose_name=_("Конфигурация LDAP"))
    sso_enabled = models.BooleanField(default=False, verbose_name=_("SSO включён"))
    sso_config = models.JSONField(default=dict, verbose_name=_("Конфигурация SSO"))
    
    # Пользовательские поля
    custom_fields = models.JSONField(default=dict, verbose_name=_("Пользовательские поля"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    
    class Meta:
        verbose_name = _("Настройки арендатора")
        verbose_name_plural = _("Настройки арендаторов")
        db_table = 'tenant_configurations'
    
    def __str__(self):
        return f"Configuration for {self.tenant.name}"
