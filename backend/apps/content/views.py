"""DarsPro — content view'lari."""
import os
from uuid import uuid4

from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# Public katalog kamdan-kam o'zgaradi — qisqa muddatli Redis cache (5 daqiqa)
CATALOG_TTL = 60 * 5

from apps.users.limits import monthly_create_limit
from apps.users.permissions import IsOwner

from .models import (
    ContentItem,
    ContentSource,
    ContentStatus,
    Favorite,
    Grade,
    GameEngine,
    Subject,
    Topic,
)
from .serializers import (
    ContentItemDetailSerializer,
    ContentItemListSerializer,
    GameEngineSerializer,
    GradeSerializer,
    SubjectSerializer,
    TopicSerializer,
)


class MediaUploadView(APIView):
    """POST /api/content/upload — rasm yuklash, {url} qaytaradi (builder uchun)."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        f = request.FILES.get("file")
        if not f:
            raise ValidationError("Fayl yuborilmadi (maydon nomi: file).")
        if f.size > settings.MAX_UPLOAD_MB * 1024 * 1024:
            raise ValidationError(f"Fayl {settings.MAX_UPLOAD_MB} MB dan katta.")
        if not (f.content_type or "").startswith("image/"):
            raise ValidationError("Faqat rasm yuklash mumkin.")

        # Mijoz content_type/fayl nomiga ishonmaymiz — haqiqiy rasmligini
        # Pillow bilan tasdiqlaymiz va kengaytmani aniqlangan formatdan olamiz.
        from PIL import Image, UnidentifiedImageError

        try:
            image = Image.open(f)
            image.verify()
        except (UnidentifiedImageError, OSError, ValueError):
            raise ValidationError("Yaroqsiz yoki buzuq rasm fayli.")
        fmt = (image.format or "").lower()
        ext = {"jpeg": ".jpg", "png": ".png", "gif": ".gif", "webp": ".webp"}.get(fmt)
        if ext is None:
            raise ValidationError("Ruxsat etilgan format: jpg, png, gif, webp.")

        f.seek(0)  # verify() faylni o'qib chiqdi — qayta tiklaymiz
        name = default_storage.save(f"uploads/{uuid4().hex}{ext}", f)
        url = request.build_absolute_uri(settings.MEDIA_URL + name)
        return Response({"url": url}, status=status.HTTP_201_CREATED)


@method_decorator(cache_page(CATALOG_TTL), name="get")
class GradeListView(generics.ListAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [AllowAny]
    pagination_class = None


@method_decorator(cache_page(CATALOG_TTL), name="get")
class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.filter(is_active=True)
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class TopicListView(generics.ListAPIView):
    serializer_class = TopicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Topic.objects.filter(is_active=True)
        grade = self.request.query_params.get("grade")
        subject = self.request.query_params.get("subject")
        if grade:
            qs = qs.filter(grade_id=grade)
        if subject:
            qs = qs.filter(subject_id=subject)
        return qs


@method_decorator(cache_page(CATALOG_TTL), name="get")
class EngineListView(generics.ListAPIView):
    queryset = GameEngine.objects.all()
    serializer_class = GameEngineSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class ContentItemViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """/api/content/items — kutubxona + builder."""

    queryset = ContentItem.objects.select_related("engine", "topic")

    def get_serializer_class(self):
        if self.action in ("list", "favorites"):
            return ContentItemListSerializer
        return ContentItemDetailSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        user = self.request.user
        if user.is_authenticated:
            ctx["favorited_ids"] = set(
                Favorite.objects.filter(user=user).values_list("content_id", flat=True)
            )
        return ctx

    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]  # retrieve, create

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            mine = self.request.query_params.get("mine")
            if mine in ("1", "true", "True") and self.request.user.is_authenticated:
                # "Mening kontentim": barcha statusdagi o'z kontenti
                return qs.filter(created_by=self.request.user)
            # Kutubxona: faqat chop etilgan kontent
            qs = qs.filter(status=ContentStatus.PUBLISHED)
            topic = self.request.query_params.get("topic")
            engine = self.request.query_params.get("engine")
            source = self.request.query_params.get("source")
            search = self.request.query_params.get("search")
            if topic:
                qs = qs.filter(topic_id=topic)
            if engine:
                qs = qs.filter(engine__slug=engine)
            if source:
                qs = qs.filter(source=source)
            if search:
                qs = qs.filter(title__icontains=search)
        return qs

    def _check_quota(self, user):
        limit = monthly_create_limit(user.effective_plan)
        if limit is None:
            return  # cheksiz
        if limit == 0:
            raise PermissionDenied(
                "Tarifingiz o'yin yaratishga ruxsat bermaydi. Tarifni yangilang."
            )
        now = timezone.now()
        used = ContentItem.objects.filter(
            created_by=user,
            source=ContentSource.TEACHER,
            created_at__year=now.year,
            created_at__month=now.month,
        ).count()
        if used >= limit:
            raise PermissionDenied(
                f"Oylik limit ({limit} ta) tugadi. Keyingi oy yoki tarifni yangilang."
            )

    def perform_create(self, serializer):
        self._check_quota(self.request.user)
        serializer.save(
            created_by=self.request.user,
            source=ContentSource.TEACHER,
            status=ContentStatus.PENDING,
        )

    def perform_update(self, serializer):
        # Rad etilgan kontentni tahrirlaganda qayta ko'rib chiqishga yuboriladi.
        instance = serializer.instance
        if instance.status == ContentStatus.REJECTED:
            serializer.save(status=ContentStatus.PENDING)
        else:
            serializer.save()

    @action(detail=True, methods=["post", "delete"])
    def favorite(self, request, pk=None):
        """POST/DELETE /api/content/items/{id}/favorite — sevimlilarga qo'shish/olib tashlash."""
        item = self.get_object()
        if request.method == "POST":
            Favorite.objects.get_or_create(user=request.user, content=item)
            return Response(status=status.HTTP_201_CREATED)
        Favorite.objects.filter(user=request.user, content=item).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def favorites(self, request):
        """GET /api/content/items/favorites — sevimli published kontent."""
        qs = (
            ContentItem.objects.filter(
                favorited_by__user=request.user, status=ContentStatus.PUBLISHED
            )
            .select_related("engine", "topic")
            .order_by("-favorited_by__created_at")
        )
        page = self.paginate_queryset(qs)
        ser = ContentItemListSerializer(
            page, many=True, context=self.get_serializer_context()
        )
        return self.get_paginated_response(ser.data)

    @action(detail=True, methods=["post"])
    def clone(self, request, pk=None):
        """POST /api/content/items/{id}/clone — kontentni o'z nusxasiga klonlaydi."""
        source = self.get_object()
        self._check_quota(request.user)
        copy = ContentItem.objects.create(
            topic=source.topic,
            engine=source.engine,
            created_by=request.user,
            title=f"{source.title} (nusxa)",
            source=ContentSource.TEACHER,
            status=ContentStatus.PENDING,
            data=source.data,
        )
        return Response(
            ContentItemDetailSerializer(copy).data, status=status.HTTP_201_CREATED
        )
