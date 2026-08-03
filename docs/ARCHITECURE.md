# Nexus Clip - Architecture

Version: 1.0 
Status: LOCKED 
Depends On: PRODUCT_SPEC.md

---

# 1. Architecture Overview

Nexus Clip follows a layered architecture where each layer has a single responsibility.

The frontend communicates only with the backend.

The backend owns all business logic and coordinates data between persistent storage, temporary storage, and object storage.

```text
                    Browser

          React + TypeScript + Tailwind

                     │
                     │
             REST API / WebSockets
                     │
                     ▼
               FastAPI Backend

      ┌──────────────┼──────────────┐
      │              │              │
      ▼              ▼              ▼
 PostgreSQL      Redis (TTL)    Cloudflare R2
(User Data)    (Guest Boards)      (Files)
```

---

# 2. Technology Stack

| Layer | Technology | Reason |
|--------|------------|--------|
| Frontend | React | Existing expertise and mature ecosystem |
| Language | TypeScript | Type safety |
| Backend | FastAPI | High performance, async support, automatic API documentation |
| ORM | SQLAlchemy | Production-ready ORM |
| Validation | Pydantic | Request and response validation |
| Database | PostgreSQL | Relational data model for persistent user data |
| Guest Storage | Redis | Native TTL support for temporary guest boards |
| File Storage | Cloudflare R2 | Durable object storage |
| Realtime | WebSockets | Cross-device synchronization |
| Styling | Tailwind CSS | Fast and consistent UI development |

---

# 3. Project Structure

## Backend

```text
backend/

api/
    HTTP endpoints

services/
    Business logic

repositories/
    Database and cache access

models/
    Database models

schemas/
    Request / Response validation

storage/
    Cloudflare R2 integration

cache/
    Redis integration

jobs/
    Scheduled cleanup jobs

core/
    Configuration
```

---

## Frontend

```text
frontend/

pages/

components/

hooks/

services/

contexts/

types/

utils/
```

---

# 4. High Level System Flow

## Guest Clipboard

```text
Guest User

        │
        ▼

Paste / Upload

        │
        ▼

FastAPI

        │
        ▼

Redis

        │
        ▼

Response

        │
        ▼

UI Updates
```

---

## Logged-in Clipboard

```text
Authenticated User

          │
          ▼

Paste / Upload

          │
          ▼

FastAPI

          │
          ▼

PostgreSQL

          │
          ▼

Response

          │
          ▼

UI Updates
```

---

## File Upload

```text
Drop File

     │
     ▼

FastAPI

     │
     ▼

Cloudflare R2

     │
     ▼

Store Metadata

     │
     ▼

Redis / PostgreSQL

     │
     ▼

Response
```

---

## Guest → Logged-in Migration

```text
Guest Board

      │
      ▼

User Login

      │
      ▼

Read Guest Board

      │
      ▼

Create Permanent Board

      │
      ▼

Move Clips

      │
      ▼

Delete Guest Data

      │
      ▼

Continue Normally
```

---

# 5. Backend Architecture

Business logic never communicates directly with storage.

```text
HTTP Request

      │
      ▼

Controller

      │
      ▼

Service

      │
      ▼

Repository

      │
      ▼

Redis / PostgreSQL / R2
```

Responsibilities

- Controllers receive requests and return responses.
- Services contain business logic.
- Repositories communicate with storage.
- Storage layers never contain business logic.

---

# 6. Frontend Architecture

```text
Pages

   │
   ▼

Components

   │
   ▼

Hooks

   │
   ▼

Services

   │
   ▼

Backend
```

Responsibilities

- Pages compose screens.
- Components render UI.
- Hooks manage client-side logic.
- Services communicate with backend APIs.

---

# 7. Storage Architecture

## Guest Users

```text
Guest Board

      │
      ▼

Redis

      │

24 Hour TTL
```

Guest boards exist only in Redis and expire automatically.

---

## Logged-in Users

```text
User

   │
   ▼

PostgreSQL

   │

Permanent Storage
```

---

## Files

```text
Upload

   │
   ▼

Cloudflare R2

   │
   ▼

Metadata

   │
   ▼

Database
```

Only metadata is stored in Redis/PostgreSQL.

Uploaded files are stored in Cloudflare R2.

---

# 8. Data Lifecycle

## Guest

```text
Created

   │

Active

   │

24 Hour TTL

   │

Automatically Deleted
```

---

## Logged-in

```text
Created

   │

Updated

   │

Pinned?

 ┌─Yes───────────────┐
 │                   │
 │ Never Auto Delete │
 │                   │
 └──────No───────────┘
          │
          ▼

Retention Policy

          │
          ▼

Deleted
```

---

# 9. Security Architecture

Authentication

- JWT authentication for registered users.
- Guest users receive a temporary board session.

Authorization

- Every request is validated server-side.
- Users may only access their own boards.

Privacy

- No Board IDs are exposed in browser URLs.
- Board Codes are generated only after the first Clip exists.
- Guest boards remain private unless the Board Code is intentionally shared.

Storage

- Files are never stored on the application server.
- Uploaded files are stored in Cloudflare R2.

---

# 10. Engineering Constraints

The following rules are mandatory throughout the project.

1. Business logic must never directly communicate with Redis, PostgreSQL, or Cloudflare R2.

2. All storage operations must go through repositories.

3. Guest data must never be stored permanently.

4. Files must never be stored on the application server.

5. Frontend must never know how data is stored internally.

6. Every layer must have a single responsibility.

---

# 11. Extension Points

The architecture intentionally allows future improvements without major redesign.

## Redis

Can additionally become a cache layer for PostgreSQL.

---

## Search

Can evolve into AI-powered semantic search.

---

## Authentication

OAuth providers can be added.

---

## Storage

Cloudflare R2 can be replaced with any S3-compatible object storage.

---

## Client Applications

The backend is designed to support:

- Web
- Desktop
- Mobile
- Browser Extension
- CLI

without changing business logic.
