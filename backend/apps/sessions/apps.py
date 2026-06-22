from django.apps import AppConfig


class SessionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sessions"
    # django.contrib.sessions ham "sessions" label'ini ishlatadi — to'qnashuvni
    # oldini olish uchun boshqa label beramiz.
    label = "game_sessions"
