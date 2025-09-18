"""
URL-маршруты для системы автоматизации.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.api.views.automation import (
    AutomationRuleViewSet, AutomationExecutionViewSet,
    AutomationTemplateViewSet, AutomationScheduleViewSet
)

# Создаем роутер
router = DefaultRouter()
router.register(r'rules', AutomationRuleViewSet, basename='automation-rule')
router.register(r'executions', AutomationExecutionViewSet, basename='automation-execution')
router.register(r'templates', AutomationTemplateViewSet, basename='automation-template')
router.register(r'schedules', AutomationScheduleViewSet, basename='automation-schedule')

urlpatterns = [
    # Включаем маршруты роутера
    path('', include(router.urls)),
]
