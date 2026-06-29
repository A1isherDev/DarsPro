"""DarsPro — to'lov (Payme + Click) testlari (Phase 3)."""
import base64
import hashlib
import uuid

from django.test import override_settings
from rest_framework.test import APITestCase

from apps.payments.models import OrderStatus, PaymentTransaction, PaymeState
from apps.users.models import Subscription, SubscriptionStatus, User

PAYME_KEY = "test-payme-key"
CLICK_SECRET = "test-click-secret"


@override_settings(
    PAYME_MERCHANT_KEY=PAYME_KEY,
    PAYME_MERCHANT_ID="merchant1",
    CLICK_SECRET_KEY=CLICK_SECRET,
    CLICK_SERVICE_ID="svc1",
    CLICK_MERCHANT_ID="mrc1",
)
class PaymeTests(APITestCase):
    URL = "/api/payments/payme/webhook"

    def setUp(self):
        self.user = User.objects.create_user(
            email="pay@x.uz", password="Qwerty!2345"
        )
        self.order = PaymentTransaction.objects.create(
            provider="payme", user=self.user, plan="pro", amount=39000
        )
        self.tiyin = 39000 * 100

    def _post(self, method, params, key=PAYME_KEY, rpc_id=1):
        auth = base64.b64encode(f"Paycom:{key}".encode()).decode()
        return self.client.post(
            self.URL,
            {"method": method, "params": params, "id": rpc_id},
            format="json",
            HTTP_AUTHORIZATION=f"Basic {auth}",
        )

    def _account(self, oid=None):
        return {"order_id": str(oid or self.order.id)}

    def test_happy_path(self):
        r = self._post(
            "CheckPerformTransaction",
            {"amount": self.tiyin, "account": self._account()},
        )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["result"]["allow"])

        r = self._post(
            "CreateTransaction",
            {
                "id": "ptx1",
                "time": 1700000000000,
                "amount": self.tiyin,
                "account": self._account(),
            },
        )
        self.assertEqual(r.json()["result"]["state"], PaymeState.CREATED)

        r = self._post("PerformTransaction", {"id": "ptx1"})
        self.assertEqual(r.json()["result"]["state"], PaymeState.PERFORMED)

        self.user.refresh_from_db()
        self.assertEqual(self.user.plan, "pro")
        self.assertEqual(Subscription.objects.filter(user=self.user).count(), 1)

    def test_wrong_amount(self):
        r = self._post(
            "CheckPerformTransaction",
            {"amount": 12345, "account": self._account()},
        )
        self.assertEqual(r.json()["error"]["code"], -31001)

    def test_unknown_order(self):
        r = self._post(
            "CheckPerformTransaction",
            {"amount": self.tiyin, "account": {"order_id": str(uuid.uuid4())}},
        )
        self.assertEqual(r.json()["error"]["code"], -31050)

    def test_perform_idempotent(self):
        self._post(
            "CreateTransaction",
            {
                "id": "ptx1",
                "time": 1,
                "amount": self.tiyin,
                "account": self._account(),
            },
        )
        r1 = self._post("PerformTransaction", {"id": "ptx1"})
        r2 = self._post("PerformTransaction", {"id": "ptx1"})
        self.assertEqual(
            r1.json()["result"]["perform_time"],
            r2.json()["result"]["perform_time"],
        )
        self.assertEqual(Subscription.objects.filter(user=self.user).count(), 1)

    def test_cancel_after_perform(self):
        self._post(
            "CreateTransaction",
            {
                "id": "ptx1",
                "time": 1,
                "amount": self.tiyin,
                "account": self._account(),
            },
        )
        self._post("PerformTransaction", {"id": "ptx1"})
        r = self._post("CancelTransaction", {"id": "ptx1", "reason": 5})
        self.assertEqual(r.json()["result"]["state"], PaymeState.CANCELLED_AFTER)
        sub = Subscription.objects.get(user=self.user)
        self.assertEqual(sub.status, SubscriptionStatus.CANCELLED)
        self.user.refresh_from_db()
        self.assertEqual(self.user.plan, "free")

    def test_bad_auth(self):
        r = self._post(
            "CheckPerformTransaction",
            {"amount": self.tiyin, "account": self._account()},
            key="wrong-key",
        )
        self.assertEqual(r.json()["error"]["code"], -32504)


