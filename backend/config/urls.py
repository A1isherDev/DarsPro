"""DarsPro — asosiy URL konfiguratsiyasi."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from .health import liveness, readiness

urlpatterns = [
    path("api/health", liveness, name="health"),
    path("api/health/ready", readiness, name="health-ready"),
    path("", include("django_prometheus.urls")),  # /metrics
    path("api/schema", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("django-admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls_auth")),
    path("api/users/", include("apps.users.urls")),
    path("api/content/", include("apps.content.urls")),
    path("api/sessions/", include("apps.sessions.urls")),
    path("api/admin/", include("apps.admin_panel.urls")),
]

if settings.DEBUG:
    # Dev'da media fayllarni Django xizmat qiladi (prodda nginx/S3)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
