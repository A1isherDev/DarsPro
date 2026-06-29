"""DarsPro — pricing, admin dashboard stats va seed_games testlari."""
from datetime import timedelta
from io import StringIO

from django.core.cache import cache
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.content.models import ContentItem, ContentStatus, GameEngine, Grade, Subject, Topic
from apps.users.models import Plan, Subscription, User


class PlansEndpointTests(APITestCase):
    def test_plans_public(self):
        """GET /api/users/plans auth'siz 4 ta tarif qaytaradi."""
        resp = self.client.get("/api/users/plans")
        self.assertEqual(resp.status_code, 200)
        plans = resp.data["plans"]
        self.assertEqual([p["slug"] for p in plans], ["free", "start", "pro", "max"])
        pro = next(p for p in plans if p["slug"] == "pro")
        self.assertEqual(pro["price"], 39000)
        self.assertTrue(pro["highlight"])
        self.assertTrue(len(pro["features"]) > 0)


class AdminStatsTests(APITestCase):
    fixtures = ["grades.json", "subjects.json", "engines.json"]

    def setUp(self):
        cache.clear()
        self.staff = User.objects.create_superuser("admin@test.uz", "StrongPass123")
        self.topic = Topic.objects.create(
            subject=Subject.objects.get(slug="biologiya"),
            grade=Grade.objects.get(pk=7),
            title="Hujayra",
            slug="hujayra",
        )
        self.engine = GameEngine.objects.get(slug="quiz")

    def _login(self, email, password="StrongPass123"):
        resp = self.client.post(
            "/api/auth/login", {"email": email, "password": password}, format="json"
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")

    def test_stats_requires_admin(self):
        teacher = User.objects.create_user("t@test.uz", "StrongPass123")
        self._login("t@test.uz")
        self.assertEqual(self.client.get("/api/admin/stats").status_code, 403)

    def test_stats_computes_blocks_and_mrr(self):
        # Ikki obunali foydalanuvchi (pro + start) -> MRR = 39000 + 19000
        for em, pl in [("o1@test.uz", Plan.PRO), ("o2@test.uz", Plan.START)]:
            u = User.objects.create_user(em, "StrongPass123")
            Subscription.objects.create(
                user=u, plan=pl, expires_at=timezone.now() + timedelta(days=20)
            )
        # Bitta published kontent
        ContentItem.objects.create(
            topic=self.topic, engine=self.engine, title="Q",
            status=ContentStatus.PUBLISHED, play_count=5,
            data={"questions": [{"text": "q", "options": ["a", "b"], "answer": 0}]},
        )

        self._login("admin@test.uz")
        resp = self.client.get("/api/admin/stats")
        self.assertEqual(resp.status_code, 200, resp.content)
        d = resp.data

        # Bloklar mavjud
        for key in ("users", "subscriptions", "content", "sessions"):
            self.assertIn(key, d)

        self.assertEqual(d["subscriptions"]["active"], 2)
        self.assertEqual(d["subscriptions"]["mrr"], 39000 + 19000)
        self.assertEqual(d["subscriptions"]["by_plan"], {"pro": 1, "start": 1})

        self.assertEqual(d["content"]["total"], 1)
        self.assertEqual(d["content"]["by_status"]["published"], 1)
        self.assertEqual(d["content"]["by_engine"]["quiz"], 1)
        self.assertEqual(d["content"]["total_plays"], 5)
        self.assertEqual(len(d["content"]["top_played"]), 1)

        # signal user.plan ni sinxronladi -> users.by_plan da ko'rinadi
        self.assertEqual(d["users"]["by_plan"].get("pro"), 1)


class SeedGamesCommandTests(APITestCase):
    fixtures = ["grades.json", "subjects.json", "engines.json"]

    def test_seed_creates_100_and_idempotent(self):
        out = StringIO()
        call_command("seed_games", stdout=out)
        seeded = ContentItem.objects.filter(source="staff", status="published")
        self.assertEqual(seeded.count(), 100)
        # 11 engine ham qamrab olingan
        engines = set(seeded.values_list("engine__slug", flat=True))
        self.assertEqual(len(engines), 11)

        # Qayta ishga tushirish dublikat yaratmaydi
        call_command("seed_games", stdout=StringIO())
        self.assertEqual(
            ContentItem.objects.filter(source="staff", status="published").count(), 100
        )
