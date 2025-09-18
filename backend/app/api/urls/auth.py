"""
URL-маршруты для аутентификации и авторизации.
"""
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from app.api.views.auth import (
    UserRegistrationView, UserLoginView, UserLogoutView,
    UserProfileView, UserUpdateView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView, TenantListView,
    UserListView, verify_email, user_permissions, refresh_token
)
from app.api.views.auth import CustomTokenObtainPairView

app_name = 'auth'

urlpatterns = [
    # Аутентификация
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    # JWT токены
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/refresh-custom/', refresh_token, name='token_refresh_custom'),
    
    # Профиль пользователя
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UserUpdateView.as_view(), name='profile_update'),
    
    # Смена пароля
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Верификация
    path('verify-email/', verify_email, name='verify_email'),
    
    # Разрешения
    path('permissions/', user_permissions, name='permissions'),
    
    # Тенанты
    path('tenants/', TenantListView.as_view(), name='tenant_list'),
    
    # Пользователи
    path('users/', UserListView.as_view(), name='user_list'),
]
