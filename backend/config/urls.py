"""DarsPro — asosiy URL konfiguratsiyasi."""
from django.contrib import admin
from django.urls import include, path

from .health import liveness, readiness

urlpatterns = [
    path("api/health", liveness, name="health"),
    path("api/health/ready", readiness, name="health-ready"),
    path("django-admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls_auth")),
    path("api/users/", include("apps.users.urls")),
    path("api/content/", include("apps.content.urls")),
    path("api/sessions/", include("apps.sessions.urls")),
    path("api/admin/", include("apps.admin_panel.urls")),
]
