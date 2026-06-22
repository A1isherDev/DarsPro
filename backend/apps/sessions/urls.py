"""DarsPro — /api/sessions/ marshrutlari.

join_code DRS-XXXX formatida (8 belgi), id esa UUID. URL pattern'lar shu asosda
ajratiladi.
"""
from django.urls import path, re_path

from .views import (
    SessionCreateView,
    SessionDetailView,
    SessionEndView,
    SessionJoinView,
    SessionResultsView,
    SessionStartView,
    SoloResultView,
)

JOIN = r"(?P<join_code>DRS-[A-Z0-9]{4})"
UUID = r"(?P<pk>[0-9a-f-]{36})"

urlpatterns = [
    path("", SessionCreateView.as_view(), name="session-create"),
    path("solo", SoloResultView.as_view(), name="session-solo"),
    re_path(rf"^{JOIN}/join$", SessionJoinView.as_view(), name="session-join"),
    re_path(rf"^{JOIN}$", SessionDetailView.as_view(), name="session-detail"),
    re_path(rf"^{UUID}/start$", SessionStartView.as_view(), name="session-start"),
    re_path(rf"^{UUID}/end$", SessionEndView.as_view(), name="session-end"),
    re_path(rf"^{UUID}/results$", SessionResultsView.as_view(), name="session-results"),
]
