"""
URL-маршруты для системы мониторинга производительности.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.api.views.performance import (
    PerformanceMetricViewSet, PerformanceAlertViewSet,
    PerformanceTraceViewSet, PerformanceDashboardViewSet,
    PerformanceReportViewSet, PerformanceThresholdViewSet
)

# Создаем роутер
router = DefaultRouter()
router.register(r'metrics', PerformanceMetricViewSet, basename='performance-metric')
router.register(r'alerts', PerformanceAlertViewSet, basename='performance-alert')
router.register(r'traces', PerformanceTraceViewSet, basename='performance-trace')
router.register(r'dashboards', PerformanceDashboardViewSet, basename='performance-dashboard')
router.register(r'reports', PerformanceReportViewSet, basename='performance-report')
router.register(r'thresholds', PerformanceThresholdViewSet, basename='performance-threshold')

urlpatterns = [
    # Включаем маршруты роутера
    path('', include(router.urls)),
]
