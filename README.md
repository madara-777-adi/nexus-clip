# Nexus Clip 📎

> A cross-device, privacy-first clipboard manager with guest sessions, multi-board organization, and rich clip types.

---

## ✨ Features

- **6 Clip Types** — `text`, `code`, `markdown`, `image`, `file`, `url` with smart auto-detection
- **Guest Mode** — No account needed. Paste a clip, get a `NEXUS-XXXX` Board Code to continue from any device. Sessions expire after 24 hours.
- **Multi-Board Workspaces** — Organize clips into named boards per project or context
- **Pinned Clips** — Pin important clips to exempt them from auto-cleanup
- **Auto-Cleanup** — Configurable retention (7 / 30 / 90 days or never) for unpinned clips
- **File Uploads** — Upload images and files, stored locally or on Cloudflare R2
- **Full-text Search** — Search clips by title, content, filename, or tags
- **Guest → Account Promotion** — Save your guest board into a permanent account at any time
- **JWT Auth** — Secure email/password login with `HS256` JWT access tokens

---

## 🏗️ Architecture

```
nexus-clip/
├── backend/          # FastAPI + SQLAlchemy + Redis
│   ├── app/
│   │   ├── api/      # HTTP routers
│   │   ├── auth/     # JWT + Google OAuth
│   │   ├── cache/    # Redis client
│   │   ├── core/     # Config, exceptions, logging
│   │   ├── db/       # SQLAlchemy async engine + sessions
│   │   ├── jobs/     # Background cleanup tasks
│   │   ├── models/   # ORM models
│   │   ├── repositories/
│   │   ├── schemas/  # Pydantic request/response models
│   │   └── services/ # Business logic
│   └── tests/
└── frontend/         # Vite + React + TypeScript
    └── src/
        ├── components/
        ├── contexts/
        ├── services/
        └── types/
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+, `uv` package manager
- Node.js 20+, npm
- PostgreSQL 15+
- Redis 7+

### Backend Setup

```bash
cd backend
cp .env.example .env        # Edit with your real DB/Redis/JWT values
uv sync                     # Install dependencies
uv run uvicorn app.main:app --port 8000 --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev                 # Starts on http://localhost:5173
```

### Running Tests

```bash
cd backend
uv run pytest               # 7 tests, all async, in-memory SQLite + mock Redis
```

---

## ⚙️ Environment Variables

Copy [`backend/.env.example`](backend/.env.example) to `backend/.env` and fill in:

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL async DSN (`postgresql+psycopg://...`) |
| `JWT_SECRET_KEY` | ✅ | Random 64-byte secret. Generate: `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `REDIS_URL` | ✅ | Redis connection URL (`redis://localhost:6379/0`) |
| `GOOGLE_CLIENT_ID` | optional | For Google OAuth login |
| `R2_*` | optional | Cloudflare R2 file storage. Leave blank for local storage |

---

## 📡 API Overview

Base URL: `http://localhost:8000/api/v1`

| Method | Route | Description |
|---|---|---|
| `POST` | `/auth/register` | Register user |
| `POST` | `/auth/login` | Login |
| `GET` | `/auth/me` | Get current user |
| `POST` | `/guest/board` | Create/get guest board |
| `POST` | `/guest/board/clips` | Add clip to guest board |
| `POST` | `/guest/continue` | Continue on new device with Board Code |
| `POST` | `/guest/promote` | Promote guest board to user account |
| `GET` | `/boards` | List user boards |
| `POST` | `/boards` | Create board |
| `GET` | `/boards/{id}/clips` | List clips in board |
| `POST` | `/boards/{id}/clips` | Create clip |
| `PATCH` | `/clips/{id}` | Update clip |
| `PATCH` | `/clips/{id}/pin` | Toggle pin |
| `DELETE` | `/clips/{id}` | Delete clip |
| `POST` | `/upload` | Upload file |
| `GET` | `/search` | Search clips |
| `GET` | `/settings` | Get user settings |
| `PATCH` | `/settings` | Update settings |

---

## 🔒 Privacy

- Guest Board Codes are only generated and shown **after the first clip is created** (not before)
- Guest sessions expire after **24 hours** (Redis TTL)
- Pinned clips are **never deleted** by auto-cleanup jobs
- The `.env` file is in `.gitignore` — no secrets are committed

---

## 🛣️ Roadmap

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the V2+ feature plan.
