# Nexus Clip - API Specification

Version: 1.0
Status: LOCKED
Depends On:
- PRODUCT_SPEC.md
- ARCHITECTURE.md

---

# API Principles

## Base URL

/api/v1

---

## Response Format

Success

```json
{
  "success": true,
  "message": "Operation successful.",
  "data": {}
}
```

Error

```json
{
  "success": false,
  "message": "Error message",
  "errors": []
}
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Resource Created |
| 204 | Resource Deleted |
| 400 | Validation Error |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 413 | File Too Large |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

---

# Authentication

---

## POST /auth/register

Purpose

Create a new account.

Authentication

None

Request

```json
{
  "name": "",
  "email": "",
  "password": ""
}
```

---

## POST /auth/login

Purpose

Authenticate a user.

Authentication

None

Request

```json
{
  "email": "",
  "password": ""
}
```

Returns

- Access Token
- User Profile

---

## POST /auth/logout

Purpose

Invalidate current session.

Authentication

Required

---

## GET /auth/me

Purpose

Return currently authenticated user.

Authentication

Required

---

# Guest

---

## POST /guest/board

Purpose

Create a temporary Guest Board.

Authentication

None

Returns

- Guest Session
- Temporary Board

---

## POST /guest/continue

Purpose

Continue an existing Guest Board using Board Code.

Authentication

None

Request

```json
{
  "boardCode": ""
}
```

---

# Boards

---

## GET /boards

Purpose

Return all Boards belonging to the authenticated user.

Authentication

Required

---

## POST /boards

Purpose

Create a new Board.

Authentication

Required

Request

```json
{
  "name": ""
}
```

---

## PATCH /boards/{boardId}

Purpose

Rename Board.

Authentication

Required

---

## DELETE /boards/{boardId}

Purpose

Delete Board.

Authentication

Required

---

# Clips

---

## GET /boards/{boardId}/clips

Purpose

Return all Clips inside a Board.

Authentication

Required

---

## POST /boards/{boardId}/clips

Purpose

Create a new Clip.

Authentication

Guest / Logged-in

Request

```json
{
  "type": "text",
  "content": "...",
  "title": ""
}
```

---

## PATCH /clips/{clipId}

Purpose

Update Clip.

Authentication

Guest / Logged-in

---

## DELETE /clips/{clipId}

Purpose

Delete Clip.

Authentication

Guest / Logged-in

---

## PATCH /clips/{clipId}/pin

Purpose

Toggle Pin.

Authentication

Guest / Logged-in

---

# Uploads

---

## POST /upload

Purpose

Upload File.

Authentication

Guest / Logged-in

Supported

- Images
- PDFs
- Documents
- Videos
- Audio
- Archives
- Source Code

Returns

File Metadata

---

## DELETE /upload/{fileId}

Purpose

Delete uploaded file.

Authentication

Owner only

---

# Search

---

## GET /search

Purpose

Search Clips.

Authentication

Guest / Logged-in

Query Parameters

```
?q=
&type=
&board=
```

Searches

- Clip Title
- Clip Content
- File Name
- Tags

---

# Settings

---

## GET /settings

Purpose

Return User Settings.

Authentication

Required

---

## PATCH /settings

Purpose

Update User Settings.

Authentication

Required

Supported

- Auto Cleanup
- Theme
- Default Board

---

# Guest Promotion

---

## POST /guest/promote

Purpose

Convert Guest Board into a permanent User Board after login.

Authentication

Required

Flow

Guest Board

↓

Redis

↓

Create User Board

↓

Move Clips

↓

Delete Guest Board

↓

Return User Board

---

# Navigation Rules

Authenticated Users

- Browser URL never exposes Board IDs.
- Browser URL never exposes Clip IDs.
- Browser URL never exposes Workspace names.

Navigation is handled entirely through application state.

---

Guest Users

Guest Boards are identified using Board Codes only.

Board Codes become visible only after the first Clip has been created.

---

# Authorization Rules

Users may access only their own Boards.

Guest users may access only the Guest Board associated with their active Guest Session.

Board Codes are required only for cross-device continuation.

---

# Rate Limits

Guest

- Board Creation
- Upload
- Search

Authenticated

- Upload
- Search

Exact limits are implementation details and may change without affecting the API contract.

---

# Out of Scope

The following endpoints are intentionally excluded from V1.

- AI Search
- Shared Boards
- Team Workspaces
- Browser Extension APIs
- CLI APIs
- OAuth Authentication
- Public Share Links
