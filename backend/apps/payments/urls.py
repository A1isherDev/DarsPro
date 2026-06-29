"""DarsPro — /api/payments/ marshrutlari."""
from django.urls import path

from .views import (
    CheckoutView,
    ClickWebhookView,
    PaymeWebhookView,
    TransactionStatusView,
)

urlpatterns = [
    path("checkout", CheckoutView.as_view(), name="checkout"),
    path("orders/<uuid:pk>", TransactionStatusView.as_view(), name="order-status"),
    path("payme/webhook", PaymeWebhookView.as_view(), name="payme-webhook"),
    path(
        "click/prepare",
        ClickWebhookView.as_view(action="prepare"),
        name="click-prepare",
    ),
    path(
        "click/complete",
        ClickWebhookView.as_view(action="complete"),
        name="click-complete",
    ),
]
