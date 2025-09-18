"""
URL-маршруты для шаблонов ответов.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.api.views.template import (
    ResponseTemplateViewSet, TemplateCategoryViewSet, TemplateVariableViewSet
)

# Создаем роутер
router = DefaultRouter()
router.register(r'templates', ResponseTemplateViewSet, basename='response-template')
router.register(r'categories', TemplateCategoryViewSet, basename='template-category')
router.register(r'variables', TemplateVariableViewSet, basename='template-variable')

urlpatterns = [
    # Включаем маршруты роутера
    path('', include(router.urls)),
]
