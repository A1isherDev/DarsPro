"""DarsPro — to'lov view'lari.

- CheckoutView: frontend xaridni boshlaydi (JWT) → pending tranzaksiya +
  provayder checkout URL.
- PaymeWebhookView / ClickWebhookView: provayder webhook'lari — JWT/CSRF/throttle
  YO'Q (provayder o'z auth'ini ishlatadi), idempotent, doim HTTP 200.
"""
import logging

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.plans import plan_price

from .models import OrderStatus, PaymentTransaction
from .providers import click as click_provider
from .providers import payme as payme_provider
from .serializers import CheckoutSerializer, TransactionStatusSerializer

logger = logging.getLogger("apps")


class CheckoutView(APIView):
    """POST /api/payments/checkout — xaridni boshlaydi."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = serializer.validated_data["plan"]
        provider = serializer.validated_data["provider"]
        amount = plan_price(plan)  # server tomonidan — mijozga ishonmaymiz

        txn = PaymentTransaction.objects.create(
            provider=provider,
            user=request.user,
            plan=plan,
            amount=amount,
            duration_days=settings.PAYMENT_PLAN_DURATION_DAYS,
        )
        if provider == "payme":
            pay_url = payme_provider.build_checkout_url(txn.id, amount)
        else:
            pay_url = click_provider.build_checkout_url(txn.id, amount)
        return Response(
            {"order_id": str(txn.id), "pay_url": pay_url},
            status=status.HTTP_201_CREATED,
        )


class TransactionStatusView(APIView):
    """GET /api/payments/orders/{id} — o'z buyurtmasi holatini bilish."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        txn = get_object_or_404(PaymentTransaction, pk=pk, user=request.user)
        return Response(TransactionStatusSerializer(txn).data)


class PaymeWebhookView(APIView):
    """POST /api/payments/payme/webhook — Payme Merchant JSON-RPC."""

    permission_classes = [AllowAny]
    authentication_classes = []  # SimpleJWT/CSRF chetlab o'tiladi
    throttle_classes = []  # provayder IP'sini hech qachon bloklamaymiz

    def post(self, request):
        body = request.data if isinstance(request.data, dict) else {}
        rpc_id = body.get("id")
        if not payme_provider.check_auth(request.META.get("HTTP_AUTHORIZATION", "")):
            return Response(
                {
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "error": {
                        "code": payme_provider.E_AUTH,
                        "message": "Insufficient privilege",
                    },
                }
            )
        try:
            result = payme_provider.handle(body.get("method"), body.get("params"))
            return Response({"jsonrpc": "2.0", "id": rpc_id, "result": result})
        except payme_provider.PaymeError as exc:
            return Response(
                {
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "error": {
                        "code": exc.code,
                        "message": {
                            "ru": exc.message,
                            "uz": exc.message,
                            "en": exc.message,
                        },
                        "data": exc.data,
                    },
                }
            )


class ClickWebhookView(APIView):
    """POST /api/payments/click/{prepare|complete} — Click webhook'lari."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = []
    action = "prepare"

    def post(self, request):
        data = {k: v for k, v in request.data.items()}
        handler = (
            click_provider.complete
            if self.action == "complete"
            else click_provider.prepare
        )
        return Response(handler(data))
