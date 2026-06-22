"""DarsPro — operatsion tizimlar testlari: health, reconcile_plans, cleanup_sessions."""
from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
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
from apps.sessions.models import GameSession, SessionMode, SessionStatus
from apps.users.models import Plan, Subscription, SubscriptionStatus, User


class HealthTests(APITestCase):
    def test_liveness(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "ok")

    def test_readiness(self):
        resp = self.client.get("/api/health/ready")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["checks"]["database"], "ok")
        self.assertEqual(resp.data["checks"]["cache"], "ok")


class ReconcilePlansTests(TestCase):
    def test_expired_subscription_demotes_user(self):
        user = User.objects.create_user("exp@test.uz", "StrongPass123")
        # Muddati o'tgan obuna — signal user.plan ni pro qiladi
        sub = Subscription.objects.create(
            user=user,
            plan=Plan.PRO,
            expires_at=timezone.now() - timedelta(days=1),
        )
        user.refresh_from_db()
        self.assertEqual(user.plan, Plan.PRO)
        self.assertEqual(user.effective_plan, Plan.FREE)  # o'qishda allaqachon free

        call_command("reconcile_plans", stdout=StringIO())

        user.refresh_from_db()
        sub.refresh_from_db()
        self.assertEqual(user.plan, Plan.FREE)  # saqlangan plan ham free
        self.assertIsNone(user.plan_expires_at)
        self.assertEqual(sub.status, SubscriptionStatus.EXPIRED)

    def test_active_subscription_untouched(self):
        user = User.objects.create_user("act@test.uz", "StrongPass123")
        Subscription.objects.create(
            user=user, plan=Plan.PRO, expires_at=timezone.now() + timedelta(days=10)
        )
        call_command("reconcile_plans", stdout=StringIO())
        user.refresh_from_db()
        self.assertEqual(user.plan, Plan.PRO)


class CeleryTaskTests(TestCase):
    """Eager rejimda (TESTING) task'lar sinxron ishlaydi — simni tekshiramiz."""

    def test_reconcile_task_runs_eagerly(self):
        from apps.users.tasks import reconcile_plans_task

        user = User.objects.create_user("celery@test.uz", "StrongPass123")
        Subscription.objects.create(
            user=user, plan=Plan.PRO, expires_at=timezone.now() - timedelta(days=1)
        )
        result = reconcile_plans_task.delay()  # eager => sinxron bajariladi
        self.assertTrue(result.successful())
        user.refresh_from_db()
        self.assertEqual(user.plan, Plan.FREE)

    def test_cleanup_task_runs_eagerly(self):
        from apps.sessions.tasks import cleanup_sessions_task

        result = cleanup_sessions_task.delay()
        self.assertTrue(result.successful())


class CleanupSessionsTests(TestCase):
    def setUp(self):
        self.host = User.objects.create_user("host-ops@test.uz", "StrongPass123")
        grade = Grade.objects.create(id=9, number=9, label="9-sinf")
        subject = Subject.objects.create(name="Ops", slug="ops")
        topic = Topic.objects.create(subject=subject, grade=grade, title="T", slug="t")
        engine = GameEngine.objects.create(name="Quiz", slug="quiz")
        self.content = ContentItem.objects.create(
            topic=topic, engine=engine, title="C", status=ContentStatus.PUBLISHED,
            data={"questions": [{"text": "q", "options": ["a", "b"], "answer": 0}]},
        )

    def _session(self, status, created_delta=None, ended_delta=None):
        s = GameSession.objects.create(
            content=self.content, host_user=self.host, mode=SessionMode.CLASS, status=status
        )
        updates = {}
        if created_delta is not None:
            updates["created_at"] = timezone.now() + created_delta
        if ended_delta is not None:
            updates["ended_at"] = timezone.now() + ended_delta
        if updates:
            GameSession.objects.filter(id=s.id).update(**updates)
        return s

    def test_stale_ended_and_old_pruned(self):
        stale = self._session(SessionStatus.WAITING, created_delta=timedelta(hours=-8))
        fresh = self._session(SessionStatus.WAITING, created_delta=timedelta(minutes=-10))
        old_ended = self._session(SessionStatus.ENDED, ended_delta=timedelta(days=-40))

        call_command("cleanup_sessions", stdout=StringIO())

        stale.refresh_from_db()
        fresh.refresh_from_db()
        self.assertEqual(stale.status, SessionStatus.ENDED)  # tugatildi
        self.assertEqual(fresh.status, SessionStatus.WAITING)  # tegilmadi
        self.assertFalse(GameSession.objects.filter(id=old_ended.id).exists())  # o'chirildi
