"""DarsPro — /api/admin/ marshrutlari."""
from django.urls import path, re_path

from .views import (
    AdminUsersView,
    ApproveItemView,
    GrantPlanView,
    PendingItemsView,
    RejectItemView,
)

UUID = r"(?P<pk>[0-9a-f-]{36})"

urlpatterns = [
    path("items/pending", PendingItemsView.as_view(), name="admin-items-pending"),
    re_path(rf"^items/{UUID}/approve$", ApproveItemView.as_view(), name="admin-item-approve"),
    re_path(rf"^items/{UUID}/reject$", RejectItemView.as_view(), name="admin-item-reject"),
    path("users", AdminUsersView.as_view(), name="admin-users"),
    re_path(rf"^users/{UUID}/plan$", GrantPlanView.as_view(), name="admin-user-plan"),
]
