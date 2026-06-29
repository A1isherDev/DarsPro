"""DarsPro — to'lov tranzaksiyalari.

Payme Merchant protokoli tranzaksiyani o'z holat mashinasi bilan saqlashni
talab qiladi (created→performed→cancelled), shu sababli `Subscription` emas,
alohida `PaymentTransaction` modeli kerak. Obuna faqat muvaffaqiyatli to'lovdan
keyin (utils.grant_plan) yaratiladi — mavjud signal user.plan ni sinxronlaydi.
"""
import uuid

from django.db import models


class PaymentProvider(models.TextChoices):
    PAYME = "payme", "Payme"
    CLICK = "click", "Click"


class PaymeState(models.IntegerChoices):
    CREATED = 1, "Yaratilgan"
    PERFORMED = 2, "To'langan"
    CANCELLED = -1, "Bekor (to'lovdan oldin)"
    CANCELLED_AFTER = -2, "Bekor (to'lovdan keyin)"


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Kutilmoqda"
    PAID = "paid", "To'langan"
    CANCELLED = "cancelled", "Bekor qilingan"


class PaymentTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=8, choices=PaymentProvider.choices)
    user = models.ForeignKey(
        "users.User", on_delete=models.PROTECT, related_name="payments"
    )
    plan = models.CharField(max_length=8)  # start | pro | max
    amount = models.BigIntegerField()  # so'mda (tiyin emas)
    duration_days = models.PositiveIntegerField(default=30)
    order_status = models.CharField(
        max_length=10, choices=OrderStatus.choices, default=OrderStatus.PENDING
    )

    # Provayder tomonidagi maydonlar
    provider_txn_id = models.CharField(
        max_length=64, null=True, blank=True, db_index=True
    )
    state = models.IntegerField(null=True, blank=True)  # Payme raqamli holati
    provider_time = models.BigIntegerField(null=True, blank=True)  # epoch-ms / prepare id
    create_time = models.DateTimeField(null=True, blank=True)
    perform_time = models.DateTimeField(null=True, blank=True)
    cancel_time = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.IntegerField(null=True, blank=True)

    subscription = models.ForeignKey(
        "users.Subscription", null=True, blank=True, on_delete=models.SET_NULL
    )
    raw_request = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments_transaction"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_txn_id"],
                name="uq_provider_txn",
                condition=models.Q(provider_txn_id__isnull=False),
            )
        ]
        indexes = [models.Index(fields=["provider", "state"])]

    def __str__(self):
        return f"{self.provider}:{self.plan}:{self.order_status}"
