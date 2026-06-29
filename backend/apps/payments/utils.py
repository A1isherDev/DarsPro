"""DarsPro — to'lov yordamchilari.

`grant_plan` — ikkala provayder (Payme Perform / Click Complete) chaqiradigan
yagona nuqta. Mavjud `Subscription` namunasini (ADR #5) qayta ishlatadi:
obuna yaratiladi → signal user.plan ni sinxronlaydi.
"""
from datetime import timedelta

from django.utils import timezone

from apps.users.models import Subscription, SubscriptionStatus

from .models import OrderStatus


def to_tiyin(somm) -> int:
    return int(somm) * 100


def from_tiyin(tiyin) -> int:
    return int(tiyin) // 100


def to_ms(dt) -> int:
    """DateTime → epoch-ms (Payme formati). None bo'lsa 0."""
    return int(dt.timestamp() * 1000) if dt else 0


def grant_plan(txn):
    """Tranzaksiya bo'yicha obuna yaratadi (yoki mavjud muddatga qo'shadi)."""
    now = timezone.now()
    latest = (
        txn.user.subscriptions.filter(
            status=SubscriptionStatus.ACTIVE, expires_at__gte=now
        )
        .order_by("-expires_at")
        .first()
    )
    base = latest.expires_at if latest else now
    sub = Subscription.objects.create(
        user=txn.user,
        plan=txn.plan,
        expires_at=base + timedelta(days=txn.duration_days),
        payment_ref=f"{txn.provider}:{txn.provider_txn_id}",
    )
    txn.subscription = sub
    txn.order_status = OrderStatus.PAID
    txn.save()
    return sub


def revoke_plan(txn):
    """To'langan tranzaksiya bekor qilinganda obunani bekor qiladi."""
    if txn.subscription_id:
        sub = txn.subscription
        sub.status = SubscriptionStatus.CANCELLED
        sub.save()  # signal user.plan ni qayta sinxronlaydi
    txn.order_status = OrderStatus.CANCELLED
    txn.save()
