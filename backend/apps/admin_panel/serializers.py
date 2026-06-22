"""DarsPro — admin panel serializerlari."""
from rest_framework import serializers

from apps.users.models import Plan, User


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "plan",
            "plan_expires_at",
            "is_active",
            "is_staff",
            "created_at",
        ]


class GrantPlanSerializer(serializers.Serializer):
    """Manual tarif berish: plan + amal qilish muddati (kun)."""

    plan = serializers.ChoiceField(
        choices=[c for c in Plan.choices if c[0] != Plan.FREE]
    )
    days = serializers.IntegerField(min_value=1, default=30)
    payment_ref = serializers.CharField(required=False, allow_blank=True)
