# AdamDesk

AdamDesk is a deployable multi-tenant gym SaaS platform inspired by gymdesk.com workflows.

## Included feature workflows

- Multi-tenant organizations
- Owner authentication (register/login with JWT)
- Member CRM management
- Class scheduling
- Booking API
- Lead pipeline
- Billing invoice model + KPI dashboard endpoint
- Responsive operations dashboard page

## Run locally (Docker)

```bash
docker compose up --build
```

Then open http://localhost:8000.

## Environment variables

Copy `.env.example` to `.env` and set production values:

```bash
cp .env.example .env
```

Required for production:

- `SECRET_KEY`: long random string used to sign JWT tokens.
- `DATABASE_URL`: PostgreSQL connection string (required for persistent production data).

Optional:

- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT expiry window (default: `60`).

> Note: if `DATABASE_URL` is not set, AdamDesk falls back to SQLite at `/tmp/adamdesk.db` for serverless compatibility. This is ephemeral and will reset between cold starts, so use Postgres in production.

## Production deployment guide

### Option A: Single VM with Docker Compose

1. Install Docker and Docker Compose on your VM.
2. Clone this repository on the server.
3. Create `.env` from `.env.example` and set secure values.
4. Start the stack:

```bash
docker compose up -d --build
```

5. Put Nginx/Caddy in front of port `8000` and enable HTTPS (Let's Encrypt).

### Option B: Container platform (Render/Fly.io/Railway/ECS)

1. Use the included `Dockerfile` as the web service build target.
2. Provision a managed PostgreSQL instance.
3. Set environment variables in the platform settings:
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `ACCESS_TOKEN_EXPIRE_MINUTES` (optional)
4. Run with:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

(Platforms typically inject `$PORT` automatically.)

### Option C: Vercel (fix for 404)

This repository now includes `vercel.json` and `api/index.py` so Vercel routes all paths to the FastAPI ASGI app instead of returning 404.

1. In Vercel project settings, set:
   - Framework preset: **Other**
   - Root Directory: repository root
2. Add environment variables:
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `ACCESS_TOKEN_EXPIRE_MINUTES` (optional)
3. Deploy (or redeploy) from Vercel.

If you are using Vercel Postgres, copy its connection string into `DATABASE_URL`.

## Deploy checklist

- [ ] `SECRET_KEY` rotated from defaults.
- [ ] PostgreSQL used instead of SQLite.
- [ ] TLS configured at ingress/proxy.
- [ ] Container auto-restart enabled.
- [ ] Logs and uptime checks enabled.
- [ ] Backup policy configured for Postgres.

## API quickstart

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/dashboard/{organization_id}`
- `POST /api/organizations/{organization_id}/members`
- `GET /api/organizations/{organization_id}/members`
- `POST /api/organizations/{organization_id}/classes`
- `GET /api/organizations/{organization_id}/classes`
- `POST /api/organizations/{organization_id}/leads`
- `GET /api/organizations/{organization_id}/leads`
- `POST /api/organizations/{organization_id}/bookings?member_id=1&class_session_id=1`

## Scalability notes

- App is containerized and stateless at runtime.
- Uses PostgreSQL for horizontal scale readiness.
- Can be deployed to ECS/Kubernetes/Fly.io/Render.
- Database pool pre-ping enabled and service layer split for maintainability.
