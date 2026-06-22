"""DarsPro — sessions admin."""
from django.contrib import admin

from .models import GameParticipant, GameSession, UserGame


class ParticipantInline(admin.TabularInline):
    model = GameParticipant
    extra = 0
    readonly_fields = ["display_name", "team_number", "score", "joined_at"]


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ["join_code", "content", "host_user", "mode", "status", "created_at"]
    list_filter = ["mode", "status"]
    search_fields = ["join_code", "host_user__email"]
    readonly_fields = ["id", "join_code", "created_at", "started_at", "ended_at"]
    inlines = [ParticipantInline]


@admin.register(UserGame)
class UserGameAdmin(admin.ModelAdmin):
    list_display = ["user", "content", "score", "duration_sec", "played_at"]
    search_fields = ["user__email"]
