# DarsPro — Backend

Django 5 + DRF + Channels. To'liq spec: loyiha ildizidagi `CLAUDE.md`.

## Ishga tushirish (Docker — tavsiya etiladi)

```bash
cp .env.example .env          # kerak bo'lsa sirlarni o'zgartiring
docker compose up -d db redis # Postgres + Redis
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py loaddata grades subjects engines topics sample_items
docker compose run --rm web python manage.py createsuperuser
docker compose up web          # daphne ASGI :8000 da
```

## Lokal (Docker'siz)

Postgres + Redis lokal ishlab turishi kerak. `.env` da `DATABASE_URL`/`REDIS_URL`
ni `localhost` ga moslang, so'ng:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata grades subjects engines topics sample_items
python manage.py runserver        # yoki: daphne config.asgi:application
```

> cbor2 manba'dan qurilsa xato bersa: `pip install --only-binary=:all: cbor2` avval.

## Testlar

DB serveri yoki Redis shart emas — SQLite + InMemory channel layer ustida ishlaydi:

```bash
DATABASE_URL="sqlite:////tmp/darspro_test.sqlite3" python manage.py test tests
```

12 ta test: auth, kontent+kvota, sessiya, admin, solo natija (`tests/test_smoke.py`)
va sinf rejimi WebSocket oqimi — qo'shilish/savol/ball/leaderboard/tugatish,
host gating (`tests/test_websocket.py`, `WebsocketCommunicator` + `InMemoryChannelLayer`).

## Operatsion tizimlar

**Health (monitoring / load balancer / k8s):**
- `GET /api/health` — liveness (jarayon tirikmi)
- `GET /api/health/ready` — readiness (DB + Redis), nosoz bo'lsa 503

**Davriy fon vazifalari — Celery + Beat** (broker = Redis):
```bash
docker compose up worker beat   # worker (vazifa bajaruvchi) + beat (rejalashtiruvchi)
```
Beat jadval (`config/settings.py` → `CELERY_BEAT_SCHEDULE`):
- `reconcile_plans_task` — har soat (muddati o'tgan obunalar → user.plan free)
- `cleanup_sessions_task` — har 30 daqiqa (tashlab ketilgan sessiyalar)

Qo'lda / fallback (Celery'siz) bir xil logikani management command bajaradi:
```bash
python manage.py reconcile_plans   # --dry-run
python manage.py cleanup_sessions  # --dry-run --stale-hours --prune-days
```

**Caching:** public katalog (`/grades`, `/subjects`, `/engines`) Redis'da 5 daqiqa
keshlanadi (`cache_page`). **Logging:** `LOG_LEVEL` env (default INFO), console handler.

**Xavfsizlik:** WS Origin validatsiya (`ALLOWED_HOSTS`), throttling, payload/upload
limitlari, Pillow rasm verify. **Prod media:** `MEDIA_*` lokal storage faqat
`DEBUG`'da Django orqali xizmat qilinadi — prodda nginx yoki S3 (django-storages,
`DEFAULT_FILE_STORAGE` env) orqali bering.

## Struktura

| Yo'l | Mazmun |
|------|--------|
| `config/` | settings, urls, asgi (Channels routing), wsgi |
| `apps/users/` | User (UUID, email login), Subscription, JWT auth, /me, HasPlan/IsOwner |
| `apps/content/` | Grade/Subject/Topic/GameEngine/ContentItem, engine data validatorlar, kvota |
| `apps/sessions/` | GameSession (join_code DRS-XXXX), GameParticipant, UserGame |
| `apps/admin_panel/` | staff: review (approve/reject), manual tarif berish |
| `consumers/` | sinf rejimi WebSocket consumer + JWT middleware |

## Hozircha stub (keyingi faza)

`/api/auth/google|telegram|otp/*` → 501. Frontend, Payme/Click to'lov,
juft/jamoa rejim ham keyingi fazada.
