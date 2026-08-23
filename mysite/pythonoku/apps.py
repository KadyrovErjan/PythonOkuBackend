from django.apps import AppConfig


class PythonOkuConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pythonoku'

    def ready(self):
        from . import signals  # noqa: F401
