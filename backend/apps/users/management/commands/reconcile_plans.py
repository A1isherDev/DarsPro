"""DarsPro — muddati o'tgan obunalarni yakkalash (cron orqali davriy).

`user.effective_plan` o'qish vaqtida muddatni hisobga oladi, lekin saqlangan
`user.plan` eskirib qoladi. Bu buyruq:
  1. Muddati o'tgan active obunalarni `expired` qiladi (signal user.plan ni qayta hisoblaydi),
  2. Xavfsizlik to'ri: hali ham plan != free, lekin plan_expires_at o'tgan foydalanuvchilarni free ga tushiradi.

Cron misol (har soatda):
  0 * * * * cd /app && python manage.py reconcile_plans
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.users.models import Plan, Subscription, SubscriptionStatus, User


class Command(BaseCommand):
    help = "Muddati o'tgan obunalarni expired qiladi va user.plan ni sinxronlaydi."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="O'zgartirmasdan, faqat nima qilinishini ko'rsatadi.",
        )

    def handle(self, *args, **options):
        now = timezone.now()
        dry = options["dry_run"]

        expired_subs = Subscription.objects.filter(
            status=SubscriptionStatus.ACTIVE, expires_at__lt=now
        )
        sub_count = expired_subs.count()

        stale_users = User.objects.exclude(plan=Plan.FREE).filter(
            plan_expires_at__lt=now
        )
        user_count = stale_users.count()

        if dry:
            self.stdout.write(
                f"[dry-run] {sub_count} obuna expired bo'lardi, "
                f"{user_count} foydalanuvchi free ga tushardi."
            )
            return

        with transaction.atomic():
            # Signal har save'da user.plan ni qayta hisoblaydi
            for sub in expired_subs.select_related("user"):
                sub.status = SubscriptionStatus.EXPIRED
                sub.save(update_fields=["status"])

            # Xavfsizlik to'ri (signalsiz qolgan stragglerlar)
            reset = (
                User.objects.exclude(plan=Plan.FREE)
                .filter(plan_expires_at__lt=now)
                .update(plan=Plan.FREE, plan_expires_at=None)
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"{sub_count} obuna expired, {reset} foydalanuvchi free ga tushirildi."
            )
        )
