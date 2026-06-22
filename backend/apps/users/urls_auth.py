"""DarsPro — /api/auth/ marshrutlari."""
from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    NotImplementedAuthView,
    RefreshView,
    RegisterView,
)

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("login", LoginView.as_view(), name="login"),
    path("refresh", RefreshView.as_view(), name="refresh"),
    path("logout", LogoutView.as_view(), name="logout"),
    # Keyingi fazada ulanadi (hozir 501)
    path("google", NotImplementedAuthView.as_view(), name="google"),
    path("telegram", NotImplementedAuthView.as_view(), name="telegram"),
    path("otp/send", NotImplementedAuthView.as_view(), name="otp-send"),
    path("otp/verify", NotImplementedAuthView.as_view(), name="otp-verify"),
]
