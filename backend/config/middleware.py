"""DarsPro — request-id middleware (loglarni so'rov bo'yicha bog'lash)."""
import json
import logging
import uuid

logger = logging.getLogger("apps.request")


class JsonFormatter(logging.Formatter):
    """Log yozuvlarini JSON sifatida chiqaradi (log agregatorlari uchun)."""

    def format(self, record):
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record),
        }
        if hasattr(record, "request_id"):
            payload["request_id"] = record.request_id
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


class RequestIDMiddleware:
    """Har so'rovga noyob ID beradi, X-Request-ID header qaytaradi va logga yozadi."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        request.request_id = rid
        response = self.get_response(request)
        response["X-Request-ID"] = rid
        logger.info(
            "%s %s %s",
            request.method,
            request.path,
            response.status_code,
            extra={"request_id": rid},
        )
        return response
