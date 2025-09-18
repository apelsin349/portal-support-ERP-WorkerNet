"""
URL-маршруты для системы уведомлений.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.api.views.notification import NotificationViewSet

# Создаем роутер
router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    # Включаем маршруты роутера
    path('', include(router.urls)),
]
