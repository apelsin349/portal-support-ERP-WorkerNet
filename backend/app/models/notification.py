"""
Notification models for user notifications and delivery tracking.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Notification(models.Model):
    """A notification delivered to a specific user."""

    NOTIFICATION_TYPES = (
        ("ticket", "Ticket"),
        ("system", "System"),
        ("chat", "Chat"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("User"),
    )
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default="system", verbose_name=_("Type"))
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    message = models.TextField(blank=True, verbose_name=_("Message"))
    payload = models.JSONField(default=dict, verbose_name=_("Payload"))
    is_read = models.BooleanField(default=False, db_index=True, verbose_name=_("Is Read"))
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        db_table = "notifications"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id} | {self.type} | {self.title}"

