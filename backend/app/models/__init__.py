# Пакет моделей
# Импортируем все модели для регистрации в Django
from .tenant import User, Tenant, TenantConfiguration
from .ticket import Ticket, TicketComment, TicketAttachment, Tag, SLA, TicketSLA
from .knowledge import KnowledgeCategory, KnowledgeArticle, KnowledgeArticleAttachment, KnowledgeArticleRating, KnowledgeArticleView, KnowledgeSearch
from .chat import ChatMessage
from .notification import Notification

__all__ = [
    'User', 'Tenant', 'TenantConfiguration',
    'Ticket', 'TicketComment', 'TicketAttachment', 'Tag', 'SLA', 'TicketSLA',
    'KnowledgeCategory', 'KnowledgeArticle', 'KnowledgeArticleAttachment', 'KnowledgeArticleRating', 'KnowledgeArticleView', 'KnowledgeSearch',
    'ChatMessage',
    'Notification',
]
