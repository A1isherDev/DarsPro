"""DarsPro — sessiya gigienasi (cron orqali davriy).

  1. Tashlab ketilgan waiting/active sessiyalarni (--stale-hours dan eski) tugatadi.
  2. Juda eski ended sessiyalarni (--prune-days dan eski) o'chiradi
     (GameParticipant cascade orqali tozalanadi).

Cron misol (har 30 daqiqada):
  */30 * * * * cd /app && python manage.py cleanup_sessions
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.sessions.models import GameSession, SessionStatus


class Command(BaseCommand):
    help = "Tashlab ketilgan sessiyalarni tugatadi va eski yozuvlarni o'chiradi."

    def add_arguments(self, parser):
        parser.add_argument("--stale-hours", type=int, default=6)
        parser.add_argument("--prune-days", type=int, default=30)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        now = timezone.now()
        stale_before = now - timedelta(hours=options["stale_hours"])
        prune_before = now - timedelta(days=options["prune_days"])
        dry = options["dry_run"]

        stale = GameSession.objects.filter(
            status__in=[SessionStatus.WAITING, SessionStatus.ACTIVE],
            created_at__lt=stale_before,
        )
        prune = GameSession.objects.filter(
            status=SessionStatus.ENDED, ended_at__lt=prune_before
        )
        stale_n, prune_n = stale.count(), prune.count()

        if dry:
            self.stdout.write(
                f"[dry-run] {stale_n} sessiya tugatilardi, {prune_n} ta o'chirilardi."
            )
            return

        stale.update(status=SessionStatus.ENDED, ended_at=now)
        deleted, _ = prune.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"{stale_n} sessiya tugatildi, {prune_n} eski sessiya o'chirildi."
            )
        )
