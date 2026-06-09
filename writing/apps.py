from django.apps import AppConfig


class WritingConfig(AppConfig):
    name = 'writing'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        import writing.signals  # noqa — registers post_save receivers
