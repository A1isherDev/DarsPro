# DarsPro — CLAUDE.md

Bu fayl DarsPro loyihasining yagona haqiqat manbai.
Har bir Claude Code sessiyasi bu fayldan boshlanishi shart.

---

## Loyiha haqida

**DarsPro** — O'zbekiston maktab o'qituvchilari uchun obuna platformasi.
O'qituvchilar tayyor o'yinlar va kontent kutubxonasidan foydalanadi,
shuningdek o'z savollarini kiritib, o'yin enginelari orqali original
o'yinlar yaratadi.

- **Til:** Faqat O'zbek tili
- **Platforma:** Web (online-only, fayl yuklab olish yo'q)
- **Maqsad auditoriya:** 1–11 sinf maktab o'qituvchilari, Toshkent va butun O'zbekiston

---

## Tech Stack

### Frontend
- Next.js 14 (App Router)
- TypeScript
- TailwindCSS
- Shadcn/UI
- Zustand (state management)
- Socket.IO client (real-time)

### Backend
- Django 5 + Django REST Framework
- Django Channels (WebSocket)
- PostgreSQL
- Redis (channel layer + caching)
- SimpleJWT (access + refresh tokens)

### Infratuzilma
- S3-compatible storage (rasmlar, audio)
- Payme + Click (kelajakda, hozir manual)

---

## Loyiha strukturasi

```
darspro/
├── frontend/                  # Next.js app
│   ├── app/
│   │   ├── (auth)/            # login, register
│   │   ├── (dashboard)/       # o'qituvchi dashboard
│   │   │   ├── library/       # kontent kutubxonasi
│   │   │   ├── builder/       # o'yin yaratish
│   │   │   └── sessions/      # o'yin sessiyalari
│   │   ├── play/
│   │   │   └── [join_code]/   # o'quvchi kirish sahifasi
│   │   └── admin/             # staff panel
│   ├── components/
│   │   ├── engines/           # har bir engine komponenti
│   │   │   ├── Quiz/
│   │   │   ├── Matching/
│   │   │   ├── Flashcard/
│   │   │   └── ...
│   │   ├── ui/                # shadcn komponenlari
│   │   └── shared/
│   └── lib/
│       ├── api.ts             # API client
│       └── socket.ts          # WebSocket client
│
└── backend/                   # Django project
    ├── config/                # settings, urls, asgi
    ├── apps/
    │   ├── users/             # User model, auth
    │   ├── content/           # Grade, Subject, Topic, ContentItem, GameEngine
    │   ├── sessions/          # GameSession, GameParticipant, UserGame
    │   └── admin_panel/       # staff endpoints
    └── consumers/             # WebSocket consumers
```

---

## Database — asosiy jadvallar

### users_user
```
id              UUID PK
full_name       VARCHAR
email           VARCHAR UNIQUE
phone           VARCHAR NULLABLE
telegram_id     VARCHAR NULLABLE
auth_provider   ENUM(email, google, telegram, phone)
plan            ENUM(free, start, pro, max) DEFAULT free
plan_expires_at TIMESTAMP NULLABLE
is_active       BOOLEAN DEFAULT true
is_staff        BOOLEAN DEFAULT false
created_at      TIMESTAMP
```

### users_subscription
```
id              UUID PK
user_id         FK → users_user
plan            ENUM(start, pro, max)
status          ENUM(active, expired, cancelled)
started_at      TIMESTAMP
expires_at      TIMESTAMP
payment_ref     VARCHAR NULLABLE
```

### content_grade
```
id              INTEGER PK (1–11)
number          INTEGER
label           VARCHAR  -- "1-sinf", "2-sinf"...
```

### content_subject
```
id              UUID PK
name            VARCHAR  -- "Matematika", "Biologiya"
slug            VARCHAR UNIQUE
icon            VARCHAR  -- emoji yoki icon nomi
is_active       BOOLEAN DEFAULT true
```

### content_topic
```
id              UUID PK
subject_id      FK → content_subject
grade_id        FK → content_grade
title           VARCHAR
slug            VARCHAR
order           INTEGER
is_active       BOOLEAN DEFAULT true
```

### content_gameengine
```
id              UUID PK
name            VARCHAR  -- "Quiz", "Matching"
slug            VARCHAR UNIQUE  -- "quiz", "matching"
default_config  JSONB
```

### content_contentitem
```
id              UUID PK
topic_id        FK → content_topic
engine_id       FK → content_gameengine
created_by      FK → users_user NULLABLE  -- NULL = staff yaratgan
title           VARCHAR
source          ENUM(staff, teacher) DEFAULT staff
data            JSONB  -- engine-specific kontent
status          ENUM(draft, pending, published, rejected) DEFAULT draft
play_count      INTEGER DEFAULT 0
created_at      TIMESTAMP
```

### sessions_gamesession
```
id              UUID PK
content_id      FK → content_contentitem
host_user_id    FK → users_user
join_code       VARCHAR(8) UNIQUE  -- masalan: "DRS-47F2"
mode            ENUM(solo, class, pair, team)
status          ENUM(waiting, active, ended)
max_players     INTEGER DEFAULT 30
settings        JSONB  -- timer, show_leaderboard va h.k.
started_at      TIMESTAMP NULLABLE
ended_at        TIMESTAMP NULLABLE
```

### sessions_gameparticipant
```
id              UUID PK
session_id      FK → sessions_gamesession
display_name    VARCHAR
team_number     INTEGER NULLABLE  -- faqat team mode uchun
score           INTEGER DEFAULT 0
answers         JSONB
joined_at       TIMESTAMP
```

### sessions_usergame
```
id              UUID PK
user_id         FK → users_user
content_id      FK → content_contentitem
score           INTEGER
duration_sec    INTEGER
played_at       TIMESTAMP
```

---

## API Endpoints

**Base URL:** `/api/`
**Auth:** Bearer token (SimpleJWT)

### Auth `/api/auth/`
```
POST /register          — email + parol
POST /login             — token qaytaradi
POST /google            — OAuth callback
POST /telegram          — Telegram widget
POST /otp/send          — SMS yuborish
POST /otp/verify        — Kodni tasdiqlash
POST /refresh           — Token yangilash
POST /logout            [auth]
```

### Foydalanuvchi `/api/users/`
```
GET  /plans                     — tariflar ro'yxati (public, pricing sahifasi)
GET  /me                [auth]  — profil + tarif
PATCH /me               [auth]  — profil yangilash
GET  /me/stats          [auth]  — statistika
GET  /me/history        [auth]  — o'yin tarixi
```

### Kontent `/api/content/`
```
GET  /grades                    — 1–11 ro'yxat
GET  /subjects                  — fanlar
GET  /topics                    — ?grade=&subject=
GET  /engines                   — engine turlari
POST /upload            [auth]  — rasm yuklash → {url} (builder uchun)
GET  /items                     — ?topic=&engine=&source= (faqat published)
GET  /items?mine=true   [auth]  — o'z kontenti (barcha status: draft/pending/...)
GET  /items/{id}        [auth]  — to'liq + data field
POST /items             [auth]  — builder (o'qituvchi yaratadi)
PATCH /items/{id}       [auth]  — faqat o'z kontenti (rejected→pending qayta yuboriladi)
DELETE /items/{id}      [auth]  — faqat o'z kontenti
```

### Admin `/api/admin/`
```
GET  /stats             [admin] — dashboard ko'rsatkichlari (users, MRR, content, sessions)
GET  /items/pending     [admin] — review navbati
PATCH /items/{id}/approve [admin]
PATCH /items/{id}/reject  [admin]
GET  /users             [admin]
PATCH /users/{id}/plan  [admin] — manual tarif berish
```

### Sessiya `/api/sessions/`
```
POST /                  [auth]  — sessiya yaratish
POST /solo              [auth]  — yakka o'yin natijasini saqlash (UserGame)
GET  /{join_code}               — kod bilan kirish (auth yo'q)
POST /{join_code}/join          — o'quvchi kiradi (ism kiritadi)
PATCH /{id}/start       [auth]  — o'yinni boshlash
PATCH /{id}/end         [auth]  — o'yinni tugatish
GET  /{id}/results      [auth]  — yakuniy natijalar
GET  /{id}/report       [auth]  — savol bo'yicha aniqlik tahlili (host)
GET  /{id}/results.csv  [auth]  — natijalarni CSV yuklab olish (host)
```

### WebSocket
```
ws/session/{join_code}/

Client → Server:
  player_join         { display_name, team_number? }
  answer_submit       { question_index, answer, time_taken }
  host_next           {}
  host_pause          {}
  host_end            {}

Server → Client:
  player_joined       { participant_id, display_name, total_players }
  game_started        { content_data, settings }
  question_show       { index, question, time_limit }
  answer_result       { correct, score_delta }
  leaderboard_update  { rankings: [{name, score, team?}] }
  game_ended          { final_results }
```

---

## O'yin Enginelari

Har bir engine ikkita rejimda ishlaydi:
- **Play rejimi:** `content_contentitem.data` ni o'qib o'ynaydi
- **Builder rejimi:** O'qituvchi ma'lumot kiritadi, `data` hosil bo'ladi

### data JSONB sxemalari

**quiz:**
```json
{
  "questions": [
    {
      "text": "Savolni yozing",
      "image": null,
      "options": ["A", "B", "C", "D"],
      "answer": 0,
      "time_limit": 30
    }
  ]
}
```

**matching:**
```json
{
  "pairs": [
    { "term": "Fotosintez", "definition": "O'simlik quyosh nuri bilan oziq..." }
  ]
}
```

**flashcard:**
```json
{
  "cards": [
    { "front": "Atom", "back": "Moddaning eng kichik bo'lagi" }
  ]
}
```

**spin_wheel:**
```json
{
  "items": ["Ali", "Vali", "Maftuna", "Jasur"],
  "type": "students"
}
```

**memory:**
```json
{
  "pairs": [
    { "a": "🐶", "b": "It" }
  ]
}
```

**crossword:**
```json
{
  "words": [
    { "word": "ATOM", "clue": "Moddaning eng kichik bo'lagi" }
  ]
}
```

**sort_order:**
```json
{
  "items": [
    { "text": "Urug' ekish", "order": 1 },
    { "text": "Suv berish", "order": 2 },
    { "text": "Unib chiqish", "order": 3 }
  ],
  "title": "O'simlik o'sish bosqichlari"
}
```

**fill_blank:**
```json
{
  "text": "O'zbekiston poytaxti ___ shahridir.",
  "blanks": ["Toshkent"],
  "hints": []
}
```

**word_search:**
```json
{
  "words": ["ATOM", "MOLEKULA", "ION"],
  "grid_size": 10
}
```

---

## Tariflar va cheklovlar

| Imkoniyat          | free | start | pro | max  |
|--------------------|------|-------|-----|------|
| Narx (so'm/oy)     | 0    | 19000 | 39000 | 79000 |
| Kutubxona kirish   | cheklangan | to'liq | to'liq | to'liq |
| Oylik o'yin yaratish | 0  | 15    | ∞   | ∞    |
| Sinf (live) o'quvchi | 10 | 30    | 100 | 500  |
| Jamoa/juft rejim   | ❌  | ✅    | ✅  | ✅   |
| Ko'p o'qituvchi    | ❌  | ❌    | ❌  | 5 ta |
| Reklama            | bor | yo'q  | yo'q | yo'q |

**Tarif tekshirish middleware:** har bir himoyalangan endpointda
`user.plan` va `user.plan_expires_at` tekshiriladi.

---

## Muhim qarorlar (ADR)

### 1. Online-only, fayl yo'q
O'qituvchilar kontent yuklab ololmaydi. Platforma ichida ko'radi va o'ynaydi.
**Sabab:** Kontent tarqalishini oldini olish, obunani ushlab turish.

### 2. content_contentitem.data — JSONB
Har bir engine uchun alohida jadval emas, bitta JSONB field.
**Sabab:** Yangi engine qo'shganda migration kerak emas. Engine o'z sxemasini biladi.

### 3. O'quvchilar akkauntisiz kiradi
`GameParticipant` — faqat ism va score. Auth yo'q.
**Sabab:** Sinf sharoitida har bir o'quvchiga akkaunt ochib bo'lmaydi.

### 4. join_code — qisqa va yodda qoladigan
Format: `DRS-XXXX` (8 belgi). O'qituvchi proyektorda ko'rsatadi,
o'quvchilar telefondan kiritadi.

### 5. user.plan denormalizatsiya
Subscription jadvali + user.plan ikkalasi sinxron.
**Sabab:** Har so'rovda subscription JOIN qilmaslik uchun.
Subscription o'zgarganda signal orqali user.plan yangilanadi.

### 6. Til — faqat O'zbek
i18n yo'q. Barcha UI, xatolar, ma'lumotlar o'zbekcha.
**Sabab:** MVP uchun soddalik. Rus tili kelajakda qo'shilishi mumkin.

---

## Kodni yozish qoidalari

### Django
- Model nomlar: `ContentItem`, `GameSession` (PascalCase)
- Serializer: har bir model uchun alohida `serializers.py`
- View: `ModelViewSet` ishlatish, custom action uchun `@action`
- Permission: `IsAuthenticated`, `IsAdminUser`, custom `HasPlan(plan='pro')`
- Signal: subscription o'zgarganda `user.plan` yangilash

### Next.js
- Sahifa: `app/` router, Server Components default
- Client components: faqat interaktiv bo'lsa `'use client'`
- API calls: `lib/api.ts` orqali (axios instance, token interceptor)
- Engine komponenti: `components/engines/{EngineName}/` papkada:
  - `Play.tsx` — o'ynash rejimi
  - `Builder.tsx` — yaratish rejimi
  - `index.ts` — export

### TypeScript
- `any` ishlatmaslik
- API response uchun interface: `types/api.ts` da saqlash
- Engine data uchun: `types/engines.ts` da har bir engine interface

---

## MVP scope (1-faza)

Faqat shular birinchi versiyada:

**Backend:** ✅ (1-faza qurildi → `backend/`)
- [x] User auth (email; Google/Telegram/OTP stub → 501)
- [x] Content models + fixtures (Grade 1-11, 8 fan, 9 engine)
- [x] 3 ta engine data validatsiyasi: Quiz, Matching, Flashcard
- [x] ContentItem CRUD + oylik yaratish kvotasi
- [x] GameSession (solo + class rejim) + max_players tarif limiti
- [x] WebSocket consumer (class rejim, JWT host auth)
- [x] Admin plan berish (Subscription → signal → user.plan)

**Frontend:** ✅ (1-faza qurildi → `frontend/`)
- [x] Auth sahifalari
- [x] Kutubxona (filter: sinf + fan + mavzu)
- [x] Quiz engine (Play + Builder)
- [x] Matching engine (Play + Builder)
- [x] Flashcard engine (Play + Builder)
- [x] Sinf rejimi (host xonasi + o'quvchi sahifalari, native WebSocket)
- [x] Dashboard (statistika)

> ⚠️ WebSocket: backend Django Channels (xom WS) ishlatgani uchun frontend
> `lib/socket.ts` da native WebSocket ishlatadi — Socket.IO emas.

**Qo'shimcha qurilgan (MVP'dan tashqari):**
- ✅ Barcha 9 engine (memory, spin_wheel, sort_order, fill_blank, crossword,
  word_search) — backend validator + frontend Play/Builder + namuna kontent
- ✅ Admin panel UI (`/admin`), profil tahrirlash, solo natija saqlash
- ✅ "Mening kontentim" (tahrir/o'chir, rejected→pending qayta yuborish)
- ✅ Juft/jamoa rejimi (Start+ tarif gate, jamoa raqami, jamoalar reytingi)
- ✅ Mustahkamlik: DRF throttling + prod hardening, WebSocket reconnect +
  idempotent join, paginatsiya (LoadMore), mobil drawer
- ✅ Testlar: backend 20 (smoke + WebSocket + ops), frontend 39 (Vitest)
- ✅ CI (.github/workflows), frontend Docker (standalone)
- ✅ Operatsion: health endpointlar (`/api/health`, `/ready`), **Celery + Beat**
  (reconcile_plans har soat, cleanup_sessions har 30 daq; management command fallback),
  katalog caching, LOGGING. Docker: worker + beat servislari
- ✅ API hujjat: Swagger UI `/api/docs` (drf-spectacular), root README
- ✅ Analitika: sessiya report (savol aniqligi), CSV eksport, teaching-stats; dashboard kartasi
- ✅ Media upload: rasmli quiz savollari (`/api/content/upload`, lokal/S3 storage)
- ✅ O'qituvchi qulayliklari: kutubxona qidiruvi (`?search=`), kontent klon
  (`items/{id}/clone`), sevimlilar (`items/{id}/favorite`, `items/favorites`),
  PDF hisobot (print)
- ✅ 11 engine (true_false, poll qo'shildi); gamifikatsiya: yutuqlar
  (`/users/me/achievements`) + dashboard; ovoz effektlari (Web Audio)
- ✅ Observability: request-id middleware, JSON logging (`LOG_FORMAT=json`),
  Sentry (`SENTRY_DSN` bo'lsa), Prometheus `/metrics`; E2E (Playwright + axe a11y)
- ✅ Hardening: WS Origin validatsiya (CSWSH), WS max_players + display_name cap +
  rate-limit, payload limitlari (data ≤100KB, savol/variant caps), kuchli parol
  validatorlari, upload Pillow verify (soxta rasm rad). Test: `test_security.py`
- ✅ UI qayta-ishlash: o'yinbop/rang-barang dizayn, Framer Motion, Baloo 2 +
  Nunito shriftlar, kengaytirilgan token palitra (success/warning/info/answer),
  primitivlar (Skeleton/EmptyState/Toast/Dialog/Progress), Kahoot-uslub Quiz,
  3D flip Flashcard, celebrate/shake, medalli reyting
- ✅ Tariflar: public `GET /api/users/plans` (`apps/users/plans.py` — yagona
  narx manbai) + `/pricing` sahifasi (4 tarif kartasi, faqat ma'lumot — to'lov
  manual). Landing + dashboard nav'da havola
- ✅ Admin dashboard: `GET /api/admin/stats` (users/plan, faol obuna + taxminiy
  MRR, content status/engine, sessiyalar — hammasi DB aggregatsiyasi) +
  `/admin/dashboard` UI (KPI kartalar + breakdown barlar). Review `/admin` da qoladi
- ✅ Test kontenti: `python manage.py seed_games` — 11 engine bo'yicha 100 ta
  tayyor o'yin (idempotent, uuid5 + update_or_create, validatordan o'tadi).
  Test: `test_dashboard.py`

**Keyinga qoldiriladiganlar:**
- Payme/Click to'lov
- Max tarif (ko'p o'qituvchi)
- SMS OTP / Google / Telegram auth (hozir stub)
- Krossvord/so'z-izlash: hozir soddalashtirilgan (to'liq interlocking grid emas)
