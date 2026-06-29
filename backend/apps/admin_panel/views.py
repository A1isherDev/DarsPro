"""DarsPro — staff (admin) view'lari."""
from datetime import timedelta

from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import ContentItem, ContentStatus
from apps.content.serializers import ContentItemListSerializer
from apps.users.models import Subscription, SubscriptionStatus, User
from apps.users.plans import PLAN_PRICING, plan_price

from .serializers import AdminUserSerializer, GrantPlanSerializer


def _counts_by(qs, field):
    """{field_value: count} lug'atini qaytaradi (None kalitlarsiz)."""
    rows = qs.values(field).annotate(n=Count("id"))
    return {row[field]: row["n"] for row in rows if row[field] is not None}


class AdminStatsView(APIView):
    """GET /api/admin/stats — admin dashboard uchun jamlangan ko'rsatkichlar.

    Hammasi DB aggregatsiyasi orqali hisoblanadi. Yangi model/migration yo'q.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        from apps.sessions.models import (
            GameParticipant,
            GameSession,
            UserGame,
        )

        now = timezone.now()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # — Foydalanuvchilar —
        users = User.objects.all()
        users_by_plan = _counts_by(users, "plan")
        users_block = {
            "total": users.count(),
            "by_plan": users_by_plan,
            "staff": users.filter(is_staff=True).count(),
            "new_today": users.filter(created_at__gte=day_ago).count(),
            "new_week": users.filter(created_at__gte=week_ago).count(),
            "new_month": users.filter(created_at__gte=month_ago).count(),
        }

        # — Obunalar (faol = active status va muddati o'tmagan) —
        active_subs = Subscription.objects.filter(
            status=SubscriptionStatus.ACTIVE, expires_at__gte=now
        )
        subs_by_plan = _counts_by(active_subs, "plan")
        mrr = sum(plan_price(plan) * n for plan, n in subs_by_plan.items())
        subs_block = {
            "active": active_subs.count(),
            "by_plan": subs_by_plan,
            "expiring_week": active_subs.filter(expires_at__lte=now + timedelta(days=7)).count(),
            "mrr": mrr,
            "pricing": {p["slug"]: p["price"] for p in PLAN_PRICING.values()},
        }

        # — Kontent —
        items = ContentItem.objects.all()
        top_played = list(
            items.filter(play_count__gt=0)
            .order_by("-play_count")
            .values("id", "title", "play_count")[:5]
        )
        content_block = {
            "total": items.count(),
            "by_status": _counts_by(items, "status"),
            "by_engine": _counts_by(items, "engine__slug"),
            "pending": items.filter(status=ContentStatus.PENDING).count(),
            "total_plays": items.aggregate(s=Sum("play_count"))["s"] or 0,
            "top_played": [
                {"id": str(t["id"]), "title": t["title"], "play_count": t["play_count"]}
                for t in top_played
            ],
        }

        # — Sessiyalar —
        sessions = GameSession.objects.all()
        sessions_block = {
            "total": sessions.count(),
            "by_mode": _counts_by(sessions, "mode"),
            "by_status": _counts_by(sessions, "status"),
            "week": sessions.filter(created_at__gte=week_ago).count(),
            "participants": GameParticipant.objects.count(),
            "solo_games": UserGame.objects.count(),
        }

        return Response(
            {
                "users": users_block,
                "subscriptions": subs_block,
                "content": content_block,
                "sessions": sessions_block,
                "generated_at": now.isoformat(),
            }
        )


class PendingItemsView(generics.ListAPIView):
    """GET /api/admin/items/pending — review navbati."""

    serializer_class = ContentItemListSerializer
    permission_classes = [IsAdminUser]
    queryset = (
        ContentItem.objects.filter(status=ContentStatus.PENDING)
        .select_related("engine", "topic")
        .order_by("created_at")
    )


class ApproveItemView(APIView):
    """PATCH /api/admin/items/{id}/approve — tasdiqlash."""

    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        item = get_object_or_404(ContentItem, pk=pk)
        item.status = ContentStatus.PUBLISHED
        item.save(update_fields=["status"])
        return Response({"id": str(item.id), "status": item.status})


class RejectItemView(APIView):
    """PATCH /api/admin/items/{id}/reject — rad etish."""

    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        item = get_object_or_404(ContentItem, pk=pk)
        item.status = ContentStatus.REJECTED
        item.save(update_fields=["status"])
        return Response({"id": str(item.id), "status": item.status})


class AdminUsersView(generics.ListAPIView):
    """GET /api/admin/users — foydalanuvchilar ro'yxati."""

    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]
    queryset = User.objects.all().order_by("-created_at")


class GrantPlanView(APIView):
    """PATCH /api/admin/users/{id}/plan — manual tarif berish.

    Subscription yaratadi → signal user.plan ni sinxronlaydi (ADR #5).
    """

    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = GrantPlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        Subscription.objects.create(
            user=user,
            plan=data["plan"],
            expires_at=timezone.now() + timedelta(days=data["days"]),
            payment_ref=data.get("payment_ref") or None,
        )
        user.refresh_from_db()
        return Response(
            AdminUserSerializer(user).data, status=status.HTTP_200_OK
        )
