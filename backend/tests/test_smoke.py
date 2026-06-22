"""DarsPro — backend MVP smoke testlari (auth, content, sessiya, admin, kvota)."""
from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from apps.content.models import (
    ContentItem,
    ContentStatus,
    GameEngine,
    Grade,
    Subject,
    Topic,
)
from apps.users.models import Plan, Subscription, User


class BaseSetup(APITestCase):
    # Fixtures migratsiyalardan keyin yuklanadi
    fixtures = ["grades.json", "subjects.json", "engines.json"]

    def setUp(self):
        # cache_page katalogni keshlaydi — testlar orasida tozalaymiz
        from django.core.cache import cache

        cache.clear()
        self.subject = Subject.objects.get(slug="biologiya")
        self.grade = Grade.objects.get(pk=7)
        self.engine = GameEngine.objects.get(slug="quiz")
        self.topic = Topic.objects.create(
            subject=self.subject, grade=self.grade, title="Hujayra", slug="hujayra"
        )

    def register(self, email):
        resp = self.client.post(
            "/api/auth/register",
            {"email": email, "password": "StrongPass123", "full_name": "Test"},
            format="json",
        )
        assert resp.status_code == 201, resp.content
        return resp.data["tokens"]["access"]

    def auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


class AuthTests(BaseSetup):
    def test_register_and_me(self):
        token = self.register("a@test.uz")
        # tokensiz -> 401
        self.client.credentials()
        self.assertEqual(self.client.get("/api/users/me").status_code, 401)
        # token bilan -> 200
        self.auth(token)
        resp = self.client.get("/api/users/me")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["email"], "a@test.uz")
        self.assertEqual(resp.data["effective_plan"], "free")


