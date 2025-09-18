# Пакет моделей
# Импортируем все модели для регистрации в Django
from .tenant import User, Tenant, TenantConfiguration
from .ticket import Ticket, TicketComment, TicketAttachment, Tag, SLA, TicketSLA
from .knowledge import KnowledgeCategory, KnowledgeArticle, KnowledgeArticleAttachment, KnowledgeArticleRating, KnowledgeArticleView, KnowledgeSearch
from .chat import ChatMessage
from .notification import Notification
from .ab_testing import FeatureFlag, ABTest, ABTestVariant, ABTestParticipant, ABTestEvent, ABTestMetric
from .incident import Incident, IncidentUpdate, IncidentAttachment, IncidentTimeline, IncidentEscalation, IncidentSLA
from .template import ResponseTemplate, TemplateVariable, TemplateUsage, TemplateCategory, TemplateVersion
from .rating import TicketRating, AgentRating, ServiceRating, RatingCategory, RatingSurvey, RatingSurveyQuestion, RatingSurveyResponse
from .automation import AutomationRule, AutomationExecution, AutomationCondition, AutomationAction, AutomationTemplate, AutomationSchedule
from .performance import PerformanceMetric, PerformanceAlert, PerformanceTrace, PerformanceDashboard, PerformanceReport, PerformanceThreshold

__all__ = [
    # Tenant models
    'User', 'Tenant', 'TenantConfiguration',
    
    # Ticket models
    'Ticket', 'TicketComment', 'TicketAttachment', 'Tag', 'SLA', 'TicketSLA',
    
    # Knowledge base models
    'KnowledgeCategory', 'KnowledgeArticle', 'KnowledgeArticleAttachment', 'KnowledgeArticleRating', 'KnowledgeArticleView', 'KnowledgeSearch',
    
    # Communication models
    'ChatMessage', 'Notification',
    
    # A/B Testing models
    'FeatureFlag', 'ABTest', 'ABTestVariant', 'ABTestParticipant', 'ABTestEvent', 'ABTestMetric',
    
    # Incident management models
    'Incident', 'IncidentUpdate', 'IncidentAttachment', 'IncidentTimeline', 'IncidentEscalation', 'IncidentSLA',
    
    # Template models
    'ResponseTemplate', 'TemplateVariable', 'TemplateUsage', 'TemplateCategory', 'TemplateVersion',
    
    # Rating models
    'TicketRating', 'AgentRating', 'ServiceRating', 'RatingCategory', 'RatingSurvey', 'RatingSurveyQuestion', 'RatingSurveyResponse',
    
    # Automation models
    'AutomationRule', 'AutomationExecution', 'AutomationCondition', 'AutomationAction', 'AutomationTemplate', 'AutomationSchedule',
    
    # Performance models
    'PerformanceMetric', 'PerformanceAlert', 'PerformanceTrace', 'PerformanceDashboard', 'PerformanceReport', 'PerformanceThreshold',
]
