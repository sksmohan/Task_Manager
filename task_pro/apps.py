from django.apps import AppConfig


class TaskProConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'task_pro'

    def ready(self):
        import task_pro.signals
