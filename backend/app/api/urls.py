"""
API URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TicketViewSet,
    KnowledgeArticleViewSet,
    KnowledgeCategoryViewSet,
    UserViewSet,
    TenantViewSet,
    HealthView,
)

# Create router
router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'knowledge/articles', KnowledgeArticleViewSet, basename='knowledge-article')
router.register(r'knowledge/categories', KnowledgeCategoryViewSet, basename='knowledge-category')
router.register(r'users', UserViewSet, basename='user')
router.register(r'tenants', TenantViewSet, basename='tenant')

urlpatterns = [
    # Health check
    path('health/', HealthView.as_view(), name='health'),
    
    # Include router URLs
    path('', include(router.urls)),
    
    # Authentication
    path('auth/', include('rest_framework_simplejwt.urls')),
]
