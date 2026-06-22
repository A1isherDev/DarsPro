"""DarsPro — Subscription o'zgarganda user.plan ni sinxronlash (ADR #5)."""
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Plan, Subscription, SubscriptionStatus


def _sync_user_plan(user):
    """Foydalanuvchining eng so'nggi faol obunasiga qarab user.plan ni yangilaydi."""
    active = (
        user.subscriptions.filter(status=SubscriptionStatus.ACTIVE)
        .order_by("-expires_at")
        .first()
    )
    if active:
        user.plan = active.plan
        user.plan_expires_at = active.expires_at
    else:
        user.plan = Plan.FREE
        user.plan_expires_at = None
    user.save(update_fields=["plan", "plan_expires_at"])


@receiver(post_save, sender=Subscription)
def subscription_saved(sender, instance, **kwargs):
    _sync_user_plan(instance.user)


@receiver(post_delete, sender=Subscription)
def subscription_deleted(sender, instance, **kwargs):
    _sync_user_plan(instance.user)
