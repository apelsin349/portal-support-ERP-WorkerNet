"""
Модели уведомлений для пользователей и учёт статуса доставки.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Notification(models.Model):
    """Уведомление, доставленное конкретному пользователю."""

    NOTIFICATION_TYPES = (
        ("ticket", "Тикет"),
        ("system", "Система"),
        ("chat", "Чат"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Пользователь"),
    )
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default="system", verbose_name=_("Тип"))
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    message = models.TextField(blank=True, verbose_name=_("Сообщение"))
    payload = models.JSONField(default=dict, verbose_name=_("Данные"))
    is_read = models.BooleanField(default=False, db_index=True, verbose_name=_("Прочитано"))
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("Создано"))

    class Meta:
        verbose_name = _("Уведомление")
        verbose_name_plural = _("Уведомления")
        db_table = "notifications"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id} | {self.type} | {self.title}"

