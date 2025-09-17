"""
Модели чата для службы поддержки и обмена сообщениями в реальном времени.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class ChatMessage(models.Model):
    """Сообщение чата в конкретной комнате."""

    room_name = models.CharField(max_length=200, db_index=True, verbose_name=_("Комната"))
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_messages",
        verbose_name=_("Отправитель"),
    )
    content = models.TextField(verbose_name=_("Содержимое"))
    message_type = models.CharField(max_length=20, default="text", verbose_name=_("Тип сообщения"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Время"))

    class Meta:
        verbose_name = _("Сообщение чата")
        verbose_name_plural = _("Сообщения чата")
        db_table = "chat_messages"
        indexes = [models.Index(fields=["room_name", "timestamp"])]

    def __str__(self) -> str:
        return f"{self.room_name} | {self.sender_id} | {self.timestamp.isoformat()}"

