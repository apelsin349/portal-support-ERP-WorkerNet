"""
Представления для аутентификации и авторизации.
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.db import transaction

from app.models import User, Tenant
from app.api.serializers_auth import (
    UserRegistrationSerializer, UserLoginSerializer, CustomTokenObtainPairSerializer,
    UserProfileSerializer, UserUpdateSerializer, PasswordChangeSerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer, TenantSerializer,
    UserListSerializer, RefreshTokenSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """Регистрация нового пользователя."""
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Создание пользователя."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            user = serializer.save()
            
            # Отправка email подтверждения
            self.send_verification_email(user)
        
        return Response({
            'message': 'Пользователь успешно зарегистрирован',
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    
    def send_verification_email(self, user):
        """Отправка email для верификации."""
        # Здесь можно добавить логику отправки email
        pass


class CustomTokenObtainPairView(TokenObtainPairView):
    """Кастомный view для получения JWT токенов."""
    
    serializer_class = CustomTokenObtainPairSerializer


class UserLoginView(APIView):
    """Вход в систему."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Аутентификация пользователя."""
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Создание JWT токенов
        refresh = RefreshToken.for_user(user)
        
        # Логирование входа
        login(request, user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserProfileSerializer(user).data
        })


class UserLogoutView(APIView):
    """Выход из системы."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Выход пользователя."""
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass
        
        logout(request)
        
        return Response({
            'message': 'Успешный выход из системы'
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Профиль пользователя."""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserUpdateView(generics.UpdateAPIView):
    """Обновление профиля пользователя."""
    
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    """Смена пароля."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Смена пароля пользователя."""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Пароль успешно изменен'
        })


class PasswordResetView(APIView):
    """Сброс пароля."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Запрос на сброс пароля."""
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Генерация токена сброса
        reset_token = get_random_string(32)
        user.reset_token = reset_token
        user.reset_token_expires = timezone.now() + timezone.timedelta(hours=1)
        user.save()
        
        # Отправка email с токеном
        self.send_reset_email(user, reset_token)
        
        return Response({
            'message': 'Инструкции по сбросу пароля отправлены на email'
        })
    
    def send_reset_email(self, user, token):
        """Отправка email с токеном сброса."""
        # Здесь можно добавить логику отправки email
        pass


class PasswordResetConfirmView(APIView):
    """Подтверждение сброса пароля."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Подтверждение сброса пароля."""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            user = User.objects.get(
                reset_token=token,
                reset_token_expires__gt=timezone.now(),
                is_active=True
            )
        except User.DoesNotExist:
            return Response({
                'error': 'Неверный или истекший токен'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        user.save()
        
        return Response({
            'message': 'Пароль успешно сброшен'
        })


class TenantListView(generics.ListAPIView):
    """Список активных тенантов."""
    
    serializer_class = TenantSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Tenant.objects.filter(is_active=True)


class UserListView(generics.ListAPIView):
    """Список пользователей тенанта."""
    
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(tenant=self.request.user.tenant)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_email(request):
    """Верификация email пользователя."""
    user = request.user
    
    if user.is_verified:
        return Response({
            'message': 'Email уже верифицирован'
        })
    
    # Здесь можно добавить логику отправки кода верификации
    # и проверки кода
    
    user.is_verified = True
    user.save()
    
    return Response({
        'message': 'Email успешно верифицирован'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_permissions(request):
    """Получение разрешений пользователя."""
    user = request.user
    
    permissions_list = []
    if user.is_superuser:
        permissions_list.append('superuser')
    if user.is_staff:
        permissions_list.append('staff')
    if user.is_verified:
        permissions_list.append('verified')
    
    # Добавляем разрешения на основе ролей
    # Здесь можно добавить логику для кастомных ролей
    
    return Response({
        'permissions': permissions_list,
        'is_superuser': user.is_superuser,
        'is_staff': user.is_staff,
        'is_verified': user.is_verified
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def refresh_token(request):
    """Обновление токена."""
    serializer = RefreshTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    refresh = RefreshToken(serializer.validated_data['refresh'])
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    })
