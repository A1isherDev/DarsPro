"""DarsPro — to'lov serializerlari."""
from rest_framework import serializers

from apps.users.plans import PAID_PLANS

from .models import PaymentProvider, PaymentTransaction


class CheckoutSerializer(serializers.Serializer):
    plan = serializers.ChoiceField(choices=PAID_PLANS)
    provider = serializers.ChoiceField(choices=PaymentProvider.values)


class TransactionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ["id", "provider", "plan", "amount", "order_status", "created_at"]
        read_only_fields = fields