class ContentTests(BaseSetup):
    def test_public_catalog(self):
        self.assertEqual(len(self.client.get("/api/content/grades").data), 11)
        self.assertTrue(len(self.client.get("/api/content/subjects").data) >= 1)
        self.assertTrue(len(self.client.get("/api/content/engines").data) >= 3)

    def test_quota_free_blocked_pro_allowed(self):
        quiz_data = {
            "questions": [
                {"text": "2+2?", "options": ["3", "4", "5"], "answer": 1, "time_limit": 20}
            ]
        }
        payload = {
            "title": "Test quiz",
            "topic": str(self.topic.id),
            "engine": str(self.engine.id),
            "data": quiz_data,
        }
        # free user -> 403 (kvota 0)
        free_token = self.register("free@test.uz")
        self.auth(free_token)
        resp = self.client.post("/api/content/items", payload, format="json")
        self.assertEqual(resp.status_code, 403, resp.content)

        # pro user -> 201, status pending, source teacher
        pro_token = self.register("pro@test.uz")
        pro = User.objects.get(email="pro@test.uz")
        Subscription.objects.create(
            user=pro, plan=Plan.PRO, expires_at=timezone.now() + timedelta(days=30)
        )
        pro.refresh_from_db()
        self.assertEqual(pro.plan, "pro")  # signal sinxronladi
        self.auth(pro_token)
        resp = self.client.post("/api/content/items", payload, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(resp.data["status"], ContentStatus.PENDING)
        self.assertEqual(resp.data["source"], "teacher")

    def test_mine_lists_own_unpublished_and_edit_resets_status(self):
        from apps.content.models import ContentItem, ContentStatus

        pro_token = self.register("mine@test.uz")
        pro = User.objects.get(email="mine@test.uz")
        Subscription.objects.create(
            user=pro, plan=Plan.PRO, expires_at=timezone.now() + timedelta(days=30)
        )
        self.auth(pro_token)
        payload = {
            "title": "Mening quiz",
            "topic": str(self.topic.id),
            "engine": str(self.engine.id),
            "data": {
                "questions": [
                    {"text": "Q?", "options": ["a", "b"], "answer": 0, "time_limit": 20}
                ]
            },
        }
        created = self.client.post("/api/content/items", payload, format="json")
        item_id = created.data["id"]

        # Public ro'yxat pending kontentni ko'rsatmaydi
        self.assertEqual(self.client.get("/api/content/items").data["count"], 0)
        # ?mine=true o'z kontentini ko'rsatadi
        mine = self.client.get("/api/content/items?mine=true")
        self.assertEqual(mine.data["count"], 1)

        # Rad etilganni tahrirlash -> qayta pending
        ContentItem.objects.filter(id=item_id).update(status=ContentStatus.REJECTED)
        patch = self.client.patch(
            f"/api/content/items/{item_id}",
            {"title": "Tuzatildi"},
            format="json",
        )
        self.assertEqual(patch.status_code, 200, patch.content)
        self.assertEqual(
            ContentItem.objects.get(id=item_id).status, ContentStatus.PENDING
        )

        # O'chirish
        self.assertEqual(
            self.client.delete(f"/api/content/items/{item_id}").status_code, 204
        )

    def test_invalid_quiz_data_rejected(self):
        pro_token = self.register("pro2@test.uz")
        pro = User.objects.get(email="pro2@test.uz")
        Subscription.objects.create(
            user=pro, plan=Plan.PRO, expires_at=timezone.now() + timedelta(days=30)
        )
        self.auth(pro_token)
        bad = {
            "title": "Bad",
            "topic": str(self.topic.id),
            "engine": str(self.engine.id),
            "data": {"questions": [{"text": "x", "options": ["a"], "answer": 0}]},
        }
        resp = self.client.post("/api/content/items", bad, format="json")
        self.assertEqual(resp.status_code, 400, resp.content)


class SessionTests(BaseSetup):
    def _published_item(self):
        return ContentItem.objects.create(
            topic=self.topic,
            engine=self.engine,
            title="Sinf quiz",
            status=ContentStatus.PUBLISHED,
            data={"questions": [{"text": "q", "options": ["a", "b"], "answer": 0}]},
        )

    def test_create_and_join(self):
        token = self.register("host@test.uz")
        self.auth(token)
        item = self._published_item()
        resp = self.client.post(
            "/api/sessions/",
            {"content": str(item.id), "mode": "class", "max_players": 10},
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        join_code = resp.data["join_code"]
        self.assertTrue(join_code.startswith("DRS-"))
        session_id = resp.data["id"]

        # o'quvchi auth'siz kiradi
        self.client.credentials()
        join = self.client.post(
            f"/api/sessions/{join_code}/join",
            {"display_name": "Ali"},
            format="json",
        )
        self.assertEqual(join.status_code, 201, join.content)

        # host o'yinni boshlaydi/tugatadi
        self.auth(token)
        self.assertEqual(
            self.client.patch(f"/api/sessions/{session_id}/start").status_code, 200
        )
        self.assertEqual(
            self.client.patch(f"/api/sessions/{session_id}/end").status_code, 200
        )
        results = self.client.get(f"/api/sessions/{session_id}/results")
        self.assertEqual(results.status_code, 200)
        self.assertEqual(results.data["total_players"], 1)

    def test_solo_result_recorded(self):
        token = self.register("solo@test.uz")
        self.auth(token)
        item = self._published_item()
        resp = self.client.post(
            "/api/sessions/solo",
            {"content": str(item.id), "score": 850, "duration_sec": 42},
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        # stats endpoint endi to'ldi
        stats = self.client.get("/api/users/me/stats")
        self.assertEqual(stats.data["total_games"], 1)
        self.assertEqual(stats.data["best_score"], 850)
        # play_count oshdi
        item.refresh_from_db()
        self.assertEqual(item.play_count, 1)

    def test_team_mode_requires_paid_plan(self):
        item = self._published_item()
        # free user -> team rejimi 400
        free_token = self.register("freeteam@test.uz")
        self.auth(free_token)
        resp = self.client.post(
            "/api/sessions/",
            {"content": str(item.id), "mode": "team"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400, resp.content)

        # start user -> team rejimi 201
        start_token = self.register("startteam@test.uz")
        start = User.objects.get(email="startteam@test.uz")
        Subscription.objects.create(
            user=start, plan=Plan.START, expires_at=timezone.now() + timedelta(days=30)
        )
        self.auth(start_token)
        ok = self.client.post(
            "/api/sessions/",
            {"content": str(item.id), "mode": "team", "max_players": 30},
            format="json",
        )
        self.assertEqual(ok.status_code, 201, ok.content)
        self.assertEqual(ok.data["mode"], "team")

    def test_max_players_plan_limit(self):
        token = self.register("host2@test.uz")
        self.auth(token)
        item = self._published_item()
        # free tarif cap = 10, 30 so'rasak -> 400
        resp = self.client.post(
            "/api/sessions/",
            {"content": str(item.id), "mode": "class", "max_players": 30},
            format="json",
        )
        self.assertEqual(resp.status_code, 400, resp.content)


class AdminTests(BaseSetup):
    def test_grant_plan_and_review(self):
        staff = User.objects.create_superuser("staff@test.uz", "StrongPass123")
        teacher = User.objects.create_user("t@test.uz", "StrongPass123")
        item = ContentItem.objects.create(
            topic=self.topic,
            engine=self.engine,
            title="Pending",
            created_by=teacher,
            source="teacher",
            status=ContentStatus.PENDING,
            data={"questions": [{"text": "q", "options": ["a", "b"], "answer": 0}]},
        )
        # staff login
        login = self.client.post(
            "/api/auth/login",
            {"email": "staff@test.uz", "password": "StrongPass123"},
            format="json",
        )
        self.auth(login.data["access"])

        # pending ro'yxati
        pending = self.client.get("/api/admin/items/pending")
        self.assertEqual(pending.status_code, 200)
        self.assertEqual(pending.data["count"], 1)

        # approve
        approve = self.client.patch(f"/api/admin/items/{item.id}/approve")
        self.assertEqual(approve.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.status, ContentStatus.PUBLISHED)

        # manual tarif berish -> signal user.plan
        grant = self.client.patch(
            f"/api/admin/users/{teacher.id}/plan",
            {"plan": "start", "days": 30},
            format="json",
        )
        self.assertEqual(grant.status_code, 200, grant.content)
        teacher.refresh_from_db()
        self.assertEqual(teacher.plan, "start")
