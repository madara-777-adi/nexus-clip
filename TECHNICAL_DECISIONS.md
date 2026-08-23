# Technical Decisions

This document explains the *why* behind Nexus Clip's architecture — the
trade-offs considered and the reasoning for each major choice. For setup
instructions and feature list, see the [main README](../README.md).

---

## 1. Backend: FastAPI + async SQLAlchemy

**Choice:** FastAPI on Python 3.12, with SQLAlchemy 2.0's async ORM and
`psycopg` (v3, async driver) against PostgreSQL.

**Why:**
- Native `async`/`await` support end-to-end (routes → services → repositories
  → DB driver) means the app doesn't block on I/O — important since most
  requests are simple CRUD against Postgres/Redis, not CPU-bound work.
- Pydantic (already FastAPI's request/response layer) doubles as the
  validation layer for config (`pydantic-settings`) and DTOs (`schemas/`),
  so there's one validation library for the whole backend instead of three.
- Automatic OpenAPI docs at `/docs` for free, which matters more on a solo
  project with no separate API documentation effort.

**Trade-off accepted:** async SQLAlchemy has a steeper learning curve than
the sync ORM (session lifecycle, lazy-loading pitfalls), but it avoids
needing a separate task queue for what is otherwise simple request/response
work.

---

## 2. Layered structure: `api/ → services/ → repositories/ → models/`

**Choice:** Strict separation — routers only orchestrate, services hold
business logic, repositories hold query logic, models are plain ORM
definitions.

**Why:** Keeps route handlers thin and testable in isolation (e.g.
`ClipRepository.delete_expired_unpinned` can be unit tested without spinning
up FastAPI). It also means swapping a data source (e.g. moving guest
sessions from Redis to Postgres) only touches the repository/service layer,
not the API surface.

**Trade-off accepted:** more files and indirection than a flat
"routes call the DB directly" structure — a reasonable cost once the app has
auth, boards, clips, search, and guest flows all touching overlapping data.

---

## 3. Guest Mode: Redis, not Postgres

**Choice:** Guest board sessions live in Redis with a 24-hour TTL
(`app/cache/`, `app/services/guest_service.py`), not as rows in Postgres.

**Why:**
- Guest sessions are inherently short-lived and disposable — Redis TTL
  expiry gives automatic cleanup for free, with no cron/cleanup job needed
  for this specific case.
- Keeps the Postgres schema clean of throwaway/anonymous data; only
  registered users and their promoted boards ever hit the relational DB.
- The Board Code (`NEXUS-XXXX`) is only generated on the **first clip**, not
  session creation — this was a deliberate choice so an idle guest visit
  never allocates a persistent-looking identifier.

**Trade-off accepted:** if Redis is unavailable, guest mode is fully down
(there's no Postgres fallback for guest sessions) — acceptable since guest
mode is explicitly the "no commitment, ephemeral" tier of the product, and
registered-user flows don't depend on Redis being up (`cache/` degrades to
no-ops when `redis_enabled` is false or the client errors, rather than
raising — see `app/cache/redis_cache.py`).

---

## 4. Auth: JWT (HS256) + optional Google OAuth, no session store

**Choice:** Stateless `HS256`-signed JWTs (`app/auth/jwt.py`) for session
auth, with Google ID token verification (`app/auth/google.py`) as an
alternative login path. No server-side session table.

**Why:** Stateless tokens mean auth checks don't require a DB or Redis round
trip on every request — just signature verification. For Google login, the
ID token is verified against Google's public keys and specific claims
(`email_verified`, `iss`) are checked server-side rather than trusting
whatever the client sends, so a forged or replayed client-side payload can't
impersonate a user.

**Trade-off accepted:** HS256 (symmetric) means the same secret both signs
and verifies tokens — simpler than RS256's key-pair setup, but it does mean
the secret must never leak, since anyone holding it can mint valid tokens.
There's also no built-in token revocation (no session store to invalidate)
— acceptable for a project this size, but would need a denylist or a move
to short-lived tokens + refresh tokens if revocation becomes a requirement.

---

## 5. File storage: local disk today, R2 path left open

**Choice:** Uploaded files are currently written to local disk
(`/tmp/nexus_uploads` in `StorageService`) and served back via
`/static/uploads/{filename}` with a forced `Content-Disposition: attachment`
header — deliberately chosen over inline rendering.

**Why forced download instead of inline serving:** An uploaded `.svg` or
`.html` file, if served inline, can execute as a script in the browser under
the app's own origin (stored XSS). Forcing every upload to download as an
attachment — regardless of file type — closes that off as defense in depth,
on top of already disallowing `.svg`/`.html` extensions at upload time.

**Known limitation:** local disk storage is **ephemeral** on the current
Render deployment — the filesystem is wiped on every redeploy/restart, and
wouldn't be shared across multiple instances if the service scales
horizontally. This is a conscious, temporary trade-off: Cloudflare R2
(S3-compatible) integration is scaffolded for but not yet wired up (see the
comment in `storage_service.py`). Environment variables for R2 credentials
already have a placeholder in `.env.example` for when that migration
happens.

---

## 6. CORS: explicit allow-list via env var, not wildcard

**Choice:** `CORSMiddleware` origins come from a `CORS_ORIGINS` env var,
defaulting only to local dev ports (`5173`, `3000`) — production must set
it explicitly to the deployed frontend origin(s).

**Why:** `allow_origins=["*"]` isn't compatible with `allow_credentials=True`
(browsers reject that combination), and this app uses credentialed
requests. An explicit allow-list also means only known frontend origins can
call the API with cookies/auth headers, rather than any origin on the
internet.

**Trade-off accepted:** every new deployment origin (a Vercel preview URL,
a custom domain) has to be added to the env var manually — there's no
wildcard subdomain matching. If preview-URL testing becomes routine, the
next step would be switching to `allow_origin_regex` for a matched pattern
instead of exact strings.

---

## 7. Auto-cleanup as an explicit job, not TTL-based deletion

**Choice:** Clip retention (7/30/90 days/never) is enforced by an explicit
`run_auto_cleanup_job` that queries `UserSettings` per user and deletes
expired, **unpinned** clips — not a database-level TTL or cron-in-SQL
mechanism.

**Why:** Retention is per-user and configurable, and pinned clips must
always be exempt regardless of age — logic that's easiest to express and
test as an explicit query (`delete_expired_unpinned`) rather than encoding
per-row expiry at write time. Keeping it as a callable job function (rather
than baking it into a scheduler) also means it can be triggered by whatever
scheduling mechanism the deployment target supports (cron, Render cron job,
manual trigger) without changing the logic itself.

---

## 8. Frontend: Vite + React + TypeScript, no heavier framework

**Choice:** Plain Vite/React/TS SPA — no Next.js, no server-side rendering,
no state management library beyond React context (`BoardContext`).

**Why:** The app is entirely behind guest/auth flows with no public,
SEO-relevant pages, so SSR provides little benefit here. A single
`BoardContext` for board/clip state is sufficient at the current scope
(one board's worth of clips visible at a time) — reaching for Redux/Zustand
would add ceremony without a clear win yet.

**Trade-off accepted:** if the app grows multiple independent pieces of
global state (e.g. real-time collaboration, multi-board views open at once),
context alone will likely need to be split up or replaced — a deliberate
"revisit later" rather than a permanent decision.

---

## 9. Frontend/backend origin separation (Vercel + Render)

**Choice:** Frontend deployed to Vercel, backend deployed separately to
Render, talking over CORS rather than same-origin (e.g. via a reverse proxy
or monorepo rewrite rule).

**Why:** Keeps the two deployment lifecycles independent — frontend
redeploys don't require a backend redeploy and vice versa, and each platform
is used for what it's best at (Vercel for static/edge frontend hosting,
Render for a long-running Python service with Postgres/Redis).

**Trade-off accepted:** any URL the frontend builds for backend resources
(API calls, static file links) must be built against the backend's origin
explicitly (`VITE_API_BASE_URL` / a derived `API_ORIGIN`), never against
`window.location.origin` — a class of bug this project hit in practice
(file download links silently pointed at the frontend's own domain) before
being caught and fixed.

---

## Known limitations / deliberately deferred

- **File storage is not yet persistent** across deploys (see §5) — R2
  migration is the next infrastructure step.
- **No token revocation** for JWTs (see §4) — acceptable at current scale.
- **No horizontal scaling story for guest sessions** — Redis is a single
  logical store; fine at current traffic, would need clustering/replication
  before scaling out meaningfully.
- **CORS origins are manually maintained**, not regex-matched — fine while
  there are only 1–2 known frontend origins.