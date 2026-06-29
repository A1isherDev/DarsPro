"""DarsPro — Payme (Paycom) Merchant API protokoli.

Sof mantiq (DRF'siz) — alohida test qilinadi. View faqat HTTP/JSON-RPC
qatlamini va Basic auth'ni qo'shadi.
"""
import base64
import binascii
import hmac

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models import OrderStatus, PaymentTransaction, PaymeState
from ..utils import grant_plan, revoke_plan, to_ms, to_tiyin

ACCOUNT_FIELD = "order_id"


class PaymeError(Exception):
    """JSON-RPC xato (Payme kodlari bilan)."""

    def __init__(self, code: int, message: str, data=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


def _err(code, text, data=None):
    return PaymeError(code, text, data)


# Xato kodlari
E_AUTH = -32504
E_ORDER_NOT_FOUND = -31050
E_WRONG_AMOUNT = -31001
E_CANT_PERFORM = -31008
E_TXN_NOT_FOUND = -31003
E_METHOD = -32601


def check_auth(auth_header: str) -> bool:
    """`Authorization: Basic ...` ni `Paycom:MERCHANT_KEY` bilan solishtiradi."""
    if not auth_header or not auth_header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(auth_header[6:]).decode()
    except (binascii.Error, UnicodeDecodeError):
        return False
    candidates = [settings.PAYME_MERCHANT_KEY]
    if settings.PAYME_TEST_KEY:
        candidates.append(settings.PAYME_TEST_KEY)
    for key in candidates:
        if key and hmac.compare_digest(decoded, f"Paycom:{key}"):
            return True
    return False


def build_checkout_url(order_id, amount_somm) -> str:
    params = (
        f"m={settings.PAYME_MERCHANT_ID};"
        f"ac.{ACCOUNT_FIELD}={order_id};"
        f"a={to_tiyin(amount_somm)}"
    )
    encoded = base64.b64encode(params.encode()).decode()
    return f"{settings.PAYME_CHECKOUT_URL.rstrip('/')}/{encoded}"


def _get_order(params):
    account = params.get("account") or {}
    order_id = account.get(ACCOUNT_FIELD)
    if not order_id:
        raise _err(E_ORDER_NOT_FOUND, "Buyurtma topilmadi", ACCOUNT_FIELD)
    try:
        return PaymentTransaction.objects.select_for_update().get(
            id=order_id, provider="payme"
        )
    except (PaymentTransaction.DoesNotExist, ValueError, ValidationError):
        raise _err(E_ORDER_NOT_FOUND, "Buyurtma topilmadi", ACCOUNT_FIELD)


def _check_amount(order, amount):
    if int(amount) != to_tiyin(order.amount):
        raise _err(E_WRONG_AMOUNT, "Noto'g'ri summa")


def _by_txn(payme_id):
    try:
        return PaymentTransaction.objects.select_for_update().get(
            provider_txn_id=payme_id, provider="payme"
        )
    except PaymentTransaction.DoesNotExist:
        raise _err(E_TXN_NOT_FOUND, "Tranzaksiya topilmadi")


# --- Metodlar -------------------------------------------------------------
def check_perform_transaction(params):
    order = _get_order(params)
    _check_amount(order, params.get("amount"))
    if order.order_status != OrderStatus.PENDING:
        raise _err(E_CANT_PERFORM, "Buyurtma allaqachon yopilgan")
    return {"allow": True}


def create_transaction(params):
    payme_id = params["id"]
    order = _get_order(params)
    # Idempotent: shu Payme id allaqachon bog'langan bo'lsa.
    if order.provider_txn_id == payme_id:
        return {
            "create_time": to_ms(order.create_time),
            "transaction": str(order.id),
            "state": order.state,
        }
    if order.provider_txn_id:  # boshqa tranzaksiya band qilgan
        raise _err(E_CANT_PERFORM, "Buyurtma band")
    _check_amount(order, params.get("amount"))
    if order.order_status != OrderStatus.PENDING:
        raise _err(E_CANT_PERFORM, "Buyurtma allaqachon yopilgan")

    order.provider_txn_id = payme_id
    order.provider_time = params.get("time")
    order.state = PaymeState.CREATED
    order.create_time = timezone.now()
    order.raw_request = params
    order.save()
    return {
        "create_time": to_ms(order.create_time),
        "transaction": str(order.id),
        "state": PaymeState.CREATED.value,
    }


def perform_transaction(params):
    order = _by_txn(params["id"])
    if order.state == PaymeState.PERFORMED:  # idempotent
        return {
            "perform_time": to_ms(order.perform_time),
            "transaction": str(order.id),
            "state": PaymeState.PERFORMED.value,
        }
    if order.state != PaymeState.CREATED:
        raise _err(E_CANT_PERFORM, "Operatsiyani bajarib bo'lmadi")
    order.state = PaymeState.PERFORMED
    order.perform_time = timezone.now()
    order.save()
    grant_plan(order)
    return {
        "perform_time": to_ms(order.perform_time),
        "transaction": str(order.id),
        "state": PaymeState.PERFORMED.value,
    }


def cancel_transaction(params):
    order = _by_txn(params["id"])
    if order.state in (PaymeState.CANCELLED, PaymeState.CANCELLED_AFTER):
        return {
            "cancel_time": to_ms(order.cancel_time),
            "transaction": str(order.id),
            "state": order.state,
        }
    if order.state == PaymeState.PERFORMED:
        order.state = PaymeState.CANCELLED_AFTER
        revoke_plan(order)  # obunani bekor qiladi
    else:
        order.state = PaymeState.CANCELLED
        order.order_status = OrderStatus.CANCELLED
    order.cancel_time = timezone.now()
    order.cancel_reason = params.get("reason")
    order.save()
    return {
        "cancel_time": to_ms(order.cancel_time),
        "transaction": str(order.id),
        "state": order.state,
    }


def check_transaction(params):
    order = _by_txn(params["id"])
    return {
        "create_time": to_ms(order.create_time),
        "perform_time": to_ms(order.perform_time),
        "cancel_time": to_ms(order.cancel_time),
        "transaction": str(order.id),
        "state": order.state,
        "reason": order.cancel_reason,
    }


def get_statement(params):
    frm, to = params.get("from"), params.get("to")
    qs = PaymentTransaction.objects.filter(
        provider="payme",
        provider_txn_id__isnull=False,
        provider_time__gte=frm,
        provider_time__lte=to,
    )
    return {
        "transactions": [
            {
                "id": o.provider_txn_id,
                "time": o.provider_time,
                "amount": to_tiyin(o.amount),
                "account": {ACCOUNT_FIELD: str(o.id)},
                "create_time": to_ms(o.create_time),
                "perform_time": to_ms(o.perform_time),
                "cancel_time": to_ms(o.cancel_time),
                "transaction": str(o.id),
                "state": o.state,
                "reason": o.cancel_reason,
            }
            for o in qs
        ]
    }


_METHODS = {
    "CheckPerformTransaction": check_perform_transaction,
    "CreateTransaction": create_transaction,
    "PerformTransaction": perform_transaction,
    "CancelTransaction": cancel_transaction,
    "CheckTransaction": check_transaction,
    "GetStatement": get_statement,
}


def handle(method, params):
    """Metodni dispatch qiladi. Har biri atomik + qator qulfi bilan ishlaydi."""
    handler = _METHODS.get(method)
    if handler is None:
        raise _err(E_METHOD, "Metod topilmadi")
    with transaction.atomic():
        return handler(params or {})
