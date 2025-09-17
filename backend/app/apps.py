from django.apps import AppConfig


class AppConfig(AppConfig):
    name = 'app'
    verbose_name = 'Приложение WorkerNet'

    def ready(self):
        # Импортируем модели для регистрации в Django
        try:
            from .models import *  # noqa: F401, F403
        except Exception:
            # Избегаем падений при командах, не требующих загрузки всех моделей
            pass


