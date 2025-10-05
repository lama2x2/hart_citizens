from django.apps import AppConfig


class ActionLogsConfig(AppConfig):
    default_auto_field = 'django.db.models.UUIDField'
    name = 'action_logs'
    verbose_name = 'Логи действий'
