"""
URL-маршруты для управления инцидентами.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.api.views.incident import IncidentViewSet

# Создаем роутер
router = DefaultRouter()
router.register(r'incidents', IncidentViewSet, basename='incident')

urlpatterns = [
    # Включаем маршруты роутера
    path('', include(router.urls)),
]
