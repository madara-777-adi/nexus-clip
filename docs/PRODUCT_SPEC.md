# Nexus Clip — Product Specification

Version: 1.0
Status: LOCKED
Project: Nexus Clip

---

# 1. Vision

Nexus Clip is a private, cross-device clipboard workspace.

Its purpose is to let users instantly capture, organize, and retrieve temporary information across devices with as little friction as possible.

Nexus Clip is designed around speed, privacy, and simplicity.

---

# 2. Product Principles

Every decision made during development must follow these principles.

## Privacy by Default

User content is private.

Nothing becomes accessible to another device unless the user explicitly shares or reveals the Board Code.

---

## Zero Friction

A new user should be able to start using Nexus Clip immediately without creating an account.

---

## Temporary First

Nexus Clip behaves like a clipboard.

It is optimized for temporary information rather than permanent document management.

---

## Fast Over Fancy

Reliability and responsiveness always take priority over additional features.

---

## Everything is a Clip

Regardless of its type, every stored item is treated as a Clip.

Examples include:

- Text
- Code
- Markdown
- Images
- Files
- URLs

---

# 3. Core Concepts

## Board

A Board is an isolated workspace that contains Clips.

Guest users own one temporary Board.

Authenticated users may create multiple Boards.

Examples:

- Project Alpha
- Resume
- Linux Notes
- Interview Preparation

---

## Clip

A Clip is a single piece of stored content.

Each Clip belongs to exactly one Board.

Supported Clip Types:

- Text
- Markdown
- Code
- Image
- File
- URL

---

# 4. User Modes

## Guest Mode

A Guest Board is automatically created when a guest stores their first Clip.

Guest users are not required to create an account.

Features

- Single Board
- Drag & Drop
- Paste
- File Upload
- Search
- Pin Clips
- Cross-device continuation using Board Code

Retention

- Automatically deleted after 24 hours

Privacy

The Board Code remains hidden until the first Clip is created.

---

## Logged-in Mode

Authenticated users own an account containing multiple Boards.

Features

- Multiple Boards
- Permanent storage
- Configurable auto-cleanup
- Pinned Clips protected from cleanup
- Cross-device synchronization
- Board management

Retention

Permanent by default.

Optional automatic cleanup:

- 7 days
- 30 days
- 90 days
- Never

Pinned Clips are never automatically deleted.

---

# 5. User Journey

Guest

Open Website

↓

Paste or Drop Content

↓

Temporary Board Created

↓

Board Code Appears

↓

Continue Working

↓

(Optional) Open Another Device

↓

Enter Board Code

↓

Continue Using Same Board

---

Logged-in

Login

↓

Create or Select Board

↓

Store Clips

↓

Automatically Available Across Devices

---

# 6. V1 Features

## Boards

Guest

- Automatic Board creation
- Board Code generation

Authenticated

- Create Board
- Rename Board
- Delete Board
- Switch Board

---

## Clips

- Paste
- Drag & Drop
- Upload
- Copy
- Delete
- Pin
- Search

---

## Supported Files

- Images
- Documents
- PDFs
- Videos
- Audio
- Archives
- Source Code

---

## Search

Search supports

- Clip Title
- Clip Content
- File Name
- Tags

---

## Device Continuation

Guest

Board Code

Authenticated

Automatic synchronization

---

### URL Privacy

Nexus Clip must never expose internal resource identifiers in browser URLs.

Guest Board IDs, User Board IDs, Clip IDs, Workspace IDs, or any other internal identifiers must remain server-side.

Users interact with Boards through the application interface rather than URL navigation.

The only publicly accessible URL is an intentionally generated Share Link, which is outside the scope of V1.

### Private Navigation

Authenticated users navigate entirely through application state.

Browser URLs never expose Board identifiers, Clip identifiers, Workspace names, or other private resources.

Guest users use Board Codes solely for cross-device continuation.

# 7. Non-Goals

Nexus Clip is NOT

- Cloud Storage
- A Note Taking Application
- A Project Management Tool
- A Team Collaboration Platform
- A Document Editor

---

# 8. Out of Scope (V1)

The following ideas are intentionally excluded.

- AI Search
- Browser Extension
- Desktop Application
- Mobile Application
- Shared Boards
- Team Boards
- OCR
- Semantic Search
- CLI
- Version History
- AI Categorization
- End-to-End Encryption

These belong to future versions.

---

# 9. Success Criteria

V1 is complete when the following are fully working.

Guest Mode

✓ Temporary Board

✓ Board Code

✓ Cross-device continuation

✓ 24-hour cleanup

Authenticated Mode

✓ Multiple Boards

✓ Persistent storage

✓ Auto-cleanup

Core Features

✓ Clipboard

✓ Drag & Drop

✓ File Upload

✓ Search

✓ Pinning

✓ Stable deployment

No new features are added after this point.

Development moves to V1.1.
