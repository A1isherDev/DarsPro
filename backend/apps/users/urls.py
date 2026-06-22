"""DarsPro — /api/users/ marshrutlari."""
from django.urls import path

from .views import (
    MeAchievementsView,
    MeHistoryView,
    MeStatsView,
    MeTeachingStatsView,
    MeView,
)

urlpatterns = [
    path("me", MeView.as_view(), name="me"),
    path("me/stats", MeStatsView.as_view(), name="me-stats"),
    path("me/teaching-stats", MeTeachingStatsView.as_view(), name="me-teaching-stats"),
    path("me/achievements", MeAchievementsView.as_view(), name="me-achievements"),
    path("me/history", MeHistoryView.as_view(), name="me-history"),
]
