"""DarsPro — content admin."""
from django.contrib import admin

from .models import ContentItem, GameEngine, Grade, Subject, Topic


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ["id", "number", "label"]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "icon", "is_active"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ["title", "subject", "grade", "order", "is_active"]
    list_filter = ["grade", "subject", "is_active"]
    search_fields = ["title"]


@admin.register(GameEngine)
class GameEngineAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ["title", "engine", "topic", "source", "status", "play_count"]
    list_filter = ["status", "source", "engine"]
    search_fields = ["title"]
    readonly_fields = ["id", "play_count", "created_at"]
