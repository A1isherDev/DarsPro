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
