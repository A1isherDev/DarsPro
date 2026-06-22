"""DarsPro — sinf (live) rejimi WebSocket consumer.

Host (token bilan) o'yinni boshqaradi; o'quvchilar (tokensiz) qo'shiladi va
javob yuboradi. Joriy savol indeksi Redis cache'da saqlanadi (barcha ulanishlar
uchun umumiy).
"""
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.cache import cache


def _group_name(join_code):
    return f"session_{join_code.replace('-', '_')}"


def _qindex_key(join_code):
    return f"session:{join_code}:q_index"


class SessionConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.join_code = self.scope["url_route"]["kwargs"]["join_code"]
        self.group = _group_name(self.join_code)
        self.participant_id = None

        session = await self._get_session(self.join_code)
        if session is None:
            await self.close(code=4404)  # sessiya topilmadi
            return

        self.session_id = session["id"]
        user = self.scope.get("user")
        self.is_host = (
            user is not None
            and getattr(user, "is_authenticated", False)
            and str(user.id) == str(session["host_user_id"])
        )

        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group"):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive_json(self, content, **kwargs):
        event = content.get("type")
        handler = {
            "player_join": self._on_player_join,
            "answer_submit": self._on_answer_submit,
            "host_next": self._on_host_next,
            "host_pause": self._on_host_pause,
            "host_end": self._on_host_end,
        }.get(event)

        if handler is None:
            await self.send_json({"type": "error", "detail": "Noma'lum event."})
            return
        await handler(content)

    # --- Client → Server handlerlari ---

    async def _on_player_join(self, content):
        name = (content.get("display_name") or "").strip()
        if not name:
            await self.send_json({"type": "error", "detail": "Ism kiritilmadi."})
            return
        participant = await self._create_participant(
            self.session_id, name, content.get("team_number")
        )
        self.participant_id = participant["id"]
        total = await self._participant_count(self.session_id)
        await self.channel_layer.group_send(
            self.group,
            {
                "type": "player_joined",
                "participant_id": participant["id"],
                "display_name": name,
                "total_players": total,
            },
        )

    async def _on_answer_submit(self, content):
        if not self.participant_id:
            await self.send_json({"type": "error", "detail": "Avval o'yinga qo'shiling."})
            return
        q_index = content.get("question_index")
        answer = content.get("answer")
        time_taken = content.get("time_taken", 0)

        correct, delta = await self._score_answer(
            self.participant_id, self.session_id, q_index, answer, time_taken
        )
        # Natijani faqat shu o'quvchiga
        await self.send_json(
            {"type": "answer_result", "correct": correct, "score_delta": delta}
        )
        # Leaderboard'ni hammaga
        rankings = await self._leaderboard(self.session_id)
        await self.channel_layer.group_send(
            self.group, {"type": "leaderboard_update", "rankings": rankings}
        )

    async def _on_host_next(self, content):
        if not self.is_host:
            return await self._deny()
        question = await self._next_question(self.session_id, self.join_code)
        if question is None:
            await self._end_game()
            return
        await self.channel_layer.group_send(
            self.group,
            {
                "type": "question_show",
                "index": question["index"],
                "question": question["question"],
                "time_limit": question["time_limit"],
            },
        )

    async def _on_host_pause(self, content):
        if not self.is_host:
            return await self._deny()
        await self.channel_layer.group_send(self.group, {"type": "game_paused"})

    async def _on_host_end(self, content):
        if not self.is_host:
            return await self._deny()
        await self._end_game()

    async def _end_game(self):
        rankings = await self._leaderboard(self.session_id)
        await self._mark_ended(self.session_id)
        await sync_to_async(cache.delete)(_qindex_key(self.join_code))
        await self.channel_layer.group_send(
            self.group, {"type": "game_ended", "final_results": rankings}
        )

    async def _deny(self):
        await self.send_json(
            {"type": "error", "detail": "Bu amal faqat host uchun."}
        )

    # --- Server → Client (group event) handlerlari ---

    async def player_joined(self, event):
        await self.send_json(event)

    async def question_show(self, event):
        await self.send_json(event)

    async def leaderboard_update(self, event):
        await self.send_json(event)

    async def game_paused(self, event):
        await self.send_json(event)

    async def game_ended(self, event):
        await self.send_json(event)

    async def game_started(self, event):
        await self.send_json(event)

    # --- DB / cache yordamchilari ---

    @database_sync_to_async
    def _get_session(self, join_code):
        from apps.sessions.models import GameSession

        try:
            s = GameSession.objects.select_related("content", "content__engine").get(
                join_code=join_code
            )
        except GameSession.DoesNotExist:
            return None
        return {
            "id": str(s.id),
            "host_user_id": str(s.host_user_id),
            "engine_slug": s.content.engine.slug,
            "data": s.content.data,
        }

    @database_sync_to_async
    def _create_participant(self, session_id, name, team_number):
        from apps.sessions.models import GameParticipant

        # Idempotent: reconnect yoki qayta player_join dublikat yaratmaydi —
        # bir sessiyada bir ism = bir ishtirokchi (ball saqlanadi).
        p, _ = GameParticipant.objects.get_or_create(
            session_id=session_id,
            display_name=name,
            defaults={"team_number": team_number},
        )
        return {"id": str(p.id)}

    @database_sync_to_async
    def _participant_count(self, session_id):
        from apps.sessions.models import GameParticipant

        return GameParticipant.objects.filter(session_id=session_id).count()

    @database_sync_to_async
    def _score_answer(self, participant_id, session_id, q_index, answer, time_taken):
        from apps.sessions.models import GameParticipant, GameSession

        session = GameSession.objects.select_related("content", "content__engine").get(
            id=session_id
        )
        engine = session.content.engine.slug
        data = session.content.data or {}

        correct = False
        if engine == "quiz":
            questions = data.get("questions", [])
            if isinstance(q_index, int) and 0 <= q_index < len(questions):
                correct = answer == questions[q_index].get("answer")

        # Ball: to'g'ri javob 500–1000 (tezroq = ko'proq)
        delta = 0
        if correct:
            t = max(0, min(int(time_taken or 0), 30))
            delta = int(1000 - (t / 30) * 500)

        p = GameParticipant.objects.get(id=participant_id)
        p.score += delta
        answers = p.answers if isinstance(p.answers, list) else []
        answers.append(
            {
                "question_index": q_index,
                "answer": answer,
                "correct": correct,
                "time_taken": time_taken,
                "score_delta": delta,
            }
        )
        p.answers = answers
        p.save(update_fields=["score", "answers"])
        return correct, delta

    @database_sync_to_async
    def _leaderboard(self, session_id):
        from apps.sessions.models import GameParticipant

        qs = GameParticipant.objects.filter(session_id=session_id).order_by(
            "-score", "joined_at"
        )[:50]
        return [
            {"name": p.display_name, "score": p.score, "team": p.team_number}
            for p in qs
        ]

    @database_sync_to_async
    def _mark_ended(self, session_id):
        from django.utils import timezone

        from apps.sessions.models import GameSession, SessionStatus

        GameSession.objects.filter(id=session_id).update(
            status=SessionStatus.ENDED, ended_at=timezone.now()
        )

    async def _next_question(self, session_id, join_code):
        """Joriy indeksni oshiradi va navbatdagi savolni qaytaradi (quiz)."""
        session = await self._get_session(join_code)
        data = session.get("data") or {}
        questions = data.get("questions", []) if session["engine_slug"] == "quiz" else []

        key = _qindex_key(join_code)
        current = await sync_to_async(cache.get)(key)
        next_index = 0 if current is None else current + 1
        if next_index >= len(questions):
            return None
        await sync_to_async(cache.set)(key, next_index, timeout=3600)

        q = questions[next_index]
        # To'g'ri javobni o'quvchilarga yubormaymiz
        safe_q = {k: v for k, v in q.items() if k != "answer"}
        return {
            "index": next_index,
            "question": safe_q,
            "time_limit": q.get("time_limit", 30),
        }
