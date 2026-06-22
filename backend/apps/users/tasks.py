"""DarsPro — users Celery vazifalari."""
from celery import shared_task
from django.core.management import call_command


@shared_task(name="apps.users.tasks.reconcile_plans_task")
def reconcile_plans_task():
    """Muddati o'tgan obunalarni yakkalaydi (beat orqali har soat)."""
    call_command("reconcile_plans")
