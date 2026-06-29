"""DarsPro — auth va foydalanuvchi view'lari."""
from django.db.models import Avg, Count, Max, Sum
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .serializers import (
    EmailTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
)


def _tokens_for(user):
    refresh = RefreshToken.for_user(user)
    refresh["plan"] = user.effective_plan
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register — email + parol."""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"user": UserSerializer(user).data, "tokens": _tokens_for(user)},
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """POST /api/auth/login — token qaytaradi."""

    serializer_class = EmailTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"


class RefreshView(TokenRefreshView):
    """POST /api/auth/refresh — access token yangilash."""

    permission_classes = [AllowAny]


class LogoutView(APIView):
    """POST /api/auth/logout — refresh token'ni blacklist'ga qo'shadi."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"detail": "refresh token majburiy."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            return Response(
                {"detail": "Yaroqsiz token."}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_205_RESET_CONTENT)


class NotImplementedAuthView(APIView):
    """Google / Telegram / OTP — keyingi fazada (hozir stub)."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        return Response(
            {"detail": "Bu auth usuli hali ulanmagan."},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/users/me — profil + tarif."""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user


class MeStatsView(APIView):
    """GET /api/users/me/stats — o'yinlar statistikasi."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.sessions.models import UserGame

        agg = UserGame.objects.filter(user=request.user).aggregate(
            total_games=Count("id"),
            total_score=Sum("score"),
            avg_score=Avg("score"),
            best_score=Max("score"),
            total_seconds=Sum("duration_sec"),
        )
        return Response(
            {
                "total_games": agg["total_games"] or 0,
                "total_score": agg["total_score"] or 0,
                "avg_score": round(agg["avg_score"] or 0, 1),
                "best_score": agg["best_score"] or 0,
                "total_seconds": agg["total_seconds"] or 0,
            }
        )


class MeAchievementsView(APIView):
    """GET /api/users/me/achievements — yutuqlar (mavjud ma'lumotdan hisoblanadi)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.content.models import ContentItem
        from apps.sessions.models import GameParticipant, GameSession, UserGame

        user = request.user
        games = UserGame.objects.filter(user=user).count()
        created = ContentItem.objects.filter(created_by=user).count()
        hosted = GameSession.objects.filter(host_user=user).count()
        reached = GameParticipant.objects.filter(session__host_user=user).count()
        streak = self._streak(user)

        defs = [
            ("first_game", "Birinchi qadam", "🎯", games, 1),
            ("player", "O'yinboz", "🎮", games, 10),
            ("creator", "Ijodkor", "✍️", created, 1),
            ("host", "Murabbiy", "📡", hosted, 1),
            ("popular", "Mashhur", "🌟", reached, 50),
            ("streak", "Izchillik (3 kun)", "🔥", streak, 3),
        ]
        badges = [
            {
                "key": k,
                "label": label,
                "emoji": emoji,
                "current": cur,
                "target": tgt,
                "earned": cur >= tgt,
            }
            for (k, label, emoji, cur, tgt) in defs
        ]
        return Response({"streak": streak, "badges": badges})

    @staticmethod
    def _streak(user):
        from apps.sessions.models import UserGame

        dates = sorted(
            {
                d.date()
                for d in UserGame.objects.filter(user=user).values_list(
                    "played_at", flat=True
                )
            }
        )
        if not dates:
            return 0
        from datetime import timedelta

        best = run = 1
        for i in range(1, len(dates)):
            if dates[i] - dates[i - 1] == timedelta(days=1):
                run += 1
                best = max(best, run)
            else:
                run = 1
        return best


class MeTeachingStatsView(APIView):
    """GET /api/users/me/teaching-stats — o'qituvchining host statistikasi."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Avg, Count

        from apps.sessions.models import GameParticipant, GameSession, SessionStatus

        user = request.user
        sessions = GameSession.objects.filter(host_user=user)
        participants = GameParticipant.objects.filter(session__host_user=user)
        top = list(
            sessions.values("content__title")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )
        return Response(
            {
                "total_sessions": sessions.count(),
                "ended_sessions": sessions.filter(status=SessionStatus.ENDED).count(),
                "total_participants": participants.count(),
                "avg_participant_score": round(
                    participants.aggregate(a=Avg("score"))["a"] or 0, 1
                ),
                "top_content": [
                    {"title": t["content__title"], "sessions": t["count"]} for t in top
                ],
            }
        )


class MeHistoryView(generics.ListAPIView):
    """GET /api/users/me/history — o'yin tarixi."""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        from apps.sessions.serializers import UserGameSerializer

        return UserGameSerializer

    def get_queryset(self):
        from apps.sessions.models import UserGame

        return (
            UserGame.objects.filter(user=self.request.user)
            .select_related("content")
            .order_by("-played_at")
        )


class PlansView(APIView):
    """GET /api/users/plans — tariflar ro'yxati (public, pricing sahifasi uchun)."""

    permission_classes = [AllowAny]

    def get(self, request):
        from .plans import pricing_list

        return Response({"plans": pricing_list()})
