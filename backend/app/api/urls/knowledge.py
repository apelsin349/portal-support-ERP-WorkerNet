"""
URL-маршруты для базы знаний.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.api.views.knowledge import (
    KnowledgeCategoryViewSet,
    KnowledgeArticleViewSet,
    KnowledgeArticleRatingViewSet
)

# Создаем роутер
router = DefaultRouter()
router.register(r'categories', KnowledgeCategoryViewSet, basename='knowledge-category')
router.register(r'articles', KnowledgeArticleViewSet, basename='knowledge-article')
router.register(r'ratings', KnowledgeArticleRatingViewSet, basename='knowledge-rating')

urlpatterns = [
    # Включаем маршруты роутера
    path('', include(router.urls)),
]
