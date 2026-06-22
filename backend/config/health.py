"""DarsPro — health/readiness endpointlari (monitoring, k8s, load balancer)."""
from django.core.cache import cache
from django.db import connection
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    throttle_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([])
def liveness(request):
    """Jarayon tirikmi — tashqi bog'liqliklarsiz."""
    return Response({"status": "ok"})


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([])
def readiness(request):
    """Xizmat so'rovlarga tayyormi — DB va Redis tekshiriladi."""
    checks = {}
    ok = True

    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["database"] = f"error: {exc.__class__.__name__}"
        ok = False

    try:
        cache.set("healthcheck", "1", 5)
        checks["cache"] = "ok" if cache.get("healthcheck") == "1" else "error"
        if checks["cache"] != "ok":
            ok = False
    except Exception as exc:  # noqa: BLE001
        checks["cache"] = f"error: {exc.__class__.__name__}"
        ok = False

    return Response(
        {"status": "ok" if ok else "degraded", "checks": checks},
        status=200 if ok else 503,
    )
