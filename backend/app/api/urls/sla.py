"""
URL-маршруты для системы SLA.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.api.views.sla import SLAViewSet, TicketSLAViewSet

# Создаем роутер
router = DefaultRouter()
router.register(r'sla', SLAViewSet, basename='sla')
router.register(r'ticket-sla', TicketSLAViewSet, basename='ticket-sla')

urlpatterns = [
    # Включаем маршруты роутера
    path('', include(router.urls)),
]
