"""
URL-маршруты для A/B тестирования.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.api.views.ab_testing import (
    FeatureFlagViewSet, ABTestViewSet, ABTestVariantViewSet,
    ABTestParticipantViewSet, ABTestEventViewSet
)

# Создаем роутер
router = DefaultRouter()
router.register(r'feature-flags', FeatureFlagViewSet, basename='feature-flag')
router.register(r'tests', ABTestViewSet, basename='ab-test')
router.register(r'variants', ABTestVariantViewSet, basename='ab-test-variant')
router.register(r'participants', ABTestParticipantViewSet, basename='ab-test-participant')
router.register(r'events', ABTestEventViewSet, basename='ab-test-event')

urlpatterns = [
    # Включаем маршруты роутера
    path('', include(router.urls)),
]
