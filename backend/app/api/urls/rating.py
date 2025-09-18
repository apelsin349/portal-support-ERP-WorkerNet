"""
URL-маршруты для системы рейтингов.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.api.views.rating import (
    TicketRatingViewSet, AgentRatingViewSet, ServiceRatingViewSet,
    RatingSurveyViewSet, RatingSurveyQuestionViewSet, RatingSurveyResponseViewSet,
    RatingCategoryViewSet
)

# Создаем роутер
router = DefaultRouter()
router.register(r'ticket-ratings', TicketRatingViewSet, basename='ticket-rating')
router.register(r'agent-ratings', AgentRatingViewSet, basename='agent-rating')
router.register(r'service-ratings', ServiceRatingViewSet, basename='service-rating')
router.register(r'surveys', RatingSurveyViewSet, basename='rating-survey')
router.register(r'survey-questions', RatingSurveyQuestionViewSet, basename='rating-survey-question')
router.register(r'survey-responses', RatingSurveyResponseViewSet, basename='rating-survey-response')
router.register(r'categories', RatingCategoryViewSet, basename='rating-category')

urlpatterns = [
    # Включаем маршруты роутера
    path('', include(router.urls)),
]
