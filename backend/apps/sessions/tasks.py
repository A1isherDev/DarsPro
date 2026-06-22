"""DarsPro — sessions Celery vazifalari."""
from celery import shared_task
from django.core.management import call_command


@shared_task(name="apps.sessions.tasks.cleanup_sessions_task")
def cleanup_sessions_task():
    """Tashlab ketilgan sessiyalarni tozalaydi (beat orqali har 30 daqiqada)."""
    call_command("cleanup_sessions")
