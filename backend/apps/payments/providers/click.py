"""DarsPro — Click (Click Up) Prepare/Complete protokoli.

Sof mantiq — md5 imzo tekshiruvi + buyurtma holatlari. View HTTP qatlamini
qo'shadi. Click form-encoded so'rov yuboradi va `error` maydoni bilan javob
kutadi (0 = muvaffaqiyat).
"""
import hashlib
import hmac

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models import OrderStatus, PaymentTransaction
from ..utils import grant_plan

ACTION_PREPARE = "0"
ACTION_COMPLETE = "1"

# Click xato kodlari
E_OK = 0
E_SIGN = -1
E_AMOUNT = -2
E_ACTION = -3
E_ALREADY_PAID = -4
E_ORDER_NOT_FOUND = -5
E_TXN_NOT_FOUND = -6
E_CANCELLED = -9


def _sign(data, *fields) -> str:
    raw = "".join(str(data.get(f, "")) for f in fields)
    return hashlib.md5(raw.encode()).hexdigest()


def _check_sign(data, prepare=True) -> bool:
    if prepare:
        expected = _sign(
            {**data, "secret": settings.CLICK_SECRET_KEY},
            "click_trans_id",
            "service_id",
            "secret",
            "merchant_trans_id",
            "amount",
            "action",
            "sign_time",
        )
    else:
        expected = _sign(
            {**data, "secret": settings.CLICK_SECRET_KEY},
            "click_trans_id",
            "service_id",
            "secret",
            "merchant_trans_id",
            "merchant_prepare_id",
            "amount",
            "action",
            "sign_time",
        )
    return hmac.compare_digest(expected, str(data.get("sign_string", "")))


def _amount_ok(order, amount) -> bool:
    try:
        return abs(float(amount) - float(order.amount)) < 0.01
    except (TypeError, ValueError):
        return False


def _resp(data, error, note, **extra):
    out = {
        "click_trans_id": data.get("click_trans_id"),
        "merchant_trans_id": data.get("merchant_trans_id"),
        "error": error,
        "error_note": note,
    }
    out.update(extra)
    return out


def build_checkout_url(order_id, amount_somm) -> str:
    return (
        f"{settings.CLICK_CHECKOUT_URL}?service_id={settings.CLICK_SERVICE_ID}"
        f"&merchant_id={settings.CLICK_MERCHANT_ID}"
        f"&amount={amount_somm}&transaction_param={order_id}"
        f"&return_url={settings.PAYMENT_RETURN_URL}"
    )


def _get_order(data):
    oid = data.get("merchant_trans_id")
    try:
        return PaymentTransaction.objects.select_for_update().get(id=oid)
    except (PaymentTransaction.DoesNotExist, ValueError, ValidationError):
        return None


def prepare(data):
    with transaction.atomic():
        if not _check_sign(data, prepare=True):
            return _resp(data, E_SIGN, "SIGN CHECK FAILED")
        order = _get_order(data)
        if order is None:
            return _resp(data, E_ORDER_NOT_FOUND, "Order not found")
        if not _amount_ok(order, data.get("amount")):
            return _resp(data, E_AMOUNT, "Incorrect amount")
        if order.order_status == OrderStatus.PAID:
            return _resp(data, E_ALREADY_PAID, "Already paid")

        prepare_id = int(timezone.now().timestamp())
        order.provider = "click"
        order.provider_txn_id = str(data.get("click_trans_id"))
        order.provider_time = prepare_id
        order.raw_request = dict(data)
        order.save()
        return _resp(
            data, E_OK, "Success", merchant_prepare_id=prepare_id
        )


def complete(data):
    with transaction.atomic():
        if not _check_sign(data, prepare=False):
            return _resp(data, E_SIGN, "SIGN CHECK FAILED")
        order = _get_order(data)
        if order is None:
            return _resp(data, E_ORDER_NOT_FOUND, "Order not found")
        if str(order.provider_time) != str(data.get("merchant_prepare_id")):
            return _resp(data, E_TXN_NOT_FOUND, "Transaction not found")
        if not _amount_ok(order, data.get("amount")):
            return _resp(data, E_AMOUNT, "Incorrect amount")

        # Click o'zi xato bildirsa (error < 0) — bekor qilamiz.
        try:
            click_error = int(data.get("error", 0))
        except (TypeError, ValueError):
            click_error = 0
        if click_error < 0:
            order.order_status = OrderStatus.CANCELLED
            order.cancel_time = timezone.now()
            order.save()
            return _resp(data, E_CANCELLED, "Cancelled")

        if order.order_status == OrderStatus.PAID:  # idempotent
            return _resp(
                data, E_OK, "Success",
                merchant_confirm_id=int(timezone.now().timestamp()),
            )

        grant_plan(order)
        return _resp(
            data, E_OK, "Success",
            merchant_confirm_id=int(timezone.now().timestamp()),
        )
