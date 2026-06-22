# DarsPro — Frontend

Next.js 14 (App Router) + TypeScript + TailwindCSS + Zustand. To'liq spec:
loyiha ildizidagi `CLAUDE.md`.

## Ishga tushirish

Backend `localhost:8000` da ishlab turishi kerak (`../backend`).

```bash
cp .env.local.example .env.local   # API/WS manzillari
npm install
npm run dev                         # http://localhost:3000
```

`npm run build` — production build (type-check + lint bilan).
`npm run test` — Vitest (engine validatsiya parity + komponent render, 39 test).

## Docker

`output: "standalone"` bilan slim image:

```bash
docker build -t darspro-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=... darspro-frontend
```

## CI

`.github/workflows/ci.yml` — push/PR'da backend testlar + frontend test/build
avtomatik ishlaydi.

## Marshrutlar

| Route | Mazmun |
|-------|--------|
| `/` | Landing |
| `/login`, `/register` | Auth (email + parol) |
| `/dashboard` | Statistika + so'nggi o'yinlar |
| `/library` | Kutubxona — sinf/fan/mavzu filtri, o'ynash yoki sinf rejimi |
| `/builder` | O'yin yaratish (Quiz/Matching/Flashcard) |
| `/solo/[id]` | Yakka o'ynash (o'qituvchi) |
| `/sessions` | Sessiyalar — yaratish/qaytish |
| `/sessions/[code]` | **Host boshqaruv xonasi** (jonli, WebSocket) |
| `/play` | O'quvchi: kod kiritish |
| `/play/[join_code]` | **O'quvchi o'yin sahifasi** (jonli, WebSocket) |
| `/admin` | Staff: review navbati (approve/reject) — faqat `is_staff` |
| `/admin/users` | Staff: foydalanuvchilar + manual tarif berish |

## Tuzilma

| Yo'l | Mazmun |
|------|--------|
| `lib/api.ts` | axios instance + token interceptor + refresh |
| `lib/socket.ts` | **native WebSocket** client (Django Channels uchun — Socket.IO EMAS) |
| `lib/store.ts` | Zustand auth store |
| `lib/content.ts` | kontent API yordamchilari |
| `components/ui/` | shadcn uslubidagi primitivlar |
| `components/engines/{Quiz,Matching,Flashcard,Memory,SpinWheel,SortOrder,FillBlank,Crossword,WordSearch}/` | har biri `Play.tsx` + `Builder.tsx` + `index.ts` (9 engine) |
| `components/engines/registry.ts` | slug → engine moduli |
| `types/api.ts`, `types/engines.ts` | TypeScript interfacelar |

## Muhim eslatma — WebSocket protokoli

CLAUDE.md "Socket.IO client" deydi, lekin **backend Django Channels (xom
WebSocket)** ishlatadi. Socket.IO Channels'ga ulanmaydi, shuning uchun
`lib/socket.ts` brauzerning native `WebSocket` API'sini ishlatadi. Sinf rejimi
shu asosda ishlaydi.

## Hozircha qamralmagan (keyingi faza)

Google/Telegram/OTP auth, qolgan 6 engine, juft/jamoa rejim, to'lov —
keyingi fazada. (Solo o'yin natijasi `POST /api/sessions/solo` orqali
saqlanadi → dashboard statistikasi to'ladi.)
