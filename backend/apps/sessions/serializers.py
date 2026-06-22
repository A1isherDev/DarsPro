"""DarsPro — sessions serializerlari."""
from rest_framework import serializers

from apps.users.limits import max_players as plan_max_players

from .models import GameParticipant, GameSession, SessionMode, UserGame


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameParticipant
        fields = ["id", "display_name", "team_number", "score", "joined_at"]
        read_only_fields = ["id", "score", "joined_at"]


class GameSessionSerializer(serializers.ModelSerializer):
    """Sessiya yaratish va ko'rish."""

    participant_count = serializers.IntegerField(
        source="participants.count", read_only=True
    )
    content_title = serializers.CharField(source="content.title", read_only=True)
    engine_slug = serializers.CharField(source="content.engine.slug", read_only=True)

    class Meta:
        model = GameSession
        fields = [
            "id",
            "content",
            "content_title",
            "engine_slug",
            "join_code",
            "mode",
            "status",
            "max_players",
            "settings",
            "participant_count",
            "started_at",
            "ended_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "join_code",
            "status",
            "started_at",
            "ended_at",
            "created_at",
        ]

    def validate(self, attrs):
        user = self.context["request"].user
        plan = user.effective_plan

        # max_players tarif limitidan oshmasin
        cap = plan_max_players(plan)
        requested = attrs.get("max_players", cap)
        if requested > cap:
            raise serializers.ValidationError(
                {
                    "max_players": (
                        f"Tarifingiz bo'yicha maksimal {cap} o'quvchi. "
                        f"Ko'proq uchun tarifni yangilang."
                    )
                }
            )

        # Juft/jamoa rejimi faqat start+ tarifda (CLAUDE.md tariflar jadvali)
        mode = attrs.get("mode", SessionMode.SOLO)
        if mode in (SessionMode.PAIR, SessionMode.TEAM) and plan == "free":
            raise serializers.ValidationError(
                {
                    "mode": (
                        "Juft va jamoa rejimi Start tarifidan boshlab mavjud. "
                        "Tarifni yangilang."
                    )
                }
            )
        return attrs


class JoinSerializer(serializers.Serializer):
    """O'quvchi sessiyaga kiradi (auth yo'q)."""

    display_name = serializers.CharField(max_length=64)
    team_number = serializers.IntegerField(required=False, allow_null=True)


class SoloResultSerializer(serializers.ModelSerializer):
    """Yakka o'yin natijasini saqlash (POST). user view'da o'rnatiladi."""

    class Meta:
        model = UserGame
        fields = ["id", "content", "score", "duration_sec", "played_at"]
        read_only_fields = ["id", "played_at"]


class UserGameSerializer(serializers.ModelSerializer):
    content_title = serializers.CharField(source="content.title", read_only=True)
    engine_slug = serializers.CharField(source="content.engine.slug", read_only=True)

    class Meta:
        model = UserGame
        fields = [
            "id",
            "content",
            "content_title",
            "engine_slug",
            "score",
            "duration_sec",
            "played_at",
        ]
