"""
API URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import (
    TicketViewSet,
    UserViewSet,
    TenantViewSet,
    HealthView,
)

# Create router
router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'users', UserViewSet, basename='user')
router.register(r'tenants', TenantViewSet, basename='tenant')

urlpatterns = [
    # Health check
    path('health/', HealthView.as_view(), name='health'),
    
    # Include router URLs
    path('', include(router.urls)),
    
    # Authentication URLs
    path('auth/', include('app.api.urls.auth')),

    # Knowledge base URLs
    path('knowledge/', include('app.api.urls.knowledge')),

    # Notification URLs
    path('notifications/', include('app.api.urls.notification')),

    # Chat URLs
    path('chat/', include('app.api.urls.chat')),

    # SLA URLs
    path('sla/', include('app.api.urls.sla')),

    # A/B Testing URLs
    path('ab-testing/', include('app.api.urls.ab_testing')),

    # Incident Management URLs
    path('incidents/', include('app.api.urls.incident')),

    # JWT tokens (legacy)
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
