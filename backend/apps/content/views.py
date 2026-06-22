"""DarsPro — content view'lari."""
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, mixins, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

# Public katalog kamdan-kam o'zgaradi — qisqa muddatli Redis cache (5 daqiqa)
CATALOG_TTL = 60 * 5

from apps.users.limits import monthly_create_limit
from apps.users.permissions import IsOwner

from .models import (
    ContentItem,
    ContentSource,
    ContentStatus,
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
        if self.action == "list":
            return ContentItemListSerializer
        return ContentItemDetailSerializer

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
            if topic:
                qs = qs.filter(topic_id=topic)
            if engine:
                qs = qs.filter(engine__slug=engine)
            if source:
                qs = qs.filter(source=source)
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