@override_settings(
    CLICK_SECRET_KEY=CLICK_SECRET,
    CLICK_SERVICE_ID="svc1",
    CLICK_MERCHANT_ID="mrc1",
)
class ClickTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="click@x.uz", password="Qwerty!2345"
        )
        self.order = PaymentTransaction.objects.create(
            provider="click", user=self.user, plan="start", amount=19000
        )

    def _sign(self, d, prepare):
        fields = ["click_trans_id", "service_id", "secret", "merchant_trans_id"]
        if not prepare:
            fields.append("merchant_prepare_id")
        fields += ["amount", "action", "sign_time"]
        raw = "".join(str({**d, "secret": CLICK_SECRET}.get(f, "")) for f in fields)
        return hashlib.md5(raw.encode()).hexdigest()

    def _base(self, action):
        return {
            "click_trans_id": "ctx1",
            "service_id": "svc1",
            "merchant_trans_id": str(self.order.id),
            "amount": "19000",
            "action": action,
            "sign_time": "2026-06-29 10:00:00",
        }

    def _prepare(self, sign=True):
        d = self._base("0")
        d["sign_string"] = self._sign(d, prepare=True) if sign else "bad"
        return self.client.post("/api/payments/click/prepare", d, format="json")

    def test_prepare_and_complete(self):
        rp = self._prepare()
        self.assertEqual(rp.json()["error"], 0)
        prepare_id = rp.json()["merchant_prepare_id"]

        d = self._base("1")
        d["merchant_prepare_id"] = str(prepare_id)
        d["sign_string"] = self._sign(d, prepare=False)
        rc = self.client.post("/api/payments/click/complete", d, format="json")
        self.assertEqual(rc.json()["error"], 0)

        self.user.refresh_from_db()
        self.assertEqual(self.user.plan, "start")
        self.assertEqual(Subscription.objects.filter(user=self.user).count(), 1)

    def test_invalid_sign(self):
        r = self._prepare(sign=False)
        self.assertEqual(r.json()["error"], -1)
        self.assertEqual(Subscription.objects.count(), 0)

    def test_complete_idempotent(self):
        rp = self._prepare()
        prepare_id = rp.json()["merchant_prepare_id"]
        d = self._base("1")
        d["merchant_prepare_id"] = str(prepare_id)
        d["sign_string"] = self._sign(d, prepare=False)
        self.client.post("/api/payments/click/complete", d, format="json")
        r2 = self.client.post("/api/payments/click/complete", d, format="json")
        self.assertEqual(r2.json()["error"], 0)
        self.assertEqual(Subscription.objects.filter(user=self.user).count(), 1)


class CheckoutTests(APITestCase):
    @override_settings(
        PAYME_MERCHANT_ID="merchant1",
        PAYME_CHECKOUT_URL="https://checkout.paycom.uz",
    )
    def test_checkout_creates_order_and_url(self):
        user = User.objects.create_user(email="co@x.uz", password="Qwerty!2345")
        self.client.force_authenticate(user)
        r = self.client.post(
            "/api/payments/checkout",
            {"plan": "pro", "provider": "payme"},
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertIn("pay_url", r.json())
        self.assertTrue(r.json()["pay_url"].startswith("https://checkout.paycom.uz/"))
        txn = PaymentTransaction.objects.get(id=r.json()["order_id"])
        self.assertEqual(txn.amount, 39000)
        self.assertEqual(txn.order_status, OrderStatus.PENDING)

    def test_checkout_requires_auth(self):
        r = self.client.post(
            "/api/payments/checkout",
            {"plan": "pro", "provider": "payme"},
            format="json",
        )
        self.assertEqual(r.status_code, 401)
