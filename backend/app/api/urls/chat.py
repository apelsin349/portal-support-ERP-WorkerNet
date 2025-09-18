"""
URL-маршруты для системы чата.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.api.views.chat import ChatMessageViewSet

# Создаем роутер
router = DefaultRouter()
router.register(r'messages', ChatMessageViewSet, basename='chat-message')

urlpatterns = [
    # Включаем маршруты роутера
    path('', include(router.urls)),
]
