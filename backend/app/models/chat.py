"""
Chat models for support chat and real-time messaging.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class ChatMessage(models.Model):
    """Represents a single chat message in a room."""

    room_name = models.CharField(max_length=200, db_index=True, verbose_name=_("Room Name"))
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_messages",
        verbose_name=_("Sender"),
    )
    content = models.TextField(verbose_name=_("Content"))
    message_type = models.CharField(max_length=20, default="text", verbose_name=_("Message Type"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Timestamp"))

    class Meta:
        verbose_name = _("Chat Message")
        verbose_name_plural = _("Chat Messages")
        db_table = "chat_messages"
        indexes = [models.Index(fields=["room_name", "timestamp"])]

    def __str__(self) -> str:
        return f"{self.room_name} | {self.sender_id} | {self.timestamp.isoformat()}"

