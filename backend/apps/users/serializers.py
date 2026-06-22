"""DarsPro — users serializerlari."""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Profil ko'rinishi (GET/PATCH /me)."""

    effective_plan = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "telegram_id",
            "auth_provider",
            "plan",
            "effective_plan",
            "plan_expires_at",
            "is_staff",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "email",
            "auth_provider",
            "plan",
            "plan_expires_at",
            "is_staff",
            "created_at",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """Email + parol bilan ro'yxatdan o'tish."""

    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "full_name", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Email orqali login (USERNAME_FIELD allaqachon email)."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["plan"] = user.effective_plan
        return token
