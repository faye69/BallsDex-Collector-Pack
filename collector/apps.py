from django.apps import AppConfig


class CollectorConfig(AppConfig):
    name = "collector"
    verbose_name = "Collector"
    default_auto_field = "django.db.models.BigAutoField"
    dpy_package = "collector.collector"
