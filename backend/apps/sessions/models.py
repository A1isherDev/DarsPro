"""DarsPro — GameSession, GameParticipant, UserGame modellari."""
import uuid

from django.conf import settings
from django.db import models

from apps.content.models import ContentItem

from .join_code import unique_join_code


class SessionMode(models.TextChoices):
    SOLO = "solo", "Yakka"
    CLASS = "class", "Sinf"
    PAIR = "pair", "Juft"
    TEAM = "team", "Jamoa"


class SessionStatus(models.TextChoices):
    WAITING = "waiting", "Kutilmoqda"
    ACTIVE = "active", "Faol"
    ENDED = "ended", "Tugagan"


class GameSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.ForeignKey(
        ContentItem, on_delete=models.CASCADE, related_name="sessions"
    )
    host_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hosted_sessions",
    )
    join_code = models.CharField(max_length=8, unique=True, editable=False)
    mode = models.CharField(
        max_length=8, choices=SessionMode.choices, default=SessionMode.SOLO
    )
    status = models.CharField(
        max_length=8, choices=SessionStatus.choices, default=SessionStatus.WAITING
    )
    max_players = models.IntegerField(default=30)
    settings = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sessions_gamesession"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.join_code:
            self.join_code = unique_join_code(GameSession)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.join_code} ({self.status})"


class GameParticipant(models.Model):
    """O'quvchi — akkauntsiz, faqat ism + score (ADR #3)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        GameSession, on_delete=models.CASCADE, related_name="participants"
    )
    display_name = models.CharField(max_length=64)
    team_number = models.IntegerField(null=True, blank=True)  # faqat team mode
    score = models.IntegerField(default=0)
    answers = models.JSONField(default=list, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sessions_gameparticipant"
        ordering = ["-score", "joined_at"]

    def __str__(self):
        return f"{self.display_name} — {self.score}"


class UserGame(models.Model):
    """O'qituvchining shaxsiy o'yin tarixi (solo/host natijasi)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="games"
    )
    content = models.ForeignKey(
        ContentItem, on_delete=models.CASCADE, related_name="user_games"
    )
    score = models.IntegerField(default=0)
    duration_sec = models.IntegerField(default=0)
    played_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sessions_usergame"
        ordering = ["-played_at"]

    def __str__(self):
        return f"{self.user.email} — {self.content.title}"
