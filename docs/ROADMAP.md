# Nexus Clip - Roadmap

Version: 1.0
Status: ACTIVE

---

# Vision

Nexus Clip will evolve in small, stable releases.

Every release must be production-ready before the next version begins.

Feature creep is not allowed.

---

# V1 (Current Goal)

## Core

- Guest Boards
- Logged-in Boards
- Multiple Boards
- Board Management

## Clips

- Text Clips
- Code Clips
- Markdown Clips
- Images
- Files
- URLs

## Clipboard

- Paste
- Drag & Drop
- Upload
- Copy
- Delete
- Pin

## Search

- Keyword Search
- Search by Content
- Search by Filename
- Search by Tags

## Storage

- Redis (Guest Boards)
- PostgreSQL (Authenticated Users)
- Cloudflare R2 (Files)

## Authentication

- JWT Authentication
- Guest Sessions
- Guest → User Promotion

## Privacy

- Private Navigation
- Hidden Board URLs for authenticated users
- Board Code for guest continuation
- Automatic Guest Board Expiration

## Deployment

- Frontend
- Backend
- Database
- Redis
- Object Storage

---

# V1.1

## AI Intent Search

Natural language search.

Examples

- the jwt middleware
- yesterday's screenshot
- interview notes
- login api response

Instead of exact keyword matching.

---

## Browser Extension

- Save current page
- Save selected text
- Save images
- Save links

---

## Desktop Application

Global clipboard access.

Quick search.

Quick copy.

---

## Mobile Application

Native Android application.

---

# V2

## Team Boards

Shared workspaces.

---

## Shared Boards

Invite users.

Permission management.

---

## Public Clip Sharing

Temporary public links.

Expiration settings.

---

## CLI

Push clips directly from terminal.

---

## VS Code Extension

Save code snippets directly.

Search clips from editor.

---

## Better Search

Advanced filters.

Saved searches.

Search history.

---

# V3

## AI Organization

Automatic tagging.

Automatic categorization.

Duplicate detection.

---

## AI Suggestions

Related clips.

Frequently used clips.

Context-aware recommendations.

---

## Semantic Memory

Vector search.

Embeddings.

Natural language retrieval.

---

## OCR

Extract text from images.

---

## Smart Collections

Automatically group similar clips.

---

# Future Ideas

Ideas are collected here before being evaluated.

They are NOT part of the active roadmap.

- Clipboard history synchronization
- End-to-End Encryption
- Offline Mode
- Team Analytics
- Organization Accounts
- API Tokens
- Third-party Integrations
- Plugin System

---

# Completed

None

---

# Development Rule

No feature may move into development unless:

- PRODUCT_SPEC.md is updated (if required)
- ARCHITECTURE.md supports it
- API.md is updated (if applicable)

If a feature does not satisfy these conditions, it remains in the Roadmap.
