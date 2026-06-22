"""DarsPro — content serializerlari."""
from rest_framework import serializers

from .models import ContentItem, Grade, GameEngine, Subject, Topic
from .validators import validate_engine_data


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ["id", "number", "label"]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name", "slug", "icon", "is_active"]


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ["id", "subject", "grade", "title", "slug", "order", "is_active"]


class GameEngineSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameEngine
        fields = ["id", "name", "slug", "default_config"]


class ContentItemListSerializer(serializers.ModelSerializer):
    """Ro'yxat ko'rinishi — `data` siz (yengil)."""

    engine_slug = serializers.CharField(source="engine.slug", read_only=True)

    class Meta:
        model = ContentItem
        fields = [
            "id",
            "title",
            "topic",
            "engine",
            "engine_slug",
            "source",
            "status",
            "play_count",
            "created_at",
        ]


class ContentItemDetailSerializer(serializers.ModelSerializer):
    """To'liq ko'rinish + `data`. Builder POST/PATCH uchun ham."""

    engine_slug = serializers.CharField(source="engine.slug", read_only=True)

    class Meta:
        model = ContentItem
        fields = [
            "id",
            "title",
            "topic",
            "engine",
            "engine_slug",
            "created_by",
            "source",
            "data",
            "status",
            "play_count",
            "created_at",
        ]
        read_only_fields = [
            "created_by",
            "source",
            "status",
            "play_count",
            "created_at",
        ]

    def validate(self, attrs):
        # engine + data ni birga tekshiramiz (PATCH'da biri kelmasligi mumkin)
        engine = attrs.get("engine") or getattr(self.instance, "engine", None)
        data = attrs.get("data", getattr(self.instance, "data", None))
        if engine is not None and "data" in attrs:
            validate_engine_data(engine.slug, data)
        return attrs
