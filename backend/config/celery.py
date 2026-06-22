"""DarsPro — Celery ilovasi (vazifa navbati + beat rejalashtiruvchi)."""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("darspro")
# Barcha CELERY_* sozlamalari settings'dan olinadi
app.config_from_object("django.conf:settings", namespace="CELERY")
# Har app'dagi tasks.py avtomatik topiladi
app.autodiscover_tasks()
