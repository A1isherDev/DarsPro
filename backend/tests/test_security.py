"""DarsPro — xavfsizlik hardening testlari (H1–H4)."""
import io

from asgiref.sync import async_to_sync
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, TransactionTestCase, override_settings
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.content.models import (
    ContentItem,
    ContentStatus,
    GameEngine,
    Grade,
    Subject,
    Topic,
)
from apps.content.validators import validate_engine_data
from apps.sessions.models import GameSession, SessionMode
from apps.users.models import User
from consumers.middleware import JWTAuthMiddleware
from consumers.routing import websocket_urlpatterns

INMEM = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
LOCMEM = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
GOOD_ORIGIN = [(b"origin", b"http://localhost")]
BAD_ORIGIN = [(b"origin", b"http://evil.example")]


# --- H2: payload limitlari ---
class PayloadLimitTests(TestCase):
    def test_too_many_questions_rejected(self):
        data = {
            "questions": [
                {"text": "q", "options": ["a", "b"], "answer": 0} for _ in range(101)
            ]
        }
        with self.assertRaises(ValidationError):
            validate_engine_data("quiz", data)

    def test_oversized_data_rejected(self):
        big = {"question": "x" * 200000, "options": ["a", "b"]}
        with self.assertRaises(ValidationError):
            validate_engine_data("poll", big)

    def test_too_many_options_rejected(self):
        data = {"questions": [{"text": "q", "options": ["o"] * 9, "answer": 0}]}
        with self.assertRaises(ValidationError):
            validate_engine_data("quiz", data)


# --- H3: parol mustahkamligi ---
class PasswordPolicyTests(APITestCase):
    def test_numeric_password_rejected(self):
        resp = self.client.post(
            "/api/auth/register",
            {"email": "a@test.uz", "password": "29481756", "full_name": "T"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_strong_password_ok(self):
        resp = self.client.post(
            "/api/auth/register",
            {"email": "b@test.uz", "password": "Tuzilma!92xQ", "full_name": "T"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.content)


# --- H4: upload verify ---
class UploadVerifyTests(APITestCase):
    def _auth(self):
        u = User.objects.create_user("up@test.uz", "Tuzilma!92xQ")
        self.client.force_authenticate(u)

    def test_fake_image_rejected(self):
        self._auth()
        fake = SimpleUploadedFile("x.png", b"not a real image", content_type="image/png")
        resp = self.client.post("/api/content/upload", {"file": fake}, format="multipart")
        self.assertEqual(resp.status_code, 400)

    def test_real_image_ok(self):
        from PIL import Image

        self._auth()
        buf = io.BytesIO()
        Image.new("RGB", (8, 8), "red").save(buf, format="PNG")
        img = SimpleUploadedFile("x.png", buf.getvalue(), content_type="image/png")
        resp = self.client.post("/api/content/upload", {"file": img}, format="multipart")
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertIn("/media/uploads/", resp.data["url"])


# --- H1: WebSocket hardening ---
@override_settings(CHANNEL_LAYERS=INMEM, CACHES=LOCMEM)
class WebSocketHardeningTests(TransactionTestCase):
    def setUp(self):
        self.host = User.objects.create_user("wsh@test.uz", "Tuzilma!92xQ")
        grade = Grade.objects.create(id=5, number=5, label="5-sinf")
        subject = Subject.objects.create(name="T", slug="t")
        topic = Topic.objects.create(subject=subject, grade=grade, title="T", slug="t")
        engine = GameEngine.objects.create(name="Quiz", slug="quiz")
        self.content = ContentItem.objects.create(
            topic=topic, engine=engine, title="C", status=ContentStatus.PUBLISHED,
            data={"questions": [{"text": "q", "options": ["a", "b"], "answer": 0}]},
        )
        self.session = GameSession.objects.create(
            content=self.content, host_user=self.host, mode=SessionMode.CLASS,
            max_players=1,
        )
        self.code = self.session.join_code

    def _inner_app(self):
        return JWTAuthMiddleware(URLRouter(websocket_urlpatterns))

    def test_origin_validation(self):
        from config.asgi import application

        async def scenario():
            good = WebsocketCommunicator(
                application, f"/ws/session/{self.code}/", headers=GOOD_ORIGIN
            )
            ok, _ = await good.connect()
            assert ok, "to'g'ri origin qabul qilinishi kerak"
            await good.disconnect()

            bad = WebsocketCommunicator(
                application, f"/ws/session/{self.code}/", headers=BAD_ORIGIN
            )
            ok2, _ = await bad.connect()
            assert not ok2, "begona origin rad etilishi kerak"

        async_to_sync(scenario)()

    def test_max_players_enforced_over_ws(self):
        async def scenario():
            app = self._inner_app()
            p1 = WebsocketCommunicator(app, f"/ws/session/{self.code}/")
            p2 = WebsocketCommunicator(app, f"/ws/session/{self.code}/")
            assert (await p1.connect())[0]
            assert (await p2.connect())[0]

            await p1.send_json_to({"type": "player_join", "display_name": "Ali"})
            await p1.receive_json_from()  # player_joined
            await p2.receive_json_from()  # p2 ham broadcast oladi

            # max_players=1 — ikkinchi o'quvchi rad etiladi
            await p2.send_json_to({"type": "player_join", "display_name": "Vali"})
            ev = await p2.receive_json_from()
            assert ev["type"] == "error"
            await p1.disconnect()
            await p2.disconnect()

        async_to_sync(scenario)()

    def test_display_name_truncated(self):
        async def scenario():
            app = self._inner_app()
            p = WebsocketCommunicator(app, f"/ws/session/{self.code}/")
            assert (await p.connect())[0]
            await p.send_json_to(
                {"type": "player_join", "display_name": "X" * 200}
            )
            ev = await p.receive_json_from()
            assert ev["type"] == "player_joined"
            assert len(ev["display_name"]) == 64
            await p.disconnect()

        async_to_sync(scenario)()
