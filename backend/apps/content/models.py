"""DarsPro — kontent modellari: Grade, Subject, Topic, GameEngine, ContentItem."""
import uuid

from django.conf import settings
from django.db import models


class Grade(models.Model):
    """1–11 sinflar. id = sinf raqami."""

    id = models.IntegerField(primary_key=True)
    number = models.IntegerField()
    label = models.CharField(max_length=16)  # "1-sinf"

    class Meta:
        db_table = "content_grade"
        ordering = ["number"]

    def __str__(self):
        return self.label


class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=64, unique=True)
    icon = models.CharField(max_length=64, blank=True)  # emoji yoki icon nomi
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "content_subject"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Topic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="topics"
    )
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=128)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "content_topic"
        ordering = ["grade_id", "order"]
        unique_together = [("subject", "grade", "slug")]

    def __str__(self):
        return f"{self.title} ({self.grade.label})"


class GameEngine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)  # "Quiz"
    slug = models.SlugField(max_length=32, unique=True)  # "quiz"
    default_config = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "content_gameengine"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ContentSource(models.TextChoices):
    STAFF = "staff", "Staff"
    TEACHER = "teacher", "O'qituvchi"


class ContentStatus(models.TextChoices):
    DRAFT = "draft", "Qoralama"
    PENDING = "pending", "Ko'rib chiqilmoqda"
    PUBLISHED = "published", "Chop etilgan"
    REJECTED = "rejected", "Rad etilgan"


class ContentItem(models.Model):
    """Engine'ga xos kontent. data — JSONB (ADR #2)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="items")
    engine = models.ForeignKey(
        GameEngine, on_delete=models.PROTECT, related_name="items"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="content_items",
    )  # NULL = staff yaratgan
    title = models.CharField(max_length=255)
    source = models.CharField(
        max_length=8, choices=ContentSource.choices, default=ContentSource.STAFF
    )
    data = models.JSONField(default=dict)  # engine-specific
    status = models.CharField(
        max_length=10, choices=ContentStatus.choices, default=ContentStatus.DRAFT
    )
    play_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content_contentitem"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["topic", "engine"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.title
