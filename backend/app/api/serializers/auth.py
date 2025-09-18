"""
Сериализаторы для аутентификации и авторизации.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from app.models import User, Tenant


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    tenant_slug = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'tenant_slug',
            'phone', 'department', 'position'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        """Валидация данных регистрации."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        
        # Проверяем существование тенанта
        try:
            tenant = Tenant.objects.get(slug=attrs['tenant_slug'], is_active=True)
        except Tenant.DoesNotExist:
            raise serializers.ValidationError("Тенант не найден или неактивен")
        
        attrs['tenant'] = tenant
        return attrs
    
    def create(self, validated_data):
        """Создание пользователя."""
        validated_data.pop('password_confirm')
        validated_data.pop('tenant_slug')
        
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для входа в систему."""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    tenant_slug = serializers.CharField(required=False)
    
    def validate(self, attrs):
        """Валидация данных входа."""
        username = attrs.get('username')
        password = attrs.get('password')
        tenant_slug = attrs.get('tenant_slug')
        
        if not username or not password:
            raise serializers.ValidationError("Необходимо указать имя пользователя и пароль")
        
        # Аутентификация пользователя
        user = authenticate(username=username, password=password)
        
        if not user:
            raise serializers.ValidationError("Неверные учетные данные")
        
        if not user.is_active:
            raise serializers.ValidationError("Аккаунт деактивирован")
        
        # Проверка тенанта, если указан
        if tenant_slug:
            if user.tenant.slug != tenant_slug:
                raise serializers.ValidationError("Пользователь не принадлежит указанному тенанту")
        
        attrs['user'] = user
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный сериализатор для JWT токенов."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tenant_slug'] = serializers.CharField(required=False)
    
    def validate(self, attrs):
        """Валидация с учетом тенанта."""
        data = super().validate(attrs)
        
        # Добавляем информацию о пользователе в токен
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        
        # Добавляем информацию о пользователе
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'tenant': {
                'id': self.user.tenant.id,
                'name': self.user.tenant.name,
                'slug': self.user.tenant.slug,
            }
        }
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя."""
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    tenant_slug = serializers.CharField(source='tenant.slug', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'department', 'position', 'avatar',
            'is_verified', 'date_joined', 'last_login',
            'tenant_name', 'tenant_slug'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля пользователя."""
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name',
            'phone', 'department', 'position', 'avatar'
        ]
    
    def validate_email(self, value):
        """Валидация email."""
        if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """Сериализатор для смены пароля."""
    
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Валидация смены пароля."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Новые пароли не совпадают")
        return attrs
    
    def validate_old_password(self, value):
        """Проверка старого пароля."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный старый пароль")
        return value


class PasswordResetSerializer(serializers.Serializer):
    """Сериализатор для сброса пароля."""
    
    email = serializers.EmailField()
    tenant_slug = serializers.CharField(required=False)
    
    def validate(self, attrs):
        """Валидация сброса пароля."""
        email = attrs.get('email')
        tenant_slug = attrs.get('tenant_slug')
        
        try:
            if tenant_slug:
                user = User.objects.get(email=email, tenant__slug=tenant_slug, is_active=True)
            else:
                user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким email не найден")
        
        attrs['user'] = user
        return attrs


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Сериализатор для подтверждения сброса пароля."""
    
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        """Валидация подтверждения сброса пароля."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs


class TenantSerializer(serializers.ModelSerializer):
    """Сериализатор тенанта."""
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'domain', 'is_active',
            'primary_color', 'secondary_color', 'logo'
        ]
        read_only_fields = ['id', 'slug']


class UserListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка пользователей."""
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'department', 'position', 'is_active', 'is_verified',
            'date_joined', 'last_login', 'tenant_name'
        ]


class RefreshTokenSerializer(serializers.Serializer):
    """Сериализатор для обновления токена."""
    
    refresh = serializers.CharField()
    
    def validate_refresh(self, value):
        """Валидация refresh токена."""
        try:
            RefreshToken(value)
        except Exception:
            raise serializers.ValidationError("Неверный refresh токен")
        return value
