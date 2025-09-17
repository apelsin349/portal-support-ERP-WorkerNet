from django.apps import AppConfig


class AppConfig(AppConfig):
    name = 'app'
    verbose_name = 'Приложение WorkerNet'

    def ready(self):
        # Импортируем модули моделей, чтобы Django зарегистрировал модели из пакета app.models
        try:
            from .models import tenant  # noqa: F401
            from .models import ticket  # noqa: F401
            from .models import knowledge  # noqa: F401
            from .models import chat  # noqa: F401
            from .models import notification  # noqa: F401
        except Exception:
            # Избегаем падений при командах, не требующих загрузки всех моделей
            pass


