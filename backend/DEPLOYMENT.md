# Nexus Clip Backend Deployment Guide

This document provides a reference for deploying the Nexus Clip FastAPI backend manually to production environments.

## Required Environment Variables

The following environment variables MUST be provided to the production environment:

| Variable | Purpose | Example / Format |
|---|---|---|
| `DATABASE_URL` | PostgreSQL async connection string. The app will fail to start if this is missing. | `postgresql+psycopg://user:password@host:port/dbname` |
| `REDIS_URL` | Redis connection URL. The app will fail to start if this is missing. TLS is supported via the `rediss://` scheme. | `rediss://default:password@host:port` |
| `JWT_SECRET_KEY` | Secret used to sign JWT access tokens. Must be a secure, random string. | `YOUR_SECURE_RANDOM_STRING` |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID required for social login. | `your-id.apps.googleusercontent.com` |
| `CORS_ORIGINS` | A JSON-formatted list of allowed frontend origins. By default it only allows localhost; production MUST set this. | `["https://nexusclip.app", "https://www.nexusclip.app"]` |
| `PORT` | (Optional but recommended) The port the server should bind to. PaaS providers like Render inject this automatically. | `8000` |
| `ENVIRONMENT` | Should be set to `production` to toggle production-specific behavior. | `production` |

## Production Start Command

To start the server in production, use the following command. The application relies on `uvicorn` and will automatically pick up the `PORT` environment variable if injected by your platform.

```bash
uv run uvicorn app.main:app --host 0.0.0.0
```

## Running Database Migrations

Alembic is configured to read the `DATABASE_URL` directly from the environment. To apply migrations against the production database, run:

```bash
uv run alembic upgrade head
```
*(Make sure `DATABASE_URL` is exported in the environment where you run this command.)*

## Known Limitations

> [!WARNING]
> **Ephemeral Upload Storage**
> The application currently writes file uploads to the `/tmp/nexus_uploads` directory. On most PaaS providers (e.g., Render, Heroku), this storage is ephemeral. Uploaded files will not persist across restarts, redeploys, or scale-outs.
