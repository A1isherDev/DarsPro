"""Django startda Celery ilovasini yuklaymiz (shared_task uchun)."""
from .celery import app as celery_app

__all__ = ("celery_app",)
