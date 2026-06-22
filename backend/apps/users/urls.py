"""DarsPro — /api/users/ marshrutlari."""
from django.urls import path

from .views import MeHistoryView, MeStatsView, MeView

urlpatterns = [
    path("me", MeView.as_view(), name="me"),
    path("me/stats", MeStatsView.as_view(), name="me-stats"),
    path("me/history", MeHistoryView.as_view(), name="me-history"),
]
