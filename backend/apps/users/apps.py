from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    label = "users"

    def ready(self):
        # Signal'larni ro'yxatdan o'tkazish (subscription -> user.plan)
        from . import signals  # noqa: F401
