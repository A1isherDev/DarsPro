"""DarsPro — sinf rejimi WebSocket consumer integratsion testi.

Docker/Redis kerak emas: InMemoryChannelLayer + locmem cache + Django'ning
shared-cache sqlite test DB'si (TransactionTestCase) bilan ishlaydi.
"""
from asgiref.sync import async_to_sync
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase, override_settings
from rest_framework_simplejwt.tokens import RefreshToken

from apps.content.models import (
    ContentItem,
    ContentStatus,
    GameEngine,
    Grade,
    Subject,
    Topic,
)
from apps.sessions.models import GameSession, SessionMode
from apps.users.models import User
from consumers.middleware import JWTAuthMiddleware
from consumers.routing import websocket_urlpatterns

INMEM_LAYER = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
LOCMEM_CACHE = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
}


@override_settings(CHANNEL_LAYERS=INMEM_LAYER, CACHES=LOCMEM_CACHE)
class WebSocketClassFlowTest(TransactionTestCase):
    def setUp(self):
        self.host = User.objects.create_user("ws-host@test.uz", "StrongPass123")
        grade = Grade.objects.create(id=5, number=5, label="5-sinf")
        subject = Subject.objects.create(name="Test", slug="test")
        topic = Topic.objects.create(
            subject=subject, grade=grade, title="Mavzu", slug="mavzu"
        )
        engine = GameEngine.objects.create(name="Quiz", slug="quiz")
        self.content = ContentItem.objects.create(
            topic=topic,
            engine=engine,
            title="WS Quiz",
            status=ContentStatus.PUBLISHED,
            data={
                "questions": [
                    {
                        "text": "2+2?",
                        "options": ["4", "5"],
                        "answer": 0,
                        "time_limit": 30,
                    }
                ]
            },
        )
        self.session = GameSession.objects.create(
            content=self.content, host_user=self.host, mode=SessionMode.CLASS
        )
        self.code = self.session.join_code
        self.token = str(RefreshToken.for_user(self.host).access_token)

    def _app(self):
        return JWTAuthMiddleware(URLRouter(websocket_urlpatterns))

    def test_full_class_flow(self):
        async def scenario():
            app = self._app()
            player = WebsocketCommunicator(app, f"/ws/session/{self.code}/")
            host = WebsocketCommunicator(
                app, f"/ws/session/{self.code}/?token={self.token}"
            )
            pc, _ = await player.connect()
            hc, _ = await host.connect()
            assert pc and hc, "ulanish muvaffaqiyatsiz"

            # 1) O'quvchi qo'shiladi -> ikkala client player_joined oladi
            await player.send_json_to(
                {"type": "player_join", "display_name": "Ali"}
            )
            ev = await player.receive_json_from()
            assert ev["type"] == "player_joined"
            assert ev["display_name"] == "Ali"
            assert ev["total_players"] == 1
            await host.receive_json_from()  # host nusxasi

            # 2) Host savolni ko'rsatadi -> ikkala client question_show oladi
            await host.send_json_to({"type": "host_next"})
            q = await player.receive_json_from()
            assert q["type"] == "question_show"
            assert q["index"] == 0
            assert "answer" not in q["question"], "to'g'ri javob oshkor bo'lmasligi kerak"
            await host.receive_json_from()  # host nusxasi

            # 3) O'quvchi to'g'ri javob beradi -> answer_result + leaderboard
            await player.send_json_to(
                {
                    "type": "answer_submit",
                    "question_index": 0,
                    "answer": 0,
                    "time_taken": 1,
                }
            )
            res = await player.receive_json_from()
            assert res["type"] == "answer_result"
            assert res["correct"] is True
            assert res["score_delta"] > 0
            lb = await player.receive_json_from()
            assert lb["type"] == "leaderboard_update"
            assert lb["rankings"][0]["name"] == "Ali"
            assert lb["rankings"][0]["score"] > 0
            await host.receive_json_from()  # host leaderboard nusxasi

            # 4) Host o'yinni tugatadi -> game_ended
            await host.send_json_to({"type": "host_end"})
            end = await player.receive_json_from()
            assert end["type"] == "game_ended"
            assert end["final_results"][0]["name"] == "Ali"

            await player.disconnect()
            await host.disconnect()

        async_to_sync(scenario)()

    def test_team_number_flows_to_leaderboard(self):
        team_session = GameSession.objects.create(
            content=self.content, host_user=self.host, mode=SessionMode.TEAM
        )
        code = team_session.join_code

        async def scenario():
            app = self._app()
            player = WebsocketCommunicator(app, f"/ws/session/{code}/")
            host = WebsocketCommunicator(
                app, f"/ws/session/{code}/?token={self.token}"
            )
            assert (await player.connect())[0]
            assert (await host.connect())[0]

            await player.send_json_to(
                {"type": "player_join", "display_name": "Vali", "team_number": 2}
            )
            await player.receive_json_from()  # player_joined
            await host.receive_json_from()

            await host.send_json_to({"type": "host_next"})
            await player.receive_json_from()  # question_show
            await host.receive_json_from()

            await player.send_json_to(
                {
                    "type": "answer_submit",
                    "question_index": 0,
                    "answer": 0,
                    "time_taken": 1,
                }
            )
            await player.receive_json_from()  # answer_result
            lb = await player.receive_json_from()  # leaderboard_update
            assert lb["rankings"][0]["team"] == 2

            await player.disconnect()
            await host.disconnect()

        async_to_sync(scenario)()

    def test_player_join_is_idempotent(self):
        """Reconnect stsenariysi: bir ism bilan ikki marta join = bitta ishtirokchi."""

        async def scenario():
            app = self._app()
            player = WebsocketCommunicator(app, f"/ws/session/{self.code}/")
            assert (await player.connect())[0]

            await player.send_json_to(
                {"type": "player_join", "display_name": "Ali"}
            )
            ev1 = await player.receive_json_from()
            assert ev1["total_players"] == 1

            # qayta join (reconnect kabi) — yangi ishtirokchi yaratmaydi
            await player.send_json_to(
                {"type": "player_join", "display_name": "Ali"}
            )
            ev2 = await player.receive_json_from()
            assert ev2["total_players"] == 1

            await player.disconnect()

        async_to_sync(scenario)()

    def test_non_host_cannot_advance(self):
        async def scenario():
            app = self._app()
            # tokensiz (o'quvchi) ulanadi va host_next yuboradi -> rad etiladi
            player = WebsocketCommunicator(app, f"/ws/session/{self.code}/")
            pc, _ = await player.connect()
            assert pc
            await player.send_json_to({"type": "host_next"})
            ev = await player.receive_json_from()
            assert ev["type"] == "error"
            await player.disconnect()

        async_to_sync(scenario)()

    def test_unknown_session_closes(self):
        async def scenario():
            app = self._app()
            comm = WebsocketCommunicator(app, "/ws/session/DRS-ZZZZ/")
            connected, code = await comm.connect()
            assert not connected
            await comm.disconnect()

        async_to_sync(scenario)()
