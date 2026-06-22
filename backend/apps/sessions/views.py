"""DarsPro — sessiya view'lari."""
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import ContentItem

from .models import (
    GameParticipant,
    GameSession,
    SessionStatus,
)
from .serializers import (
    GameSessionSerializer,
    JoinSerializer,
    ParticipantSerializer,
    SoloResultSerializer,
)


class SessionCreateView(generics.CreateAPIView):
    """POST /api/sessions/ — host sessiya yaratadi."""

    serializer_class = GameSessionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(host_user=self.request.user)


class SoloResultView(generics.CreateAPIView):
    """POST /api/sessions/solo — yakka o'yin natijasini saqlaydi (UserGame)."""

    serializer_class = SoloResultSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        game = serializer.save(user=self.request.user)
        ContentItem.objects.filter(pk=game.content_id).update(
            play_count=F("play_count") + 1
        )


class SessionDetailView(generics.RetrieveAPIView):
    """GET /api/sessions/{join_code} — kod bilan kirish (auth shart emas)."""

    serializer_class = GameSessionSerializer
    permission_classes = [AllowAny]
    lookup_field = "join_code"
    lookup_url_kwarg = "join_code"
    queryset = GameSession.objects.select_related("content", "content__engine")


class SessionJoinView(APIView):
    """POST /api/sessions/{join_code}/join — o'quvchi ism kiritib kiradi."""

    permission_classes = [AllowAny]

    def post(self, request, join_code):
        session = get_object_or_404(GameSession, join_code=join_code)
        if session.status == SessionStatus.ENDED:
            raise ValidationError("Bu o'yin allaqachon tugagan.")
        if session.participants.count() >= session.max_players:
            raise ValidationError("O'yin to'lgan — joy qolmadi.")

        serializer = JoinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        participant = GameParticipant.objects.create(
            session=session,
            display_name=serializer.validated_data["display_name"],
            team_number=serializer.validated_data.get("team_number"),
        )
        return Response(
            ParticipantSerializer(participant).data, status=status.HTTP_201_CREATED
        )


class _HostActionMixin:
    """Sessiya egasini (host) tekshiruvchi yordamchi."""

    def get_session(self, request, pk):
        session = get_object_or_404(GameSession, pk=pk)
        if session.host_user_id != request.user.id:
            raise PermissionDenied("Bu sessiya sizga tegishli emas.")
        return session


class SessionStartView(_HostActionMixin, APIView):
    """PATCH /api/sessions/{id}/start — o'yinni boshlash."""

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        session = self.get_session(request, pk)
        if session.status != SessionStatus.WAITING:
            raise ValidationError("O'yinni faqat 'waiting' holatida boshlash mumkin.")
        session.status = SessionStatus.ACTIVE
        session.started_at = timezone.now()
        session.save(update_fields=["status", "started_at"])
        return Response(GameSessionSerializer(session, context={"request": request}).data)


class SessionEndView(_HostActionMixin, APIView):
    """PATCH /api/sessions/{id}/end — o'yinni tugatish."""

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        session = self.get_session(request, pk)
        if session.status == SessionStatus.ENDED:
            raise ValidationError("O'yin allaqachon tugagan.")
        session.status = SessionStatus.ENDED
        session.ended_at = timezone.now()
        session.save(update_fields=["status", "ended_at"])
        # play_count oshirish
        session.content.__class__.objects.filter(pk=session.content_id).update(
            play_count=F("play_count") + 1
        )
        return Response(GameSessionSerializer(session, context={"request": request}).data)


class SessionResultsView(_HostActionMixin, APIView):
    """GET /api/sessions/{id}/results — yakuniy natijalar."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        session = self.get_session(request, pk)
        participants = session.participants.all()  # score bo'yicha tartiblangan (Meta)
        rankings = [
            {
                "rank": i + 1,
                "display_name": p.display_name,
                "team_number": p.team_number,
                "score": p.score,
            }
            for i, p in enumerate(participants)
        ]
        return Response(
            {
                "session_id": str(session.id),
                "join_code": session.join_code,
                "status": session.status,
                "total_players": len(rankings),
                "rankings": rankings,
            }
        )


class SessionReportView(_HostActionMixin, APIView):
    """GET /api/sessions/{id}/report — savol bo'yicha aniqlik tahlili."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        session = self.get_session(request, pk)
        participants = list(session.participants.all())
        questions = (session.content.data or {}).get("questions", [])

        # Savol bo'yicha agregatsiya (GameParticipant.answers dan)
        agg = {}
        for p in participants:
            for ans in p.answers or []:
                idx = ans.get("question_index")
                if idx is None:
                    continue
                row = agg.setdefault(idx, {"correct": 0, "total": 0, "time": 0})
                row["total"] += 1
                row["time"] += ans.get("time_taken", 0) or 0
                if ans.get("correct"):
                    row["correct"] += 1

        question_stats = []
        for idx in sorted(agg):
            r = agg[idx]
            text = questions[idx]["text"] if idx < len(questions) else f"Savol {idx + 1}"
            question_stats.append(
                {
                    "index": idx,
                    "text": text,
                    "correct": r["correct"],
                    "total": r["total"],
                    "accuracy": round(r["correct"] / r["total"] * 100) if r["total"] else 0,
                    "avg_time": round(r["time"] / r["total"], 1) if r["total"] else 0,
                }
            )

        return Response(
            {
                "session_id": str(session.id),
                "content_title": session.content.title,
                "total_players": len(participants),
                "question_stats": question_stats,
            }
        )


class SessionResultsCsvView(_HostActionMixin, APIView):
    """GET /api/sessions/{id}/results.csv — natijalarni CSV qilib yuklab olish."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        import csv

        from django.http import HttpResponse

        session = self.get_session(request, pk)
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="darspro-{session.join_code}.csv"'
        )
        response.write("﻿")  # Excel UTF-8 BOM
        writer = csv.writer(response)
        writer.writerow(["O'rin", "Ism", "Jamoa", "Ball"])
        for i, p in enumerate(session.participants.all(), start=1):
            writer.writerow([i, p.display_name, p.team_number or "", p.score])
        return response
