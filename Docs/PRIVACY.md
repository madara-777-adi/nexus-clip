# Nexus Clip - Privacy Policy

Version: 1.0
Status: ACTIVE

Last Updated: August 2026

---

# Privacy First

Nexus Clip is built around one principle:

**Your data belongs to you.**

We only store the information necessary to provide the clipboard service.

We do not sell user data.

We do not use clipboard content for advertising.

---

# Information We Store

## Guest Users

Temporary Boards

- Clips
- Uploaded Files
- Board Code
- Creation Time
- Expiration Time

Guest Boards exist only to provide temporary clipboard synchronization.

---

## Registered Users

Account Information

- Name
- Email Address
- Password (hashed)

Clipboard Data

- Boards
- Clips
- Uploaded Files
- Settings

---

# Uploaded Files

Uploaded files are stored separately from the application server using object storage.

Files remain private and are accessible only to their owner.

---

# Guest Board Retention

Guest Boards are temporary.

They are automatically deleted after **24 hours**.

This deletion includes:

- Board
- Clips
- Uploaded Files
- Metadata

Deleted Guest Boards cannot be recovered.

---

# Registered User Retention

Registered users control their own data.

By default:

- Boards remain until deleted.
- Clips remain until deleted.
- Files remain until deleted.

Users may optionally enable automatic cleanup.

Pinned Clips are never removed automatically.

---

# Authentication

Passwords are never stored in plain text.

Authentication is handled using secure JWT tokens.

Protected resources require authentication.

---

# Data Sharing

Nexus Clip does **not** share private clipboard content with other users.

Data is shared only when the user intentionally uses a sharing feature.

Public sharing is **not part of V1**.

---

# Cookies & Local Storage

Nexus Clip may use browser storage to:

- Maintain login sessions
- Maintain Guest Sessions
- Remember user preferences

No advertising or tracking cookies are used.

---

# Security

Reasonable security practices are followed, including:

- HTTPS
- Password Hashing
- JWT Authentication
- Server-side Authorization
- Private Navigation
- Input Validation

No security system is perfect, but protecting user privacy is a core design goal.

---

# User Rights

Registered users may:

- Delete Boards
- Delete Clips
- Delete Files
- Delete their Account

Deleting an account permanently removes associated user data.

Guest users may delete their temporary Board at any time before expiration.

---

# Third-Party Services

Nexus Clip may use trusted third-party providers including:

- Cloudflare R2 (Object Storage)
- PostgreSQL Database Provider
- Redis Provider
- Hosting Provider

These services are used solely to operate Nexus Clip.

---

# Changes

This Privacy Policy may be updated as Nexus Clip evolves.

Material changes will be reflected by updating the version and last updated date.

---

# Contact

For questions regarding privacy or security, please contact the project owner through the official GitHub repository or project website.
