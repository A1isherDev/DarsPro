"""DarsPro — staff (admin) view'lari."""
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import ContentItem, ContentStatus
from apps.content.serializers import ContentItemListSerializer
from apps.users.models import Subscription, User

from .serializers import AdminUserSerializer, GrantPlanSerializer


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
