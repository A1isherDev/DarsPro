# DarsPro 🎮

O'zbekiston maktab o'qituvchilari uchun **o'yin platformasi** — tayyor o'yinlar va
kontent kutubxonasi. O'qituvchilar savollarini kiritadi, o'yin enginelari original
o'yinlar yaratadi, sinf jonli (real-time) rejimda o'ynaydi.

[![CI](https://github.com/A1isherDev/DarsPro/actions/workflows/ci.yml/badge.svg)](https://github.com/A1isherDev/DarsPro/actions/workflows/ci.yml)

> **Til:** faqat o'zbek tili · **Platforma:** web (online-only) · **Auditoriya:** 1–11 sinf o'qituvchilari

---

## Imkoniyatlar

- 🔐 **Auth** — email + parol (JWT). Google/Telegram/OTP keyingi fazada.
- 📚 **Kontent kutubxonasi** — sinf / fan / mavzu bo'yicha filtr, paginatsiya.
- 🛠 **Builder** — 11 ta o'yin engine: Quiz, Matching, Flashcard, Memory, Spin Wheel,
  Sort Order, Fill Blank, Crossword, Word Search, True/False, Poll. Har biri Play + Builder rejimida.
- 🎓 **Rejimlar** — yakka (solo), sinf (live), juft, jamoa.
- 📡 **Real-time sinf** — WebSocket (Django Channels): host boshqaradi, o'quvchilar
  kod bilan akkauntsiz qo'shiladi, jonli reyting, medallar.
- 🧑‍💼 **Admin panel** — kontent review (approve/reject), manual tarif berish.
- 💳 **Tariflar** — free / start / pro / max; oylik yaratish kvotasi, sinf hajmi limiti.
- 📊 **Analitika** — sessiya hisobotlari, statistika.
- ⚙️ **Operatsion** — health endpointlar, Celery + Beat (davriy ishlar), Redis caching, logging.

## Tech stack

| Qatlam | Texnologiyalar |
|--------|----------------|
| **Backend** | Django 5, DRF, Django Channels, Celery, PostgreSQL, Redis, SimpleJWT |
| **Frontend** | Next.js 14 (App Router), TypeScript, TailwindCSS, Framer Motion, Zustand |
| **Test/CI** | Django test (43), Vitest (47) + Playwright e2e, GitHub Actions |
| **Infra** | Docker Compose (db, redis, web, worker, beat), S3-mos storage (media) |

## Struktura

```
darspro/
├── backend/    # Django: apps/{users,content,sessions,admin_panel} + consumers/ (WS)
├── frontend/   # Next.js: app/, components/engines/, components/ui/, lib/
├── .github/    # CI workflow
└── CLAUDE.md   # to'liq spetsifikatsiya (yagona haqiqat manbai)
```

## Tez boshlash

### Backend
```bash
cd backend
cp .env.example .env
docker compose up -d db redis
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py loaddata grades subjects engines topics sample_items
docker compose run --rm web python manage.py createsuperuser
docker compose up web worker beat        # API :8000, Celery worker + beat
```
**Eng tez yo'l (Docker'siz, Postgres/Redis shart emas)** — `DEV_LOCAL` SQLite + xotira-ichi
channel layer (faqat dev/demo, bitta jarayon):
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DEV_LOCAL=True DATABASE_URL="sqlite:///dev.sqlite3"
python manage.py migrate
python manage.py loaddata grades subjects engines topics sample_items
python manage.py seed_games            # 11 engine bo'yicha 100 tayyor o'yin (ixtiyoriy)
python manage.py createsuperuser
daphne -b 127.0.0.1 -p 8000 config.asgi:application
```

### Frontend
```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev                              # http://localhost:3000
```

## API hujjat

Server ishga tushgach: **Swagger UI** → `http://localhost:8000/api/docs`
(OpenAPI sxema: `/api/schema`). Health: `/api/health`, `/api/health/ready`.

## Testlar

```bash
# Backend (DB serveri shart emas — SQLite + InMemory channel layer)
cd backend && DATABASE_URL="sqlite:////tmp/t.sqlite3" python manage.py test tests

# Frontend
cd frontend && npm run test && npm run build
```

## Arxitektura qarorlari (ADR)

1. **Online-only** — kontent yuklab olinmaydi (tarqalishni oldini olish).
2. **Engine data = JSONB** — yangi engine uchun migration kerak emas.
3. **O'quvchilar akkauntsiz** — `GameParticipant` faqat ism + ball.
4. **join_code** — `DRS-XXXX` (proyektorda ko'rsatish uchun qisqa).
5. **user.plan denormalizatsiya** — obuna o'zgarganda signal sinxronlaydi.
6. **Faqat o'zbek tili** — i18n yo'q (MVP soddaligi).

To'liq spetsifikatsiya: [`CLAUDE.md`](CLAUDE.md).

## Production'ga chiqarish (launch checklist)

Kod sukut bo'yicha xavfsiz: maxsus sozlama berilmasa, tashqi servislar o'chiq turadi.
Jonli ishga tushirishdan oldin `.env` da quyidagilarni to'ldiring:

- **`SECRET_KEY`** — uzun tasodifiy qiymat (default qoldirilsa `DEBUG=False` da xato beradi).
- **`DEBUG=False`** + **`ALLOWED_HOSTS`** + **`CORS_ALLOWED_ORIGINS`** — haqiqiy domen(lar).
  `DEBUG=False` da HTTPS redirect, HSTS, secure cookie avtomatik yoqiladi (nginx orqasida).
- **`DATABASE_URL`** — boshqariladigan PostgreSQL (+ muntazam backup).
- **`REDIS_URL`** — channel layer + cache + Celery broker (prod'da `DEV_LOCAL` ishlatmang).
- **Media (`USE_S3=True`)** — `AWS_ACCESS_KEY_ID/SECRET/BUCKET/REGION` (S3-mos: `AWS_S3_ENDPOINT_URL`).
- **Email** — `EMAIL_BACKEND=...smtp...` + `EMAIL_HOST/PORT/USER/PASSWORD`.
- **Auth provayderlari** (Phase 2) — `GOOGLE_CLIENT_ID`, `TELEGRAM_BOT_TOKEN/USERNAME`,
  `SMS_PROVIDER=eskiz` + `ESKIZ_EMAIL/PASSWORD`.
- **To'lov** (Phase 3) — `PAYME_MERCHANT_ID/KEY`, `CLICK_MERCHANT_ID/SERVICE_ID/SECRET_KEY`.
- **Observability** (ixtiyoriy) — `SENTRY_DSN`, `LOG_FORMAT=json`; Prometheus `/metrics`.

Deploy: `docker compose up -d` (db, redis, web, worker, beat) + frontend `npm run build && npm start`.
Health probe'lar: `/api/health` (liveness), `/api/health/ready` (db + cache).
